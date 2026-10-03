# DATABASE/user_db.py
"""
KING DIADEM — User DB
⚠️ ปัญหาเดิม: เก็บ password plaintext — แก้เป็น hash แล้ว
ใช้ hashlib.pbkdf2_hmac — stdlib ไม่ต้องติดตั้งอะไรเพิ่ม
"""
from __future__ import annotations
import sqlite3
import hashlib
import hmac
import os
import time
from typing import Optional

# LEGACY (ไม่มีผู้เรียก): ระบบบัญชีจริงอยู่ใน DATABASE/db.py
# เดิมเขียนลง "king_diadem.db" ที่ root ของโปรเจกต์ (คนละไฟล์กับ DB จริง data/king_diadem.db)
# และตาราง users/payments มีชื่อชนกับ schema ของ db.py — แยกไฟล์ให้ชัดเจน ตั้งได้ด้วย USER_DB_PATH
DB_NAME = os.getenv("USER_DB_PATH", "data/legacy_user_db.sqlite")


# ── Password hashing — stdlib only ───────────────────────────────
def _hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    """Return (hash_hex, salt_hex)"""
    if salt is None:
        salt = os.urandom(32)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return dk.hex(), salt.hex()

def _verify_password(password: str, hash_hex: str, salt_hex: str) -> bool:
    try:
        salt = bytes.fromhex(salt_hex)
    except (TypeError, ValueError):
        return False
    dk   = hashlib.pbkdf2_hmac("sha256", str(password).encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(dk.hex(), str(hash_hex))   # เดิม == (เวลาไม่คงที่)


# ── Context manager helper ────────────────────────────────────────
def _conn():
    d = os.path.dirname(DB_NAME)
    if d:
        os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(DB_NAME, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


# ── Schema init ───────────────────────────────────────────────────
def init_db() -> None:
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    UNIQUE NOT NULL,
                pwd_hash    TEXT    NOT NULL,
                pwd_salt    TEXT    NOT NULL,
                credits     INTEGER DEFAULT 0,
                plan        TEXT    DEFAULT 'free',
                created_at  REAL    DEFAULT (unixepoch()),
                last_login  REAL
            )
        """)
        # payments table — sync กับ payment_store.py
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments(
                id          TEXT PRIMARY KEY,
                email       TEXT,
                amount      REAL DEFAULT 0,
                plan        TEXT DEFAULT '',
                provider    TEXT DEFAULT 'stripe',
                created_at  REAL DEFAULT (unixepoch())
            )
        """)
        conn.commit()


# ── CRUD ──────────────────────────────────────────────────────────
def create_user(email: str, password: str) -> bool:
    """Return True ถ้าสร้างสำเร็จ — False ถ้า email ซ้ำ"""
    try:
        pwd_hash, pwd_salt = _hash_password(password)
        with _conn() as conn:
            conn.execute(
                "INSERT INTO users(email, pwd_hash, pwd_salt) VALUES(?,?,?)",
                (email.lower().strip(), pwd_hash, pwd_salt),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False   # email ซ้ำ
    except Exception:
        return False


def get_user(email: str) -> Optional[dict]:
    try:
        with _conn() as conn:
            row = conn.execute(
                "SELECT id, email, pwd_hash, pwd_salt, credits, plan, created_at, last_login "
                "FROM users WHERE email = ?",
                (email.lower().strip(),)
            ).fetchone()
            if not row:
                return None
            return dict(row)
    except Exception:
        return None


def verify_user(email: str, password: str) -> bool:
    user = get_user(email)
    if not user:
        _hash_password(str(password or "x"))   # เวลาเท่ากัน ไม่บอกใบ้ว่า email มีอยู่ไหม
        return False
    ok = _verify_password(password, user["pwd_hash"], user["pwd_salt"])
    if ok:
        # update last_login
        try:
            with _conn() as conn:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE email = ?",
                    (time.time(), email.lower().strip())
                )
                conn.commit()
        except Exception:
            pass
    return ok


def add_credit(email: str, amount: int) -> bool:
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
    if amount <= 0:            # เดิมรับค่าลบ = หักเครดิตผ่านฟังก์ชัน "เพิ่ม"
        return False
    try:
        with _conn() as conn:
            conn.execute(
                "UPDATE users SET credits = credits + ? WHERE email = ?",
                (amount, email.lower().strip()),
            )
            conn.commit()
        return True
    except Exception:
        return False


def get_credits(email: str) -> int:
    user = get_user(email)
    return user["credits"] if user else 0


def use_credit(email: str, amount: int = 1) -> bool:
    """Deduct credit — return False ถ้าไม่พอ"""
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
    if amount <= 0:
        return False
    try:
        with _conn() as conn:
            # UPDATE มีเงื่อนไขคำสั่งเดียว = atomic (เดิม SELECT แล้ว UPDATE → หักซ้ำได้)
            cur = conn.execute(
                "UPDATE users SET credits = credits - ? WHERE email = ? AND credits >= ?",
                (amount, email.lower().strip(), amount),
            )
            conn.commit()
        return cur.rowcount == 1
    except Exception:
        return False


def set_plan(email: str, plan: str) -> bool:
    try:
        with _conn() as conn:
            conn.execute(
                "UPDATE users SET plan = ? WHERE email = ?",
                (plan, email.lower().strip()),
            )
            conn.commit()
        return True
    except Exception:
        return False
