"""การยืนยันสองชั้น (2FA) แบบรหัส 6 หลักจากแอป Authenticator — RFC 6238 (TOTP) / RFC 4226 (HOTP)

ใช้แค่ไลบรารีมาตรฐาน · ใช้ได้กับ Google Authenticator, Microsoft Authenticator, 1Password, Authy ฯลฯ
- กุญแจลับ 160 บิตต่อบัญชี เก็บในฐานข้อมูลแบบเข้ารหัส (seal/unseal ด้วยกุญแจจาก SECRET_KEY)
  ฐานข้อมูลหลุดอย่างเดียวจึงสร้างรหัสแทนเจ้าของไม่ได้
- รหัสหนึ่งตัวใช้ได้ครั้งเดียว (จำช่วงเวลาที่ใช้ล่าสุด) กันคนแอบดูแล้วใช้ซ้ำ
- รหัสกู้คืน 8 ชุดไว้ใช้ตอนทำมือถือหาย เก็บเป็น hash ใช้ได้ชุดละครั้ง
"""
import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

STEP = 30          # วินาทีต่อรหัส
DIGITS = 6
WINDOW = 1         # ยอมรับช่วงก่อน/หลัง 1 ช่วง (นาฬิกามือถือคลาดได้ ~30 วินาที)
ISSUER = "KING DIADEM"


def new_secret() -> str:
    """กุญแจลับแบบ base32 (ไม่มี =) สำหรับใส่ในแอป Authenticator"""
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _key(secret_b32: str) -> bytes:
    s = secret_b32.strip().replace(" ", "").upper()
    return base64.b32decode(s + "=" * (-len(s) % 8))


def code_at(secret_b32: str, step: int) -> str:
    mac = hmac.new(_key(secret_b32), struct.pack(">Q", step), hashlib.sha1).digest()
    off = mac[-1] & 0x0F
    n = (struct.unpack(">I", mac[off:off + 4])[0] & 0x7FFFFFFF) % (10 ** DIGITS)
    return str(n).zfill(DIGITS)


def current_step(now: float = None) -> int:
    return int((time.time() if now is None else now) // STEP)


def verify(secret_b32: str, code: str, last_step: int = -1, now: float = None):
    """คืนเลขช่วงเวลาที่ตรง (ไว้บันทึกกันใช้ซ้ำ) หรือ None ถ้าไม่ตรง / เคยใช้แล้ว"""
    code = "".join(ch for ch in str(code or "") if ch.isdigit())
    if len(code) != DIGITS:
        return None
    base = current_step(now)
    for st in range(base - WINDOW, base + WINDOW + 1):
        if st > last_step and hmac.compare_digest(code_at(secret_b32, st), code):
            return st
    return None


def otpauth_uri(secret_b32: str, account: str) -> str:
    """ลิงก์ที่แอป Authenticator เปิดได้ทันทีบนมือถือ (และใช้ทำ QR)"""
    label = quote(f"{ISSUER}:{account}")
    return f"otpauth://totp/{label}?secret={secret_b32}&issuer={quote(ISSUER)}&digits={DIGITS}&period={STEP}"


# ── รหัสกู้คืน ────────────────────────────────────────────────────
_ALPHA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"     # ไม่มี 0/O/1/I ที่อ่านสับสน


def new_recovery_codes(n: int = 8) -> list:
    return ["".join(secrets.choice(_ALPHA) for _ in range(5)) + "-" + "".join(secrets.choice(_ALPHA) for _ in range(5))
            for _ in range(n)]


def norm_recovery(code: str) -> str:
    c = "".join(ch for ch in str(code or "").upper() if ch.isalnum())
    return c[:5] + "-" + c[5:] if len(c) == 10 else ""


def hash_recovery(code: str) -> str:
    return hashlib.sha256(norm_recovery(code).encode()).hexdigest()


# ── เข้ารหัสกุญแจลับก่อนเก็บ ─────────────────────────────────────────
def _stream(key: bytes, nonce: bytes, n: int) -> bytes:
    out, i = b"", 0
    while len(out) < n:
        out += hashlib.sha256(key + nonce + struct.pack(">I", i)).digest()
        i += 1
    return out[:n]


def seal(secret_b32: str, master: str) -> str:
    key = hashlib.sha256(("kd-2fa|" + master).encode()).digest()
    nonce = secrets.token_bytes(16)
    ct = bytes(a ^ b for a, b in zip(secret_b32.encode(), _stream(key, nonce, len(secret_b32))))
    tag = hmac.new(key, nonce + ct, hashlib.sha256).digest()[:16]
    return base64.urlsafe_b64encode(nonce + ct + tag).decode()


def unseal(blob: str, master: str):
    try:
        raw = base64.urlsafe_b64decode(blob.encode())
        nonce, ct, tag = raw[:16], raw[16:-16], raw[-16:]
        key = hashlib.sha256(("kd-2fa|" + master).encode()).digest()
        if not hmac.compare_digest(tag, hmac.new(key, nonce + ct, hashlib.sha256).digest()[:16]):
            return None
        return bytes(a ^ b for a, b in zip(ct, _stream(key, nonce, len(ct)))).decode()
    except Exception:
        return None
