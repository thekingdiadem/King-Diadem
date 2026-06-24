# DATABASE/decision_history.py
# KING DIADEM — Decision History
# ต่อ SQLite จริง ไม่เขียน JSON file (Render ephemeral disk)
# business_engine.py เรียก save_decision(result) — signature เดิม

from __future__ import annotations
import json
import time
import threading

_lock = threading.Lock()


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
            CREATE TABLE IF NOT EXISTS decision_history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        REAL    NOT NULL,
                domain    TEXT    NOT NULL DEFAULT 'general',
                route     TEXT    NOT NULL DEFAULT 'general',
                strategy  TEXT,
                risk_level TEXT,
                waterline REAL,
                payload   TEXT    NOT NULL
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

def save_decision(decision: dict) -> bool:
    """
    บันทึก decision result ลง DB
    รับ dict จาก business_engine / domain_router / app.py
    """
    if not isinstance(decision, dict):
        return False

    with _lock:
        conn = _conn()
        try:
            conn.execute("""
                INSERT INTO decision_history
                    (ts, domain, route, strategy, risk_level, waterline, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(),
                str(decision.get("domain",    "general")),
                str(decision.get("route",     "general")),
                str(decision.get("recommended_strategy", decision.get("strategy", ""))),
                str(decision.get("risk_level",  decision.get("risk", {}).get("level", ""))),
                decision.get("waterline"),
                json.dumps(decision, ensure_ascii=False, default=str),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"⚠ decision_history.save_decision: {e}")
            return False
        finally:
            conn.close()


def get_recent_decisions(
    limit:  int  = 10,
    domain: str  = "",
    route:  str  = "",
) -> list[dict]:
    """
    ดู decisions ล่าสุด
    filter by domain / route ถ้าระบุ
    """
    conn = _conn()
    try:
        where_parts = []
        params: list = []
        if domain:
            where_parts.append("domain = ?")
            params.append(domain)
        if route:
            where_parts.append("route = ?")
            params.append(route)

        where = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
        params.append(limit)

        rows = conn.execute(
            f"SELECT ts, domain, route, strategy, risk_level, waterline, payload "
            f"FROM decision_history {where} ORDER BY ts DESC LIMIT ?",
            params,
        ).fetchall()

        results = []
        for r in rows:
            try:
                payload = json.loads(r[6])
            except Exception:
                payload = {}
            results.append({
                "ts":         r[0],
                "domain":     r[1],
                "route":      r[2],
                "strategy":   r[3],
                "risk_level": r[4],
                "waterline":  r[5],
                "decision":   payload,
            })
        return results
    finally:
        conn.close()


def count_decisions(domain: str = "") -> int:
    """นับจำนวน decisions ทั้งหมด"""
    conn = _conn()
    try:
        if domain:
            row = conn.execute(
                "SELECT COUNT(*) FROM decision_history WHERE domain = ?", (domain,)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) FROM decision_history"
            ).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def clear_old_decisions(keep_days: int = 30) -> int:
    """ลบ decisions เก่ากว่า N วัน — return จำนวนที่ลบ"""
    cutoff = time.time() - (keep_days * 86400)
    with _lock:
        conn = _conn()
        try:
            cur = conn.execute(
                "DELETE FROM decision_history WHERE ts < ?", (cutoff,)
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()
