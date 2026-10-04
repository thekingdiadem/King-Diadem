# AUTH/api_keys.py
# KING DIADEM — API Key Generator v2.0
# Fix: key ถูก save ลง DB จริง + ไม่ให้ create ซ้ำโดยไม่ตั้งใจ
# -----------------------------------------------------------------

import secrets
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
        conn = _connect()
        _ensure_api_keys_table(conn)

        # ตรวจว่า user มีอยู่จริง
        row = conn.execute(
            "SELECT username FROM users WHERE username=?", (username,)
        ).fetchone()

        if not row:
            conn.close()
            return {"status": "error", "reason": "user_not_found"}

        # เครดิตต้อนรับให้เฉพาะ key แรก — เดิมให้ 100 ทุกครั้งที่สร้าง key = เครดิตไม่จำกัด
        first_key = conn.execute(
            "SELECT 1 FROM api_keys WHERE username=? LIMIT 1", (username,)
        ).fetchone() is None

        # Save key
        conn.execute(
            "INSERT INTO api_keys (key, username) VALUES (?, ?)",
            (key, username)
        )

        if first_key:
            conn.execute(
                "UPDATE users SET credits = credits + 100 WHERE username=?",
                (username,)
            )

        conn.commit()
        conn.close()

        return {"key": key, "username": username, "status": "created"}

    except Exception:
        return {"status": "error", "reason": "api_key_unavailable"}


def revoke_api_key(key: str) -> bool:
    """ปิด key โดยไม่ลบออก (audit trail)"""
    try:
        conn = _connect()
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
    if not isinstance(key, str) or not key.startswith("kd_") or len(key) > 100:
        return None
    try:
        conn = _connect()
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
