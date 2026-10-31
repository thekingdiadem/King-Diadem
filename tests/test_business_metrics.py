"""ตัวเลขธุรกิจสำหรับเจ้าของ — เจ้าของถามว่า "งานเริ่มเข้าใกล้แอปที่ทำรายได้หรือยัง" แต่ระบบไม่มีตัวเลขอะไรให้ตอบ

นับ: คนเข้าเว็บ → คนที่ลองคุย → ใช้ฟรีหมดวัน → กดไปหน้าจ่าย → จ่ายจริง (+ สมัครใหม่ · รายได้)
ไม่เก็บข้อความ อีเมล หรือ IP ตรงๆ · เห็นได้เฉพาะอีเมลใน ADMIN_EMAILS"""
import sqlite3
import uuid

import pytest


@pytest.fixture
def owner(client, app_module, monkeypatch):
    email = f"owner-{uuid.uuid4().hex[:8]}@test.co"
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {email})
    client.post("/register", json={"email": email, "password": "secret12"})
    return client


def _report(c):
    r = c.get("/api/admin/metrics?days=1")
    assert r.status_code == 200, r.text
    return r.json()["total"]


def test_only_the_owner_sees_the_numbers(client, user):
    assert client.get("/api/admin/metrics").status_code == 404      # ล็อกอินแล้วแต่ไม่ใช่เจ้าของ
    assert client.get("/me").json()["admin"] is False


def test_owner_flag_and_funnel_counts(owner, app_module):
    assert owner.get("/me").json()["admin"] is True
    before = _report(owner)
    owner.get("/")
    owner.get("/")                                   # คนเดิมเข้าซ้ำ = คนเข้าเว็บ 1 คน แต่ 2 ครั้ง
    after = _report(owner)
    assert after["visit"] - before["visit"] == 2
    assert after["u:visitor"] - before["u:visitor"] == 1


def test_paywall_counts_people_who_used_up_free(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {"boss-paywall@test.co"})
    boss = type(client)(app_module.app, base_url="https://testserver", headers={"cf-connecting-ip": "10.250.1.1"})
    boss.post("/register", json={"email": "boss-paywall@test.co", "password": "secret12"})
    before = _report(boss)
    for _ in range(app_module.FREE_DAILY_RUNS + 2):              # ไม่ล็อกอิน · ใช้ฟรีหมดแล้วชนเพดาน
        client.post("/run", json={"input": "นอนไม่หลับ"})
    after = _report(boss)
    assert after["u:chatter"] - before["u:chatter"] == 1
    assert after["chat"] - before["chat"] == app_module.FREE_DAILY_RUNS
    assert after["u:paywalled"] - before["u:paywalled"] == 1      # ชนสองครั้ง = คนเดียว


def test_purchase_counts_once_even_if_stripe_resends(owner, app_module):
    before = _report(owner)
    app_module._metric("purchase", "cs_test_same", 199)
    app_module._metric("purchase", "cs_test_same", 199)           # Stripe ส่ง event ซ้ำ
    after = _report(owner)
    assert after["u:purchase"] - before["u:purchase"] == 1
    assert after["baht"] - before["baht"] == 199


def test_no_raw_emails_or_ips_are_stored(owner, app_module):
    owner.get("/")
    from DATABASE.db import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    keys = [r[0] for r in conn.execute("SELECT key FROM metric_keys")]
    conn.close()
    assert keys and not any("@" in k or "." in k for k in keys)


def test_metrics_never_break_the_chat(client, app_module, monkeypatch):
    import DATABASE.db as db
    monkeypatch.setattr(db, "metric_inc", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("disk full")))
    assert client.post("/run", json={"input": "สวัสดี"}).status_code == 200
