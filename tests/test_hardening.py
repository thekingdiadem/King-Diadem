"""เสริมความปลอดภัย (เจ้าของโปรเจกต์ถามหลังข่าวการใช้ AI โจมตีสถาบันการเงิน)

1. ตัวนับกันเดารหัส / สมัครถี่ / rate limit ไม่หายตอนเซิร์ฟเวอร์รีสตาร์ท — เดิมอยู่ในหน่วยความจำอย่างเดียว
   บอทจึงรอจังหวะ deploy หรือ Render พักเครื่อง แล้วเดารหัสต่อจากศูนย์ได้
2. แฮชรหัสผ่าน PBKDF2 600,000 รอบ (OWASP 2023) และแฮชเก่า 200,000 รอบอัปเกรดเองตอนล็อกอินสำเร็จ
3. ไลบรารีทุกตัวล็อกเวอร์ชัน และ CI ตรวจช่องโหว่ด้วย pip-audit
"""
import hashlib
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_login_failures_survive_a_restart(client):
    import app as A
    key = "203.0.113.9|victim@example.com"
    for _ in range(A._LOGIN_MAX):
        A._login_failed(key)
    assert A._login_blocked(key)
    # จำลองรีสตาร์ท: หน่วยความจำว่าง แล้วโหลดจากฐานข้อมูล
    A._login_fail.clear()
    assert not A._login_blocked(key)
    A._restore_throttles()
    assert A._login_blocked(key)                                     # ยังโดนบล็อกต่อ ไม่เริ่มนับใหม่
    assert A._login_fail.get("email|victim@example.com")             # นับต่ออีเมลก็กลับมา


def test_rate_limit_and_signup_quota_survive_a_restart(client):
    import app as A
    who = "rate-test|198.51.100.7"
    for _ in range(A._RATE_LIMIT_N):
        assert A._rate_check(who)
    assert not A._rate_check(who)
    A._rate_bucket.clear(); A._restore_throttles()
    assert not A._rate_check(who)

    ip = "198.51.100.77"
    for _ in range(A._REG_OK_MAX):
        A._reg_succeeded(ip)
    A._reg_ok.clear(); A._restore_throttles()
    assert not A._reg_quota_left(ip)


def test_old_rows_are_pruned_and_window_respected(client):
    from DATABASE import db
    import time
    now = time.time()
    db.throttle_add("login", ["old-key"], now - 2 * 86400)
    db.throttle_add("login", ["new-key"], now)
    keys = {k for k, _ in db.throttle_load("login", now - 600)}
    assert "new-key" in keys and "old-key" not in keys


def test_password_hash_rounds_and_upgrade(client):
    from DATABASE import db
    assert db._PBKDF2_ROUNDS >= 600_000
    email = f"old-{secrets.token_hex(4)}@example.com"
    salt = secrets.token_hex(16)
    old = f"pbkdf2_sha256$200000${salt}${hashlib.pbkdf2_hmac('sha256', b'pw-12345678', salt.encode(), 200000).hex()}"
    conn = db.get_conn()
    conn.execute("INSERT INTO user_passwords (user_email, password_hash) VALUES (?, ?)", (email, old)); conn.commit(); conn.close()
    assert not db.verify_password(email, "wrong-password")
    conn = db.get_conn(); h = conn.execute("SELECT password_hash FROM user_passwords WHERE user_email = ?", (email,)).fetchone()[0]; conn.close()
    assert h == old                                                  # รหัสผิด: ไม่แตะแฮช
    assert db.verify_password(email, "pw-12345678")
    conn = db.get_conn(); h = conn.execute("SELECT password_hash FROM user_passwords WHERE user_email = ?", (email,)).fetchone()[0]; conn.close()
    assert h.split("$")[1] == str(db._PBKDF2_ROUNDS) and h != old    # อัปเกรดแล้ว
    assert db.verify_password(email, "pw-12345678")                  # ยังล็อกอินได้


def test_every_dependency_is_pinned_and_audited():
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        spec = line.split("#", 1)[0].strip()
        if spec:
            assert re.fullmatch(r"[A-Za-z0-9_.\-\[\]]+==[0-9][0-9A-Za-z.]*", spec), spec
    ci = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "pip-audit -r requirements.txt" in ci
