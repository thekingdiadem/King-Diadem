# AUTH/api_key_manager.py
# KING DIADEM — Credit Manager v2.0
# Fix: atomic SELECT+UPDATE ป้องกัน race condition
# -----------------------------------------------------------------

import sqlite3
import os as _os

# LEGACY (ไม่มีผู้เรียก) — เดิมใช้ "king_diadem.db" ที่ root (คนละไฟล์กับ DB จริง และตาราง users ชนกับ
# DATABASE/user_db.py) แยกเป็นไฟล์ของ AUTH เอง ตั้งได้ด้วย AUTH_DB_PATH
DB = _os.getenv("AUTH_DB_PATH", "data/legacy_auth.sqlite")


def _connect(**kw):
    d = _os.path.dirname(DB)
    if d:
        _os.makedirs(d, exist_ok=True)
    return sqlite3.connect(DB, timeout=15, **kw)


def use_credit(username: str, amount: int = 1) -> bool:
    """
    ตัด credit อย่าง atomic — SELECT และ UPDATE ใน transaction เดียว

    Returns True ถ้าสำเร็จ, False ถ้า credit ไม่พอหรือ user ไม่มี
    """
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
    if amount <= 0:
        return False  # เดิมคืน True → cost 0/ติดลบ = ใช้ฟรีไม่จำกัด

    try:
        conn = _connect(isolation_level=None)  # จัดการ transaction เอง (BEGIN/COMMIT)
        conn.execute("BEGIN IMMEDIATE")  # lock ป้องกัน concurrent write

        row = conn.execute(
            "SELECT credits FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if not row:
            conn.execute("ROLLBACK")
            conn.close()
            return False

        current = row[0]
        if current < amount:
            conn.execute("ROLLBACK")
            conn.close()
            return False

        conn.execute(
            "UPDATE users SET credits = credits - ? WHERE username=?",
            (amount, username)
        )
        conn.execute("COMMIT")
        conn.close()
        return True

    except Exception:
        try:
            conn.execute("ROLLBACK")
            conn.close()
        except Exception:
            pass
        return False


def get_credits(username: str) -> int:
    """Return credit balance, 0 ถ้า user ไม่มี"""
    try:
        conn = _connect()
        row = conn.execute(
            "SELECT credits FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()
        return int(row[0]) if row else 0
    except Exception:
        return 0


def add_credits(username: str, amount: int) -> bool:
    """เพิ่ม credit (ใช้จาก Stripe webhook)"""
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
    if amount <= 0:
        return False
    try:
        conn = _connect()
        conn.execute(
            "UPDATE users SET credits = credits + ? WHERE username=?",
            (amount, username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False
