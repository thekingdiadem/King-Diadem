"""เฝ้าข้อเท็จจริงใน SECURITY/QUANTUM_READINESS.md — ถ้าวันหนึ่งมีคนเพิ่ม RSA/ECC หรือลดรอบ PBKDF2 เอกสารจะไม่ตรงกับของจริง
และกันไม่ให้มีฟังก์ชัน "QKD จำลอง" ที่คืนคำว่าปลอดภัยโดยไม่มีช่องควอนตัมจริงให้วัด (อ้างความปลอดภัยเกินจริง)"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"tests", "__pycache__", ".git", "node_modules"}
PY = [p for p in ROOT.rglob("*.py") if not SKIP & set(p.relative_to(ROOT).parts)]


def test_no_asymmetric_crypto_in_app_code():
    """โค้ดเราใช้แต่ hash/HMAC/PBKDF2 ซึ่งควอนตัมไม่ทำให้แตก — จุดเสี่ยงควอนตัมมีที่เดียวคือ TLS ของผู้ให้บริการโฮสต์"""
    bad = re.compile(r"^\s*(?:import|from)\s+(rsa|ecdsa|Crypto|cryptography|nacl|jwt|OpenSSL)\b", re.M)
    hits = [str(p.relative_to(ROOT)) for p in PY if bad.search(p.read_text(encoding="utf-8", errors="ignore"))]
    assert hits == [], hits
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert not re.search(r"^(cryptography|pyjwt|rsa|ecdsa|pynacl)\b", req, re.M)


def test_password_hashing_stays_strong():
    db = (ROOT / "DATABASE/db.py").read_text(encoding="utf-8")
    assert int(re.search(r"_PBKDF2_ROUNDS = ([\d_]+)", db).group(1).replace("_", "")) >= 600_000
    assert 'pbkdf2_hmac("sha256"' in db and "compare_digest" in db


def test_no_simulated_qkd_claims_security():
    for p in PY:
        t = p.read_text(encoding="utf-8", errors="ignore")
        assert "silent_interception" not in t and "QUANTUM_CHANNEL_PURE" not in t, p
    doc = (ROOT / "SECURITY/QUANTUM_READINESS.md").read_text(encoding="utf-8")
    assert "ไม่ได้ป้องกันอะไร" in doc and "X25519MLKEM768" in doc and "ยังไม่ได้ยืนยัน" in doc
