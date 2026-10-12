"""ประวัติการปรึกษา: เก็บไว้ในบัญชี (ไอดี) + ส่งออกไปอีเมลของบัญชีได้ — พี่เลือกแบบนี้
· คนที่ไม่ได้เข้าสู่ระบบ: ไม่เก็บข้อความ (เดิมเก็บเต็มไว้ใต้ "anonymous" ที่ไม่มีใครเรียกดูหรือลบได้)
· ส่งออกได้เฉพาะของตัวเอง · ส่งได้เฉพาะอีเมลของบัญชีนั้น (ไม่รับปลายทางจากผู้ใช้)"""
import uuid

import pytest

import core.history_export as hx
from DATABASE import db


def _sent(monkeypatch):
    box = []
    monkeypatch.setenv("SMTP_HOST", "smtp.test"); monkeypatch.setenv("SMTP_USER", "bot@test"); monkeypatch.setenv("SMTP_PASS", "x")
    monkeypatch.setattr(hx, "send_history_email", lambda to, text, timeout=20.0: box.append((to, text)))
    return box


def test_anonymous_text_is_not_stored():
    before = db.count_decision_history("anonymous")
    db.log_decision(user_id="anonymous", input="เรื่องส่วนตัวมาก", output="ตอบ", route="general")
    db.log_decision(user_id="", input="เรื่องส่วนตัวมาก", output="ตอบ", route="general")
    conn = db.get_conn()
    try:
        n = conn.execute("SELECT COUNT(*) FROM decision_log WHERE input=?", ("เรื่องส่วนตัวมาก",)).fetchone()[0]
    finally:
        conn.close()
    assert n == 0 and before == 0


def test_signed_in_history_is_kept_in_the_account(user):
    user.post("/run", json={"input": "วันนี้อากาศดี"})
    info = user.get("/api/history").json()
    assert info["count"] == 1 and info["email"] == user.email


def test_export_download_is_only_mine(user, client):
    user.post("/run", json={"input": "ร้านขายได้เดือนละ 80,000 ต้นทุน 65,000"})
    r = user.get("/api/history/export")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")
    assert "attachment;" in r.headers["content-disposition"] and r.headers["cache-control"] == "no-store"
    assert user.email in r.text and "ร้านขายได้เดือนละ 80,000" in r.text and "คำตอบ:" in r.text
    other = client.__class__(client.app, base_url="https://testserver", headers={"cf-connecting-ip": "10.9.9.9"})
    other.post("/register", json={"email": f"o{uuid.uuid4().hex[:8]}@test.co", "password": "secret12"})
    assert "ร้านขายได้เดือนละ 80,000" not in other.get("/api/history/export").text


def test_needs_sign_in(client):
    for m, path in (("get", "/api/history"), ("get", "/api/history/export"), ("post", "/api/history/email")):
        assert getattr(client, m)(path).status_code == 401


def test_email_goes_only_to_the_account_and_is_throttled(user, monkeypatch):
    box = _sent(monkeypatch)
    user.post("/run", json={"input": "วันนี้อากาศดี"})
    r = user.post("/api/history/email", json={"to": "attacker@evil.test"})   # ปลายทางจากผู้ใช้ไม่มีผล
    assert r.status_code == 200 and r.json()["sent_to"] == user.email
    assert box and box[0][0] == user.email and "วันนี้อากาศดี" in box[0][1]
    assert user.post("/api/history/email").status_code == 429                 # ครั้งต่อไปต้องรอ 10 นาที


def test_email_off_until_smtp_is_set_and_download_still_works(user, monkeypatch):
    for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS"):
        monkeypatch.delenv(k, raising=False)
    user.post("/run", json={"input": "วันนี้อากาศดี"})
    assert user.get("/api/history").json()["email_ready"] is False
    r = user.post("/api/history/email")
    assert r.status_code == 503 and r.json()["download"] == "/api/history/export"


def test_failed_send_does_not_use_up_the_cooldown(user, monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test"); monkeypatch.setenv("SMTP_USER", "bot@test"); monkeypatch.setenv("SMTP_PASS", "x")
    def boom(*a, **k):
        raise OSError("smtp down")
    monkeypatch.setattr(hx, "send_history_email", boom)
    user.post("/run", json={"input": "วันนี้อากาศดี"})
    assert user.post("/api/history/email").status_code == 502
    box = _sent(monkeypatch)
    assert user.post("/api/history/email").status_code == 200 and box


def test_empty_history_has_nothing_to_send(user, monkeypatch):
    _sent(monkeypatch)
    assert user.post("/api/history/email").status_code == 404


def test_format_is_readable_thai_time():
    text = hx.format_history([{"input": "สวัสดี", "response": "สวัสดีค่ะ", "route": "risk", "persona": "LYLA",
                               "created_at": "2026-10-12 03:00:00"}], "a@b.co")
    assert "12/10/2026 10:00" in text and "เส้นทาง ความเสี่ยง" in text and "บัญชี: a@b.co" in text


def test_smtp_send_uses_tls_and_attaches_the_file(monkeypatch):
    calls = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None): calls["conn"] = (host, port)
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def starttls(self, context=None): calls["tls"] = True
        def login(self, u, p): calls["login"] = u
        def send_message(self, msg):
            calls["to"] = msg["To"]
            calls["files"] = [p.get_filename() for p in msg.iter_attachments()]

    monkeypatch.setenv("SMTP_HOST", "smtp.test"); monkeypatch.setenv("SMTP_USER", "bot@test"); monkeypatch.setenv("SMTP_PASS", "x")
    monkeypatch.setattr(hx.smtplib, "SMTP", FakeSMTP)
    hx.send_history_email("me@test.co", "hello")
    assert calls["conn"] == ("smtp.test", 587) and calls["tls"] and calls["to"] == "me@test.co"
    assert calls["files"][0].startswith("king-diadem-history-") and calls["files"][0].endswith(".txt")


def test_old_unowned_rows_are_purged_and_owned_rows_kept(user):
    """พี่ให้ล้างข้อความเก่าที่ไม่มีเจ้าของ (เดิมเก็บไว้ใต้ anonymous) — ประวัติของคนที่มีบัญชีต้องอยู่ครบ"""
    user.post("/run", json={"input": "วันนี้อากาศดี"})
    conn = db.get_conn()
    try:
        for e in ("anonymous", "ANONYMOUS ", "guest", "system", "", None, "not-an-email"):
            conn.execute("INSERT INTO decision_log (user_email,input,route,persona,response) VALUES (?,?,?,?,?)",
                         (e, "ข้อความเก่าไม่มีเจ้าของ", "general", "LYLA", "ตอบ"))
        conn.commit()
    finally:
        conn.close()
    assert db.purge_unowned_history() == 7
    assert db.purge_unowned_history() == 0                       # รันซ้ำไม่มีอะไรให้ลบ
    assert user.get("/api/history").json()["count"] == 1
    conn = db.get_conn()
    try:
        assert conn.execute("SELECT COUNT(*) FROM decision_log WHERE input=?", ("ข้อความเก่าไม่มีเจ้าของ",)).fetchone()[0] == 0
    finally:
        conn.close()


def test_purge_runs_when_the_server_starts():
    import inspect
    assert "purge_unowned_history(conn)" in inspect.getsource(db.init_db)
