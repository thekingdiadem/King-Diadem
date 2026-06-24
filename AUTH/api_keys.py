# AUTH/api_keys.py
# KING DIADEM — API Key Generator v2.0
# Fix: key ถูก save ลง DB จริง + ไม่ให้ create ซ้ำโดยไม่ตั้งใจ
# -----------------------------------------------------------------

import secrets
import sqlite3

DB = "king_diadem.db"


def _ensure_api_keys_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key      TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            created  INTEGER DEFAULT (strftime('%s','now')),
            active   INTEGER DEFAULT 1
        )
    """)
    conn.commit()


def create_api_key(username: str) -> dict:
    """
    สร้าง API key ใหม่ บันทึกลง DB และให้ 100 credits

    Returns
    -------
    {"key": "kd_...", "username": "...", "status": "created"}
    หรือ {"status": "error", "reason": "..."}
    """
    key = "kd_" + secrets.token_hex(16)

    try:
        conn = sqlite3.connect(DB)
        _ensure_api_keys_table(conn)

        # ตรวจว่า user มีอยู่จริง
        row = conn.execute(
            "SELECT username FROM users WHERE username=?", (username,)
        ).fetchone()

        if not row:
            conn.close()
            return {"status": "error", "reason": "user_not_found"}

        # Save key
        conn.execute(
            "INSERT INTO api_keys (key, username) VALUES (?, ?)",
            (key, username)
        )

        # Add 100 credits
        conn.execute(
            "UPDATE users SET credits = credits + 100 WHERE username=?",
            (username,)
        )

        conn.commit()
        conn.close()

        return {"key": key, "username": username, "status": "created"}

    except Exception as e:
        return {"status": "error", "reason": str(e)}


def revoke_api_key(key: str) -> bool:
    """ปิด key โดยไม่ลบออก (audit trail)"""
    try:
        conn = sqlite3.connect(DB)
        _ensure_api_keys_table(conn)
        conn.execute(
            "UPDATE api_keys SET active=0 WHERE key=?", (key,)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def validate_api_key(key: str) -> dict | None:
    """
    ตรวจ key ว่า active ไหม
    Return {"username": "..."} หรือ None
    """
    try:
        conn = sqlite3.connect(DB)
        _ensure_api_keys_table(conn)
        row = conn.execute(
            "SELECT username FROM api_keys WHERE key=? AND active=1",
            (key,)
        ).fetchone()
        conn.close()
        if row:
            return {"username": row[0]}
        return None
    except Exception:
        return None
