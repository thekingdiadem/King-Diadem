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
import hashlib
import hmac
import secrets
from contextlib import closing
from typing import Optional

try:
    import bcrypt
    _BCRYPT = True
except ImportError:
    _BCRYPT = False

# ── Config ────────────────────────────────────────────────────────
# DB เดียวกับแอป (DB_PATH) — เดิมอ่าน KD_DB_PATH อย่างเดียว ตั้งค่าไม่ตรงกันได้ง่าย
DB_PATH         = os.environ.get("KD_DB_PATH") or os.environ.get("DB_PATH", "data/king_diadem.db")
# ตารางชื่อ users ถูก DATABASE/db.py สร้างไปแล้วด้วย schema อื่น (ไม่มี password_hash/api_key)
# → CREATE IF NOT EXISTS ข้าม แล้ว INSERT ล้มเงียบทุกครั้ง  จึงใช้ตารางของตัวเอง
TABLE           = "api_users"
INITIAL_CREDITS = 10
API_KEY_PREFIX  = "kd_"

_lock = threading.Lock()


# ── DB init ───────────────────────────────────────────────────────
def _get_conn() -> sqlite3.Connection:
    d = os.path.dirname(DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_table() -> None:
    with closing(_get_conn()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_users (
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
    # fallback (ไม่มี bcrypt): PBKDF2-SHA256 200k รอบ — เดิม sha256 รอบเดียว เดาได้เร็วมาก
    salt = secrets.token_hex(16)
    h    = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"pbkdf2${salt}${h}"


def _verify_password(password: str, stored: str) -> bool:
    stored = str(stored or "")
    try:
        if stored.startswith("pbkdf2$"):
            _, salt, h = stored.split("$", 2)
            calc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
            return hmac.compare_digest(calc, h)
        if _BCRYPT and stored.startswith("$2"):
            return bcrypt.checkpw(password.encode(), stored.encode())
        if ":" in stored:   # รูปแบบเก่า salt:sha256 — compare แบบ constant-time
            salt, h = stored.split(":", 1)
            return hmac.compare_digest(hashlib.sha256((salt + password).encode()).hexdigest(), h)
    except Exception:
        return False
    return False


def _amount(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


_DUMMY_HASH = _hash_password(secrets.token_hex(8))


# ── Core API ──────────────────────────────────────────────────────
def create_user(email: str, password: str) -> Optional[str]:
    """
    สร้าง user ใหม่
    คืน api_key ถ้าสำเร็จ / None ถ้า email ซ้ำ

    Article 2 — password hash + unique api_key เสมอ
    """
    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        return None

    api_key = API_KEY_PREFIX + secrets.token_hex(16)

    with _lock:
        try:
            ensure_table()
            with closing(_get_conn()) as conn:
                conn.execute("""
                    INSERT INTO api_users (email, password_hash, api_key, credits, created_at)
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
    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        return None

    try:
        with closing(_get_conn()) as conn:
            row = conn.execute(
                "SELECT api_key, password_hash FROM api_users WHERE email = ?",
                (email.lower().strip(),)
            ).fetchone()

        if not row:
            _verify_password(password, _DUMMY_HASH)   # เวลาเท่ากัน ไม่บอกใบ้ว่า email มีอยู่ไหม
            return None

        if not _verify_password(password, row["password_hash"]):
            return None

        # update last_login (non-blocking best-effort)
        try:
            with closing(_get_conn()) as conn:
                conn.execute(
                    "UPDATE api_users SET last_login = ? WHERE email = ?",
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
        with closing(_get_conn()) as conn:
            row = conn.execute(
                "SELECT email, credits, created_at, last_login FROM api_users WHERE api_key = ?",
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
    amount = _amount(amount)
    if amount <= 0:
        return {"success": False, "credits_remaining": 0, "reason": "invalid amount"}

    with _lock:
        try:
            with closing(_get_conn()) as conn:
                # UPDATE เดียวแบบมีเงื่อนไข = atomic ข้าม process ด้วย (gunicorn หลาย worker)
                # เดิม SELECT แล้ว UPDATE ... AND credits=? แต่ไม่ดู rowcount → แพ้ race ก็ยังรายงานสำเร็จ
                cur = conn.execute(
                    "UPDATE api_users SET credits = credits - ? WHERE api_key = ? AND credits >= ?",
                    (amount, api_key, amount)
                )
                conn.commit()
                row = conn.execute(
                    "SELECT credits FROM api_users WHERE api_key = ?", (api_key,)
                ).fetchone()

            if not row:
                return {"success": False, "credits_remaining": 0, "reason": "user not found"}
            if cur.rowcount == 0:
                return {"success": False, "credits_remaining": int(row["credits"]), "reason": "insufficient credits"}
            return {"success": True, "credits_remaining": int(row["credits"]), "reason": "ok"}
        except Exception:
            return {"success": False, "credits_remaining": 0, "reason": "db_error"}


def add_credits(api_key: str, amount: int) -> dict:
    """เพิ่ม credits — ใช้หลัง payment / admin"""
    amount = _amount(amount)
    if amount <= 0:
        return {"success": False, "reason": "invalid amount"}

    with _lock:
        try:
            with closing(_get_conn()) as conn:
                result = conn.execute(
                    "UPDATE api_users SET credits = credits + ? WHERE api_key = ?",
                    (amount, api_key)
                )
                conn.commit()
                if result.rowcount == 0:
                    return {"success": False, "reason": "user not found"}
                row = conn.execute(
                    "SELECT credits FROM api_users WHERE api_key = ?", (api_key,)
                ).fetchone()
            return {"success": True, "credits_remaining": int(row["credits"])}
        except Exception:
            return {"success": False, "reason": "db_error"}


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
