# core/users.py
# KING DIADEM™ — User Registry
# 
# ❌ REMOVED: flat JSON file, SHA256 no-salt, race condition, no atomic credit ops
# ✅ REBUILT: SQLite + bcrypt + threading.Lock + atomic credit deduction
#
# Article 2: Trust is earned, bounded, and auditable.
# Article 6: Bounded memory — no unbounded growth.

import sqlite3
import threading
import uuid
import os
import time
from typing import Optional

try:
    import bcrypt
    _BCRYPT = True
except ImportError:
    import hashlib, secrets
    _BCRYPT = False

# ── Config ────────────────────────────────────────────────────────
DB_PATH         = os.environ.get("KD_DB_PATH", "data/king_diadem.db")
INITIAL_CREDITS = 10
API_KEY_PREFIX  = "kd_"

_lock = threading.Lock()


# ── DB init ───────────────────────────────────────────────────────
def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_table() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email        TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                api_key      TEXT NOT NULL UNIQUE,
                credits      INTEGER NOT NULL DEFAULT 10,
                created_at   REAL NOT NULL,
                last_login   REAL
            )
        """)
        conn.commit()


# ── Password ──────────────────────────────────────────────────────
def _hash_password(password: str) -> str:
    if _BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # fallback: sha256 + random salt (ถ้าไม่มี bcrypt)
    salt = secrets.token_hex(16)
    h    = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def _verify_password(password: str, stored: str) -> bool:
    if _BCRYPT:
        try:
            return bcrypt.checkpw(password.encode(), stored.encode())
        except Exception:
            return False
    # fallback
    try:
        salt, h = stored.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == h
    except Exception:
        return False


# ── Core API ──────────────────────────────────────────────────────
def create_user(email: str, password: str) -> Optional[str]:
    """
    สร้าง user ใหม่
    คืน api_key ถ้าสำเร็จ / None ถ้า email ซ้ำ

    Article 2 — password hash + unique api_key เสมอ
    """
    if not email or not password:
        return None

    api_key = API_KEY_PREFIX + uuid.uuid4().hex

    with _lock:
        try:
            with _get_conn() as conn:
                conn.execute("""
                    INSERT INTO users (email, password_hash, api_key, credits, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (email.lower().strip(), _hash_password(password),
                      api_key, INITIAL_CREDITS, time.time()))
                conn.commit()
            return api_key
        except sqlite3.IntegrityError:
            return None  # email ซ้ำ
        except Exception:
            return None


def authenticate_user(email: str, password: str) -> Optional[str]:
    """
    ตรวจ email + password
    คืน api_key ถ้าถูก / None ถ้าผิด

    ใช้ constant-time compare ผ่าน bcrypt
    """
    if not email or not password:
        return None

    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT api_key, password_hash FROM users WHERE email = ?",
                (email.lower().strip(),)
            ).fetchone()

        if not row:
            return None

        if not _verify_password(password, row["password_hash"]):
            return None

        # update last_login (non-blocking best-effort)
        try:
            with _get_conn() as conn:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE email = ?",
                    (time.time(), email.lower().strip())
                )
                conn.commit()
        except Exception:
            pass

        return row["api_key"]

    except Exception:
        return None


def get_user_by_api_key(api_key: str) -> Optional[dict]:
    """คืน user dict จาก api_key — ใช้ใน gateway auth"""
    if not api_key:
        return None
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT email, credits, created_at, last_login FROM users WHERE api_key = ?",
                (api_key,)
            ).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def get_credits(api_key: str) -> int:
    """คืน credits ปัจจุบัน"""
    user = get_user_by_api_key(api_key)
    return int(user["credits"]) if user else 0


def deduct_credit(api_key: str, amount: int = 1) -> dict:
    """
    ตัด credit แบบ atomic — ไม่มี double-charge
    คืน {"success": bool, "credits_remaining": int, "reason": str}

    Article 6 — atomic transaction ป้องกัน race condition
    """
    if amount <= 0:
        return {"success": False, "credits_remaining": 0, "reason": "invalid amount"}

    with _lock:
        try:
            with _get_conn() as conn:
                row = conn.execute(
                    "SELECT credits FROM users WHERE api_key = ?", (api_key,)
                ).fetchone()

                if not row:
                    return {"success": False, "credits_remaining": 0, "reason": "user not found"}

                current = int(row["credits"])
                if current < amount:
                    return {"success": False, "credits_remaining": current, "reason": "insufficient credits"}

                new_credits = current - amount
                conn.execute(
                    "UPDATE users SET credits = ? WHERE api_key = ? AND credits = ?",
                    (new_credits, api_key, current)  # optimistic lock
                )
                conn.commit()

            return {"success": True, "credits_remaining": new_credits, "reason": "ok"}
        except Exception as e:
            return {"success": False, "credits_remaining": 0, "reason": str(e)}


def add_credits(api_key: str, amount: int) -> dict:
    """เพิ่ม credits — ใช้หลัง payment / admin"""
    if amount <= 0:
        return {"success": False, "reason": "invalid amount"}

    with _lock:
        try:
            with _get_conn() as conn:
                result = conn.execute(
                    "UPDATE users SET credits = credits + ? WHERE api_key = ?",
                    (amount, api_key)
                )
                conn.commit()
                if result.rowcount == 0:
                    return {"success": False, "reason": "user not found"}
                row = conn.execute(
                    "SELECT credits FROM users WHERE api_key = ?", (api_key,)
                ).fetchone()
            return {"success": True, "credits_remaining": int(row["credits"])}
        except Exception as e:
            return {"success": False, "reason": str(e)}


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    ensure_table()
    test_email = f"__test_{uuid.uuid4().hex[:6]}__@kd.test"
    pw = "TestPass123!"

    # create
    key = create_user(test_email, pw)
    assert key is not None and key.startswith(API_KEY_PREFIX)

    # duplicate
    dup = create_user(test_email, pw)
    assert dup is None

    # auth success
    auth_key = authenticate_user(test_email, pw)
    assert auth_key == key

    # auth fail
    bad = authenticate_user(test_email, "wrongpassword")
    assert bad is None

    # credits
    assert get_credits(key) == INITIAL_CREDITS

    # deduct
    r1 = deduct_credit(key, 3)
    assert r1["success"] is True
    assert r1["credits_remaining"] == INITIAL_CREDITS - 3

    # insufficient
    r2 = deduct_credit(key, 999)
    assert r2["success"] is False
    assert r2["reason"] == "insufficient credits"

    # add
    r3 = add_credits(key, 10)
    assert r3["success"] is True
    assert get_credits(key) == (INITIAL_CREDITS - 3 + 10)

    # get_user
    user = get_user_by_api_key(key)
    assert user["email"] == test_email

    return {"status": "OK", "module": "users", "bcrypt": _BCRYPT}


if __name__ == "__main__":
    ensure_table()
    print(_self_test())
