"""ลบบัญชีด้วยตัวเอง — PDPA สิทธิ์ขอลบ · Play Store ต้องมีในแอป
เดิมไม่มีทางลบเองเลย ต้องส่งอีเมลขอ (นโยบายบอกไว้แต่ทำในเว็บไม่ได้)"""
from core import totp
from DATABASE.db import get_conn


def _rows(email):
    c = get_conn()
    try:
        return {t: c.execute(f"SELECT COUNT(*) FROM {t} WHERE lower({col}) = ?", (email,)).fetchone()[0]
                for t, col in (("users", "email"), ("user_passwords", "user_email"), ("decision_log", "user_email"))}
    finally:
        c.close()


def test_wrong_confirmation_is_refused(user):
    r = user.post("/api/account/delete", json={"confirm": "someone@else.co"})
    assert r.status_code == 400 and _rows(user.email)["users"] == 1


def test_guest_cannot_delete(client):
    assert client.post("/api/account/delete", json={"confirm": "x@y.co"}).status_code == 401


def test_delete_removes_account_and_signs_out(user, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    user.post("/run", json={"input": "ควรเปลี่ยนงานดีไหม"})          # ให้มีประวัติแชทจริง
    email = user.email
    r = user.post("/api/account/delete", json={"confirm": email.upper()})
    assert r.status_code == 200 and r.json()["deleted"] is True
    assert _rows(email) == {"users": 0, "user_passwords": 0, "decision_log": 0}
    assert user.get("/me").json().get("logged_in") is False
    assert user.post("/login", json={"email": email, "password": "secret12"}).status_code != 200


def test_old_cookie_cannot_come_back_after_delete(client):
    import uuid
    email = f"del-{uuid.uuid4().hex[:8]}@test.co"
    client.post("/register", json={"email": email, "password": "secret12"})
    stolen = client.cookies.get("kd_email")
    assert client.post("/api/account/delete", json={"confirm": email}).status_code == 200
    client.cookies.set("kd_email", stolen)
    assert client.get("/me").json().get("logged_in") is False


def test_two_factor_must_confirm(user):
    s = user.post("/api/2fa/setup").json()
    user.post("/api/2fa/enable", json={"code": totp.code_at(s["secret"], totp.current_step())})
    r = user.post("/api/account/delete", json={"confirm": user.email})
    assert r.status_code == 400 and r.json()["need_code"] is True and _rows(user.email)["users"] == 1
    r = user.post("/api/account/delete", json={"confirm": user.email, "code": totp.code_at(s["secret"], totp.current_step() + 1)})
    assert r.status_code == 200 and _rows(user.email)["users"] == 0


def test_card_is_in_the_tools_view():
    from tests._front import front_page
    p = front_page()
    assert 'id="card-del"' in p and "/api/account/delete" in p and "confirm(" in p
