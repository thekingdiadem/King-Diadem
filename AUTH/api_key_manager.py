# AUTH/api_key_manager.py
# KING DIADEM — Credit Manager v2.0
# Fix: atomic SELECT+UPDATE ป้องกัน race condition
# -----------------------------------------------------------------

import sqlite3

DB = "king_diadem.db"


def use_credit(username: str, amount: int = 1) -> bool:
    """
    ตัด credit อย่าง atomic — SELECT และ UPDATE ใน transaction เดียว

    Returns True ถ้าสำเร็จ, False ถ้า credit ไม่พอหรือ user ไม่มี
    """
    if amount <= 0:
        return True  # ไม่ต้องตัด

    try:
        conn = sqlite3.connect(DB, isolation_level=None)  # autocommit off
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
        conn = sqlite3.connect(DB)
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
    if amount <= 0:
        return False
    try:
        conn = sqlite3.connect(DB)
        conn.execute(
            "UPDATE users SET credits = credits + ? WHERE username=?",
            (amount, username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False
