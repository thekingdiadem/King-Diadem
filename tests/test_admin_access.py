"""สิทธิ์ผู้ดูแล · คนติดป้ายอย่างเดียว · บันทึกว่าใครทำอะไร · หน้าเช็กความปลอดภัย

ช่องโหว่ที่ปิด: สมัครด้วยรหัสผ่านใช้อีเมลของใครก็ได้ (ไม่ได้ยืนยันอีเมล) และสิทธิ์ผู้ดูแลเดิมเทียบแค่ตัวอักษร
→ อีเมลใน ADMIN_EMAILS ที่เจ้าของยังไม่เคยสมัคร ใครสมัครก่อนได้สิทธิ์ผู้ดูแลไปทันที
(เห็นรายได้ · รายงาน · ประโยคที่ผู้ใช้แนบมา) · ตอนนี้ต้องเคยเข้าด้วย Google ด้วยอีเมลนั้นก่อน
"""
import re
import uuid

import pytest

from core import admin_access
from tests.conftest import verify_email


def _mail(tag):
    return f"{tag}-{uuid.uuid4().hex[:8]}@test.co"


def _signup(client, email):
    r = client.post("/register", json={"email": email, "password": "secret12"})
    assert r.status_code == 200, r.text


ADMIN_PATHS = ("/api/admin/metrics", "/api/admin/reports", "/api/admin/security", "/admin/security",
               "/api/admin/label-queue", "/admin/label")


def test_squatting_an_admin_email_with_a_password_gives_nothing(client, app_module, monkeypatch):
    victim = _mail("owner")                       # อยู่ใน ADMIN_EMAILS แต่เจ้าของยังไม่เคยสมัคร
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {victim})
    _signup(client, victim)                       # คนอื่นสมัครด้วยอีเมลนี้ก่อน
    for path in ADMIN_PATHS:
        assert client.get(path).status_code == 404, path
    assert client.get("/me").json()["admin"] is False


def test_owner_who_proved_the_email_gets_in(client, app_module, monkeypatch):
    owner = _mail("owner")
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {owner})
    verify_email(owner)
    _signup(client, owner)
    for path in ADMIN_PATHS:
        assert client.get(path).status_code == 200, path


def test_labeler_can_label_but_sees_nothing_else(client, app_module, monkeypatch):
    lab = _mail("helper")
    monkeypatch.setattr(app_module, "_LABELER_EMAILS", {lab})
    verify_email(lab)
    _signup(client, lab)
    assert client.get("/admin/label").status_code == 200
    assert client.get("/api/admin/label-queue").status_code == 200
    for path in ("/api/admin/metrics", "/api/admin/reports", "/api/admin/security", "/admin/security"):
        assert client.get(path).status_code == 404, path


def test_unverified_labeler_gets_nothing(client, app_module, monkeypatch):
    lab = _mail("helper")
    monkeypatch.setattr(app_module, "_LABELER_EMAILS", {lab})
    _signup(client, lab)
    assert client.get("/admin/label").status_code == 404


def test_label_and_export_are_logged_without_the_users_sentence(client, app_module, monkeypatch):
    owner = _mail("owner")
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {owner})
    verify_email(owner)
    _signup(client, owner)
    secret = f"ประโยคลับของผู้ใช้ {uuid.uuid4().hex[:6]}"
    client.post("/api/report-answer", json={"reason": "missed", "answer": "x", "question": secret, "include_question": True})
    it = next(i for i in client.get("/api/admin/label-queue?limit=200").json()["items"] if i["question"] == secret)
    assert client.post("/api/admin/label", json={"id": it["id"], "label": "none"}).json()["ok"]
    client.get("/api/admin/label-export")
    acts = client.get("/api/admin/security").json()["actions"]
    kinds = [a["action"] for a in acts[:4]]
    assert "label" in kinds and "export" in kinds
    assert all(secret not in a["detail"] for a in acts)
    assert all("•••" in a["who"] for a in acts)                        # อีเมลไม่แสดงเต็ม


def test_security_status_flags_missing_2fa_and_unproven_emails():
    st = admin_access.security_status(
        twofa_on=lambda e: e.startswith("safe"), user_exists=lambda e: not e.startswith("new"),
        admin_emails={"safe@x.co", "phone@x.co", "new@x.co"}, labeler_emails={"helper@x.co", "safe@x.co"})
    by = {p["email"]: p for p in st["people"]}
    assert st["admins"] == 3 and st["labelers"] == 1 and not st["ok"] and st["weak"] == 3
    assert by[admin_access.mask("safe@x.co")]["todo"] == ""
    assert "2FA" in by[admin_access.mask("phone@x.co")]["todo"]
    assert "Google" in by[admin_access.mask("new@x.co")]["todo"]


def test_mask_and_record_validation():
    assert admin_access.mask("boss@gmail.com") == "bo•••@gmail.com" and admin_access.mask("a@b.co") == "a•••@b.co"
    assert admin_access.record("x@y.co", "admin", "delete_everything") is False
    assert admin_access.record("x@y.co", "god", "label") is False


def test_old_actions_are_pruned():
    assert admin_access.record("old@x.co", "admin", "label", "#1")
    assert admin_access.prune(now=10**12) >= 1


@pytest.mark.parametrize("page", ["static/admin_security.html", "static/admin_label.html"])
def test_admin_pages_are_csp_safe_and_not_indexed(page):
    html = open(page, encoding="utf-8").read()
    assert not re.search(r"<[^>]+\son[a-z]+=", html)
    assert 'name="robots" content="noindex' in html
