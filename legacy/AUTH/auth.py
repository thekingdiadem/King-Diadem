# AUTH/auth.py
# KING DIADEM — Auth Router v2.0
# Fix: password hashed (SHA-256), /add_credit ต้องมี admin_key
# -----------------------------------------------------------------

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib
import hmac
import os
import secrets

router = APIRouter()
# LEGACY (ไม่มีผู้เรียก — ระบบบัญชีจริงอยู่ใน app.py + DATABASE/db.py)
DB     = os.getenv("AUTH_DB_PATH", "data/legacy_auth.sqlite")

# Admin key จาก env — ถ้าไม่ set จะ block ทุก admin call
ADMIN_KEY = os.getenv("KD_ADMIN_KEY", "")


# ── HELPERS ───────────────────────────────────────────────────────

def _hash(password: str) -> str:
    """PBKDF2-SHA256 + salt — เดิม sha256 ไม่มี salt (เดาด้วย rainbow table ได้)"""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"pbkdf2${salt}${dk}"


def _check(password: str, stored: str) -> bool:
    stored = str(stored or "")
    if stored.startswith("pbkdf2$"):
        try:
            _, salt, dk = stored.split("$", 2)
        except ValueError:
            return False
        got = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
        return hmac.compare_digest(got, dk)
    # รูปแบบเก่า sha256 ล้วน (ยังรองรับเพื่อไม่ล็อกผู้ใช้เดิมออก)
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored)


def _admin_ok(key: str) -> bool:
    return bool(ADMIN_KEY) and hmac.compare_digest(str(key or ""), ADMIN_KEY)


def _get_conn():
    d = os.path.dirname(DB)
    if d:
        os.makedirs(d, exist_ok=True)
    return sqlite3.connect(DB, timeout=15)


# ── INIT DB ───────────────────────────────────────────────────────

def init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            credits  INTEGER DEFAULT 0,
            paid     INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# เดิมเรียก init_db() ตอน import → สร้างไฟล์ DB ทุกครั้งที่มีใคร import โมดูลนี้
_ready = False

def _ensure():
    global _ready
    if not _ready:
        init_db()
        _ready = True


# ── MODELS ────────────────────────────────────────────────────────

class Register(BaseModel):
    username: str
    password: str

class Login(BaseModel):
    username: str
    password: str


# ── REGISTER ──────────────────────────────────────────────────────

@router.post("/register")
def register(user: Register):
    if not user.username.strip() or not user.password.strip():
        raise HTTPException(status_code=400, detail="username/password ห้ามว่าง")

    _ensure()
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (user.username.strip(), _hash(user.password))
        )
        conn.commit()
        return {"status": "created"}
    except sqlite3.IntegrityError:
        return {"status": "exists"}
    finally:
        conn.close()


# ── LOGIN ─────────────────────────────────────────────────────────

@router.post("/login")
def login(user: Login):
    _ensure()
    conn = _get_conn()
    row = conn.execute(
        "SELECT password, credits, paid FROM users WHERE username=?",
        (user.username,)
    ).fetchone()
    conn.close()

    # ไม่แยก "ไม่มีผู้ใช้" กับ "รหัสผิด" — เดิมบอกได้ว่า username ไหนมีอยู่
    if not row or not _check(user.password, row[0]):
        return {"status": "wrong"}

    return {"status": "ok", "credits": row[1], "paid": row[2]}


# ── ADD CREDIT (admin only) ────────────────────────────────────────

@router.post("/add_credit/{username}/{amount}")
def add_credit(
    username: str,
    amount:   int,
    x_admin_key: str = Header(default=""),
):
    """
    ต้องส่ง header: X-Admin-Key: <KD_ADMIN_KEY>
    ป้องกันใครก็ได้เติม credit ตัวเอง
    """
    if not _admin_ok(x_admin_key):
        raise HTTPException(status_code=403, detail="unauthorized")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    conn = _get_conn()
    conn.execute(
        "UPDATE users SET credits = credits + ? WHERE username=?",
        (amount, username)
    )
    conn.commit()
    conn.close()
    return {"status": "credited", "username": username, "amount": amount}


# ── SET PAID (admin only) ──────────────────────────────────────────

@router.post("/set_paid/{username}")
def set_paid(
    username:    str,
    x_admin_key: str = Header(default=""),
):
    if not _admin_ok(x_admin_key):
        raise HTTPException(status_code=403, detail="unauthorized")

    conn = _get_conn()
    conn.execute(
        "UPDATE users SET paid=1 WHERE username=?",
        (username,)
    )
    conn.commit()
    conn.close()
    return {"status": "paid", "username": username}
