"""ระบบบัญชี: กันยึดบัญชีด้วยการสมัครแทน, จำกัดการเดารหัสต่อเครื่อง, จำกัดการสร้างบัญชีรัวๆ,
การแฮชรหัสผ่านไม่ขวางคนอื่น และ cookie ของ OAuth"""
import asyncio
import types
import uuid

from fastapi.testclient import TestClient

from DATABASE import db


class _FakeGoogle:
    def __init__(self, email):
        self.email = email

    async def authorize_access_token(self, request):
        return {"userinfo": {"email": self.email, "email_verified": True, "name": "Owner"}}


def _google_login(client, app_module, monkeypatch, email):
    monkeypatch.setattr(app_module, "oauth", types.SimpleNamespace(google=_FakeGoogle(email)))
    return client.get("/auth/google/callback", follow_redirects=False)


def test_pre_registered_password_is_dropped_when_owner_signs_in_with_google(client, app_module, monkeypatch):
    """เดิม: คนร้ายสมัครด้วยอีเมลของเหยื่อไว้ก่อน (ไม่มีการยืนยันอีเมล) → เหยื่อเข้าด้วย Google ได้บัญชีเดียวกัน
    → คนร้าย login ด้วยรหัสที่ตัวเองตั้ง แล้วอ่านแชต/ความจำ/เครดิตของเหยื่อได้"""
    victim = f"victim{uuid.uuid4().hex[:8]}@gmail.com"
    assert client.post("/register", json={"email": victim, "password": "attackerpw1"}).status_code == 200

    owner = TestClient(app_module.app, base_url="https://testserver", headers={"cf-connecting-ip": "10.250.0.1"})
    r = _google_login(owner, app_module, monkeypatch, victim)
    assert r.status_code in (302, 307) and r.headers["location"] == "/"
    assert db.email_verified(victim) and not db.has_password(victim)

    attacker = TestClient(app_module.app, base_url="https://testserver", headers={"cf-connecting-ip": "10.250.0.2"})
    assert attacker.post("/login", json={"email": victim, "password": "attackerpw1"}).status_code == 401


def test_password_set_after_verification_is_kept(client, app_module, monkeypatch):
    """ยืนยันครั้งแรกเท่านั้นที่ลบรหัสผ่าน — เข้าด้วย Google ครั้งถัดๆ ไปไม่แตะบัญชี"""
    email = f"g{uuid.uuid4().hex[:8]}@gmail.com"
    _google_login(client, app_module, monkeypatch, email)
    assert db.email_verified(email)
    assert db.set_password(email, "ownerpass1")          # (ถ้ามีช่องทางตั้งรหัสภายหลัง) ไม่ถูกลบซ้ำ
    _google_login(client, app_module, monkeypatch, email)
    assert db.verify_password(email, "ownerpass1")


def test_one_ip_cannot_spray_a_password_across_many_accounts(client):
    """เดิมจำกัดแค่ต่อ (IP, อีเมล) — เครื่องเดียวลองรหัสเดียวกับอีเมลนับพันได้ไม่จำกัด"""
    codes = [client.post("/login", json={"email": f"s{i}{uuid.uuid4().hex[:6]}@x.co", "password": "Password1"}).status_code
             for i in range(25)]
    assert codes[:20] == [401] * 20 and set(codes[20:]) == {429}


def test_registrations_per_ip_are_capped(client):
    """เดิมนับเฉพาะสมัครไม่สำเร็จ — สคริปต์สร้างบัญชีได้ไม่จำกัด แต่ละบัญชีได้ 10 เครดิต + โควตาฟรีของตัวเอง"""
    codes = [client.post("/register", json={"email": f"bot{i}{uuid.uuid4().hex[:6]}@x.co", "password": "password123"}).status_code
             for i in range(7)]
    assert codes[:5] == [200] * 5 and set(codes[5:]) == {429}


def test_password_hashing_does_not_block_other_requests(client, app_module, monkeypatch):
    """worker มีตัวเดียว — แฮช PBKDF2 ใน event loop ทำให้ทุกคนค้างตาม · ต้องทำใน threadpool"""
    seen = {}
    real = app_module.verify_password

    def spy(email, password):
        try:
            asyncio.get_running_loop()
            seen["in_loop"] = True
        except RuntimeError:
            seen["in_loop"] = False
        return real(email, password)

    monkeypatch.setattr(app_module, "verify_password", spy)
    client.post("/login", json={"email": "nobody@x.co", "password": "whatever1"})
    assert seen == {"in_loop": False}


def test_oauth_session_cookie_is_secure_and_short_lived(client, app_module):
    from starlette.middleware.sessions import SessionMiddleware
    mw = [m for m in app_module.app.user_middleware if m.cls is SessionMiddleware][0]
    kw = getattr(mw, "kwargs", None) or getattr(mw, "options", {})
    assert kw.get("https_only") is True and kw.get("max_age") == 600
