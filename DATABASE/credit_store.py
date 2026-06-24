# DATABASE/credit_store.py
# KING DIADEM — Credit Store
# ต่อ SQLite จริง ไม่ใช่ in-memory dict ที่หายทุก restart

from __future__ import annotations
import threading

_lock = threading.Lock()


def _conn():
    """ดึง connection จาก db.py — ใช้ path เดียวกับระบบ"""
    try:
        from DATABASE.db import get_conn
        return get_conn()
    except Exception:
        # fallback: SQLite ตรงๆ
        import sqlite3, os
        path = os.getenv("DB_PATH", "data/king_diadem.db")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return sqlite3.connect(path, check_same_thread=False)


def _ensure_table() -> None:
    """สร้าง table ถ้ายังไม่มี"""
    conn = _conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_credits (
                email   TEXT PRIMARY KEY,
                credits INTEGER NOT NULL DEFAULT 0,
                updated REAL    NOT NULL DEFAULT (julianday('now'))
            )
        """)
        conn.commit()
    finally:
        conn.close()


# สร้าง table ตอน import
try:
    _ensure_table()
except Exception:
    pass


# ── Public API ────────────────────────────────────────────────────

def get_credits(email: str) -> int:
    with _lock:
        conn = _conn()
        try:
            row = conn.execute(
                "SELECT credits FROM user_credits WHERE email = ?", (email,)
            ).fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()


def add_credits(email: str, amount: int) -> int:
    """เพิ่ม credits — return ยอดใหม่"""
    with _lock:
        conn = _conn()
        try:
            conn.execute("""
                INSERT INTO user_credits (email, credits, updated)
                VALUES (?, ?, julianday('now'))
                ON CONFLICT(email) DO UPDATE SET
                    credits = credits + excluded.credits,
                    updated = julianday('now')
            """, (email, int(amount)))
            conn.commit()
            row = conn.execute(
                "SELECT credits FROM user_credits WHERE email = ?", (email,)
            ).fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()


def use_credit(email: str, amount: int = 1) -> bool:
    """ใช้ credit — return True ถ้าสำเร็จ False ถ้าไม่พอ"""
    with _lock:
        conn = _conn()
        try:
            row = conn.execute(
                "SELECT credits FROM user_credits WHERE email = ?", (email,)
            ).fetchone()
            current = int(row[0]) if row else 0
            if current < amount:
                return False
            conn.execute("""
                UPDATE user_credits
                SET credits = credits - ?,
                    updated = julianday('now')
                WHERE email = ?
            """, (amount, email))
            conn.commit()
            return True
        finally:
            conn.close()


def set_credits(email: str, amount: int) -> int:
    """ตั้งค่า credits ตรงๆ — ใช้สำหรับ admin หรือ Stripe webhook"""
    with _lock:
        conn = _conn()
        try:
            conn.execute("""
                INSERT INTO user_credits (email, credits, updated)
                VALUES (?, ?, julianday('now'))
                ON CONFLICT(email) DO UPDATE SET
                    credits = excluded.credits,
                    updated = julianday('now')
            """, (email, int(amount)))
            conn.commit()
            return int(amount)
        finally:
            conn.close()


def get_all_credits() -> list[dict]:
    """Admin helper — ดู credits ทุก user"""
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT email, credits, updated FROM user_credits ORDER BY credits DESC"
        ).fetchall()
        return [{"email": r[0], "credits": r[1], "updated": r[2]} for r in rows]
    finally:
        conn.close()
