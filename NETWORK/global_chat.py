# NETWORK/global_chat.py
# KING DIADEM — Global Chat Store
# Persistent SQLite — ไม่ใช่ in-memory deque
# รวม global_network.py ไว้ที่เดียว (ทั้งสองทำสิ่งเดียวกัน)

from __future__ import annotations
import time
import threading

_lock = threading.Lock()
MAX_FETCH = 200


def _conn():
    try:
        from DATABASE.db import get_conn
        return get_conn()
    except Exception:
        import sqlite3, os
        path = os.getenv("DB_PATH", "data/king_diadem.db")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return sqlite3.connect(path, check_same_thread=False)


def _ensure_table() -> None:
    conn = _conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS global_chat (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                ts      REAL    NOT NULL,
                user    TEXT    NOT NULL,
                message TEXT    NOT NULL,
                channel TEXT    NOT NULL DEFAULT 'global',
                meta    TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_ts ON global_chat(ts)")
        conn.commit()
    finally:
        conn.close()


try:
    _ensure_table()
except Exception:
    pass


# ── Public API ────────────────────────────────────────────────────

def add_chat(user: str, message: str, channel: str = "global") -> bool:
    """เพิ่มข้อความลง global chat"""
    with _lock:
        conn = _conn()
        try:
            conn.execute(
                "INSERT INTO global_chat (ts, user, message, channel) VALUES (?, ?, ?, ?)",
                (time.time(), str(user), str(message), str(channel)),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"⚠ global_chat.add_chat: {e}")
            return False
        finally:
            conn.close()


# alias สำหรับ global_network.py ที่ใช้ชื่อต่างกัน
def add_message(user: str, text: str, channel: str = "global") -> bool:
    return add_chat(user, text, channel)


def get_chat(limit: int = 50, channel: str = "") -> list[dict]:
    """ดู messages ล่าสุด"""
    conn = _conn()
    try:
        if channel:
            rows = conn.execute(
                "SELECT ts, user, message, channel FROM global_chat "
                "WHERE channel = ? ORDER BY ts DESC LIMIT ?",
                (channel, min(limit, MAX_FETCH)),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT ts, user, message, channel FROM global_chat "
                "ORDER BY ts DESC LIMIT ?",
                (min(limit, MAX_FETCH),),
            ).fetchall()
        return [
            {"ts": r[0], "user": r[1], "message": r[2], "channel": r[3]}
            for r in reversed(rows)  # เรียงจากเก่าไปใหม่
        ]
    finally:
        conn.close()


# alias
def get_messages(limit: int = 50) -> list[dict]:
    return get_chat(limit)


def count_messages(channel: str = "") -> int:
    conn = _conn()
    try:
        if channel:
            row = conn.execute(
                "SELECT COUNT(*) FROM global_chat WHERE channel = ?", (channel,)
            ).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) FROM global_chat").fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def clear_old_messages(keep_days: int = 7) -> int:
    """ลบ messages เก่ากว่า N วัน"""
    cutoff = time.time() - (keep_days * 86400)
    with _lock:
        conn = _conn()
        try:
            cur = conn.execute("DELETE FROM global_chat WHERE ts < ?", (cutoff,))
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()
