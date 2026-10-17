"""กดออกจากระบบแล้ว คุกกี้ที่ถูกคัดลอกไว้ก่อนหน้าต้องใช้ไม่ได้ (เดิมใช้ได้ต่อถึง 30 วัน)"""
import uuid


def test_copied_cookie_dies_after_logout(client):
    email = f"u{uuid.uuid4().hex[:10]}@example.com"
    assert client.post("/register", json={"email": email, "password": "password123"}).status_code == 200
    saved = client.cookies.get("kd_email")
    assert client.get("/me").json()["logged_in"] is True
    assert client.post("/logout").status_code == 200
    client.cookies.set("kd_email", saved)
    assert client.get("/me").json()["logged_in"] is False


def test_logging_in_again_after_logout_works(client):
    email = f"u{uuid.uuid4().hex[:10]}@example.com"
    client.post("/register", json={"email": email, "password": "password123"})
    client.post("/logout")
    r = client.post("/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200 and client.get("/me").json()["logged_in"] is True


def test_old_style_cookie_still_works_until_logout():
    """คุกกี้รุ่นก่อน (อีเมลอย่างเดียว) ยังล็อกอินอยู่ จนกว่าผู้ใช้จะกดออก — ไม่เด้งทุกคนออกตอนอัปเดต"""
    import app
    from starlette.requests import Request
    tok = app._session_signer.dumps("legacy@example.com")
    req = Request({"type": "http", "headers": [(b"cookie", f"kd_email={tok}".encode())]})
    assert app._session_email(req) == "legacy@example.com"
