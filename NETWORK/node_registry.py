
# NETWORK/node_registry.py
# KING DIADEM — Node Registry
# Persistent SQLite — node ไม่หายทุก restart

from __future__ import annotations
import time
import json
import threading

_lock        = threading.Lock()
NODE_TIMEOUT = 120  # วินาที


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
            CREATE TABLE IF NOT EXISTS network_nodes (
                node_id   TEXT PRIMARY KEY,
                host      TEXT,
                started   REAL,
                last_seen REAL NOT NULL,
                status    TEXT NOT NULL DEFAULT 'active',
                meta      TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()


try:
    _ensure_table()
except Exception:
    pass


# ── Public API ────────────────────────────────────────────────────

def register_node(node_id: str, data: dict) -> bool:
    now = time.time()
    data = data if isinstance(data, dict) else {}
    try:
        started = float(data.get("started", now))
    except (TypeError, ValueError):
        started = now
    with _lock:
        conn = _conn()
        try:
            conn.execute("""
                INSERT INTO network_nodes (node_id, host, started, last_seen, status, meta)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    status    = excluded.status,
                    meta      = excluded.meta
            """, (
                str(node_id),
                str(data.get("host", ""))[:200],
                started,
                now,
                str(data.get("status", "active")),
                json.dumps({k: v for k, v in data.items()
                            if k not in ("host", "started", "status", "last_seen")},
                           ensure_ascii=False, default=str)[:4000],
            ))
            conn.commit()
            return True
        finally:
            conn.close()


def heartbeat(node_id: str) -> bool:
    with _lock:
        conn = _conn()
        try:
            cur = conn.execute(
                "UPDATE network_nodes SET last_seen = ? WHERE node_id = ?",
                (time.time(), str(node_id)),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


def remove_dead_nodes() -> int:
    cutoff = time.time() - NODE_TIMEOUT
    with _lock:
        conn = _conn()
        try:
            cur = conn.execute(
                "DELETE FROM network_nodes WHERE last_seen < ?", (cutoff,)
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()


def get_nodes() -> dict:
    """Return active nodes dict — auto-cleanup dead ก่อน"""
    remove_dead_nodes()
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT node_id, host, started, last_seen, status, meta "
            "FROM network_nodes ORDER BY last_seen DESC"
        ).fetchall()
        result = {}
        for r in rows:
            try:
                meta = json.loads(r[5]) if r[5] else {}
            except Exception:
                meta = {}
            # meta ก่อน แล้วค่อยทับด้วยคอลัมน์จริง — เดิม meta เขียนทับ last_seen/status ได้
            result[r[0]] = {
                **(meta if isinstance(meta, dict) else {}),
                "host":      r[1],
                "started":   r[2],
                "last_seen": r[3],
                "status":    r[4],
            }
        return result
    finally:
        conn.close()


def get_node(node_id: str) -> dict | None:
    conn = _conn()
    try:
        row = conn.execute(
            "SELECT node_id, host, started, last_seen, status FROM network_nodes "
            "WHERE node_id = ?", (str(node_id),)
        ).fetchone()
        if not row:
            return None
        return {
            "node_id":   row[0],
            "host":      row[1],
            "started":   row[2],
            "last_seen": row[3],
            "status":    row[4],
        }
    finally:
        conn.close()
