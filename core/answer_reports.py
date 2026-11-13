"""
core/answer_reports.py — ผู้ใช้รายงานคำตอบของ AI ที่ไม่เหมาะสม (ปุ่มธงใต้คำตอบ)

ต่างจากปุ่ม "ช่วยได้ / ยังไม่ช่วย" (core/feedback_loop.py) ที่เก็บแค่ตัวเลข — รายงานต้องมีตัวคำตอบ
ไม่อย่างนั้นคนดูแลจะไม่รู้ว่าต้องแก้อะไร ผู้ใช้จึงเห็นก่อนกดส่งว่าอะไรถูกส่งไปบ้าง

เก็บ: เหตุผล · เส้นทาง · ระดับความเสี่ยง · คำตอบของ AI ข้อนั้น · ข้อความที่ผู้ใช้เขียนเพิ่มเอง (ถ้ามี)
ไม่เก็บ: ข้อความที่ผู้ใช้พิมพ์ถาม · อีเมล · IP
"""
from __future__ import annotations

import re
import threading
import time

REASONS = ("harmful", "offensive", "wrong", "other")
MAX_ANSWER = 4000
MAX_NOTE = 500
_ROUTES = ("general", "risk", "civil", "survival", "collapse", "vega")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_lock = threading.Lock()
_ready = False


def _conn():
    from DATABASE.db import get_conn
    return get_conn()


def _ensure(conn) -> None:
    global _ready
    if _ready:
        return
    conn.execute("""
        CREATE TABLE IF NOT EXISTS answer_reports (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            ts     REAL NOT NULL,
            reason TEXT NOT NULL,
            route  TEXT NOT NULL DEFAULT 'general',
            risk   INTEGER NOT NULL DEFAULT 0,
            note   TEXT NOT NULL DEFAULT '',
            answer TEXT NOT NULL
        )
    """)
    conn.commit()
    _ready = True


def _text(value, limit: int) -> str:
    return _CTRL.sub("", value).strip()[:limit] if isinstance(value, str) else ""


def record(reason, answer, note=None, route=None, risk=None) -> dict:
    """บันทึกรายงานหนึ่งรายการ — คืน {"ok": True} หรือ {"ok": False, "error": ...}"""
    reason = str(reason or "").lower().strip() if isinstance(reason, str) else ""
    if reason not in REASONS:
        return {"ok": False, "error": "เลือกเหตุผลก่อนส่งนะคะ"}
    answer = _text(answer, MAX_ANSWER)
    if not answer:
        return {"ok": False, "error": "ไม่พบคำตอบที่จะรายงานค่ะ"}
    route = str(route or "general").lower().strip() if isinstance(route, str) else "general"
    if route not in _ROUTES:
        route = "general"
    try:
        risk = float(risk)
        risk = round(max(0.0, min(100.0, risk))) if risk == risk else 0
    except (TypeError, ValueError):
        risk = 0
    with _lock:
        conn = _conn()
        try:
            _ensure(conn)
            conn.execute("INSERT INTO answer_reports (ts, reason, route, risk, note, answer) VALUES (?,?,?,?,?,?)",
                         (time.time(), reason, route, risk, _text(note, MAX_NOTE), answer))
            conn.commit()
        finally:
            conn.close()
    return {"ok": True}


def recent(limit: int = 50) -> list:
    """รายงานล่าสุด (ใหม่ก่อน) — ให้ผู้ดูแลอ่าน"""
    limit = max(1, min(int(limit or 50), 200))
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT id, ts, reason, route, risk, note, answer FROM answer_reports ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "ts": r[1], "reason": r[2], "route": r[3], "risk": r[4], "note": r[5], "answer": r[6]} for r in rows]


def count() -> int:
    conn = _conn()
    try:
        _ensure(conn)
        return int(conn.execute("SELECT COUNT(*) FROM answer_reports").fetchone()[0])
    finally:
        conn.close()
