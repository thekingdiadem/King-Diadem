"""การยืนยันสองชั้น (2FA · TOTP) — เจ้าของโปรเจกต์ขอเพิ่มหลังตรวจความปลอดภัย

ใส่รหัสผ่านถูกอย่างเดียวต้องยังเข้าไม่ได้ ต้องกรอกรหัส 6 หลักจากแอป Authenticator ด้วย
รหัสหนึ่งตัวใช้ได้ครั้งเดียว · รหัสกู้คืนใช้ได้ชุดละครั้ง · ปิด 2FA ต้องมีรหัส"""
import uuid
from pathlib import Path

from core import totp

ROOT = Path(__file__).resolve().parent.parent
PW = "correct-horse-9"


def _new_user(client):
    email = f"tfa-{uuid.uuid4().hex[:8]}@example.com"
    assert client.post("/register", json={"email": email, "password": PW}).status_code == 200
    return email


def _enable(client):
    s = client.post("/api/2fa/setup").json()
    assert s["uri"].startswith("otpauth://totp/") and "secret=" + s["secret"] in s["uri"]
    st = totp.current_step()
    r = client.post("/api/2fa/enable", json={"code": totp.code_at(s["secret"], st)})
    assert r.status_code == 200, r.text
    return s["secret"], st, r.json()["recovery_codes"]


def test_rfc6238_vectors():
    s = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"                    # "12345678901234567890"
    assert [totp.code_at(s, t // 30) for t in (59, 1111111109, 1234567890)] == ["287082", "081804", "005924"]


def test_secret_is_stored_sealed():
    sealed = totp.seal("ABCDEFGHIJKLMNOP", "k1")
    assert "ABCDEFGHIJKLMNOP" not in sealed and totp.unseal(sealed, "k1") == "ABCDEFGHIJKLMNOP"
    assert totp.unseal(sealed, "other-key") is None


def test_full_flow_password_alone_is_not_enough(client):
    email = _new_user(client)
    secret, st, codes = _enable(client)
    assert len(codes) == 8 and len(set(codes)) == 8
    assert client.get("/me").json()["twofa"] is True
    client.post("/logout")

    r = client.post("/login", json={"email": email, "password": PW})
    assert r.status_code == 200 and r.json()["status"] == "2fa_required"
    assert "kd_email" not in r.cookies                          # ยังไม่ได้คุกกี้ล็อกอิน
    assert client.get("/me").json()["logged_in"] is False

    assert client.post("/login/2fa", json={"code": "000000"}).status_code == 401
    # รหัสที่ใช้ตอนเปิดไปแล้ว ใช้ซ้ำไม่ได้ · รหัสช่วงถัดไปใช้ได้
    assert client.post("/login/2fa", json={"code": totp.code_at(secret, st)}).status_code == 401
    r = client.post("/login/2fa", json={"code": totp.code_at(secret, st + 1)})
    assert r.status_code == 200 and client.get("/me").json()["email"] == email


def test_recovery_code_works_once_and_disable_needs_a_code(client):
    email = _new_user(client)
    secret, st, codes = _enable(client)
    client.post("/logout")
    client.post("/login", json={"email": email, "password": PW})
    assert client.post("/login/2fa", json={"code": codes[0].lower()}).json()["used_recovery"] is True
    assert client.get("/api/2fa").json()["recovery_left"] == 7
    client.post("/logout")
    client.post("/login", json={"email": email, "password": PW})
    assert client.post("/login/2fa", json={"code": codes[0]}).status_code == 401          # ใช้ซ้ำไม่ได้
    assert client.post("/login/2fa", json={"code": codes[1]}).status_code == 200
    # ปิดต้องมีรหัส — คนที่แค่ยืมเครื่องที่ล็อกอินค้างไว้ปิดไม่ได้
    assert client.post("/api/2fa/disable", json={"code": "123456"}).status_code == 400
    assert client.post("/api/2fa/disable", json={"code": codes[2]}).status_code == 200
    assert client.get("/api/2fa").json()["enabled"] is False


def test_no_ticket_no_entry(client):
    client.cookies.clear()
    assert client.post("/login/2fa", json={"code": "123456"}).status_code == 401
    assert client.post("/api/2fa/setup").status_code == 401


def test_enabling_logs_out_other_devices(client):
    email = _new_user(client)
    old = client.cookies.get("kd_email")
    _enable(client)
    assert client.get("/me").json()["logged_in"] is True          # เครื่องนี้ยังอยู่ (ได้คุกกี้ใหม่)
    from fastapi.testclient import TestClient
    import app as A
    other = TestClient(A.app, base_url="https://testserver")      # อีกเครื่องที่ถือคุกกี้ก่อนเปิด 2FA
    other.cookies.set("kd_email", old)
    assert other.get("/me").json()["logged_in"] is False          # ใช้ไม่ได้แล้ว


def test_google_login_also_asks_for_the_code():
    src = (ROOT / "app.py").read_text(encoding="utf-8")
    cb = src[src.index("async def google_callback"):src.index("def _safe_name")]
    assert "if _twofa_on(email):" in cb and 'RedirectResponse("/static/login.html?step=2fa")' in cb
    login = (ROOT / "static" / "login.html").read_text(encoding="utf-8")
    assert "get('step') === '2fa'" in login and 'autocomplete="one-time-code"' in login


def test_new_recovery_codes_replace_old_set(client):
    """รหัสกู้คืนหลุด (เช่นติดไปในภาพหน้าจอ) → สร้างชุดใหม่ได้ ชุดเก่าใช้ไม่ได้ทันที"""
    email = _new_user(client)
    secret, st, old = _enable(client)
    # ต้องใช้รหัสจากแอปเท่านั้น — รหัสกู้คืนที่หลุดไปเอามาสร้างชุดใหม่ไม่ได้
    assert client.post("/api/2fa/recovery", json={"code": old[0]}).status_code == 400
    assert client.post("/api/2fa/recovery", json={"code": totp.code_at(secret, st)}).status_code == 400   # ใช้ซ้ำไม่ได้
    r = client.post("/api/2fa/recovery", json={"code": totp.code_at(secret, st + 1)})
    assert r.status_code == 200, r.text
    new = r.json()["recovery_codes"]
    assert len(new) == 8 and not set(new) & set(old)
    assert client.get("/api/2fa").json()["recovery_left"] == 8

    client.post("/logout")
    client.post("/login", json={"email": email, "password": PW})
    assert client.post("/login/2fa", json={"code": old[1]}).status_code == 401
    assert client.post("/login/2fa", json={"code": new[0]}).status_code == 200


def test_new_recovery_codes_need_login_and_2fa_on(client):
    client.cookies.clear()
    assert client.post("/api/2fa/recovery", json={"code": "123456"}).status_code == 401
    _new_user(client)
    assert client.post("/api/2fa/recovery", json={"code": "123456"}).status_code == 400


def test_tools_card_has_regenerate_button():
    src = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert "id', 'tfa-regen'" in src or "'tfa-regen'" in src
    assert "/api/2fa/recovery" in src


def test_setup_gives_a_scannable_qr_for_desktop(client):
    """เปิด 2FA บนคอม: มี QR ให้มือถือสแกนจากจอ ไม่ต้องพิมพ์กุญแจ 32 ตัวเอง (เจ้าของโปรเจกต์เคยต้องพิมพ์เอง)"""
    _new_user(client)
    s = client.post("/api/2fa/setup").json()
    qr = s["qr"]
    assert qr.startswith("<svg") and "<script" not in qr.lower() and " on" not in qr.lower()
    # ภาพตรงกับข้อมูลจริง: วาดช่องดำตาม path แล้วเทียบกับเมทริกซ์ของลิงก์ otpauth เดียวกัน
    import re
    import qrcode
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    q.add_data(s["uri"])
    q.make(fit=True)
    want = q.get_matrix()
    n = len(want)
    got = [[False] * n for _ in range(n)]
    for x, y, w in re.findall(r"M(\d+) (\d+)h(\d+)", qr):
        for i in range(int(w)):
            got[int(y)][int(x) + i] = True
    assert got == want


def test_qr_is_inserted_only_when_it_is_plain_svg():
    src = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert "/^<svg[\\s>]/.test(d.qr)" in src and "<script|\\son\\w+=|href=" in src
