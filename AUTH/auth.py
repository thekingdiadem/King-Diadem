# AUTH/auth.py
# KING DIADEM — Auth Router v2.0
# Fix: password hashed (SHA-256), /add_credit ต้องมี admin_key
# -----------------------------------------------------------------

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib
import os

router = APIRouter()
DB     = "king_diadem.db"

# Admin key จาก env — ถ้าไม่ set จะ block ทุก admin call
ADMIN_KEY = os.getenv("KD_ADMIN_KEY", "")


# ── HELPERS ───────────────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _get_conn():
    return sqlite3.connect(DB)


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

init_db()


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
    conn = _get_conn()
    row = conn.execute(
        "SELECT password, credits, paid FROM users WHERE username=?",
        (user.username,)
    ).fetchone()
    conn.close()

    if not row:
        return {"status": "no_user"}
    if row[0] != _hash(user.password):
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
    if not ADMIN_KEY or x_admin_key != ADMIN_KEY:
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
    if not ADMIN_KEY or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="unauthorized")

    conn = _get_conn()
    conn.execute(
        "UPDATE users SET paid=1 WHERE username=?",
        (username,)
    )
    conn.commit()
    conn.close()
    return {"status": "paid", "username": username}
