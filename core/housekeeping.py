"""
core/housekeeping.py — ลอกท่อรอบดึก: เก็บกวาดตะกอนที่สะสมเงียบๆ ในเซิร์ฟเวอร์

เจ้าของโปรเจกต์: "เหมือนท่อระบายน้ำ ไม่ลอกทีนึงไม่รู้ว่าตะไคร่เหนียวแค่ไหน · ทุกอย่างทำงานตลอดทุกวินาที
ถ้าไม่มีเบรก พักแบบที่ผู้ใช้ไม่เดือดร้อน แล้วล้างของเก่าที่รก การอัปเดตครั้งต่อไปจะยิ่งยาก
และของที่ควรดูแลจริงๆ กลับไม่ได้ดูแล"

หลักการ:
1. ล้างเฉพาะ "ตะกอน" — ของที่หมดหน้าที่แล้วแน่ๆ · ไม่แตะของสำคัญ: บัญชี เครดิต การจ่ายเงิน
   ประวัติปรึกษา บันทึก audit (append-only โดยตั้งใจ) และสำเนาสำรอง (DATABASE/backup วนเก็บเองอยู่แล้ว)
2. ทำตอนดึกเวลาไทย (02:00–05:59) วันละครั้ง · ถ้าเซิร์ฟเวอร์ไม่เคยได้ทำเกิน 30 ชม. (เช่นหลับตอนดึก) ทำได้ทุกเวลา
3. ทุกขั้นแยกกัน พังขั้นไหนข้ามขั้นนั้น ไม่ทำให้เซิร์ฟเวอร์ล้ม · งานเบา ใช้เวลาไม่ถึงวินาที ผู้ใช้ไม่รู้สึก
4. เรียกจากรอบตรวจตัวเองของ core/self_heal (ทุก 10 นาที) · ผลล่าสุดดูได้ที่ /health

สิ่งที่ล้าง:
- usage_daily: ตัวนับโควตาฟรีรายวัน ใช้แค่ของ "วันนี้" แต่เดิมเก็บทุกวันทุกคนไปตลอด → เก็บ 7 วันล่าสุด
- หน่วยความจำ: บันทึกเวลาส่งเมลประวัติ (app._history_mail_last) ที่เกินช่วงกันส่งถี่แล้ว
- ประโยคที่ผู้ใช้แนบมากับปุ่มรายงาน เมื่อครบ 90 วัน (core/answer_reports)
- decision_reports ที่หมดอายุแล้ว (เดิมลบแค่ตอนเปิดเซิร์ฟเวอร์)
- SQLite: PRAGMA optimize (สถิติให้ค้นเร็ว) + checkpoint WAL (ไฟล์ -wal ไม่บวมเรื่อยๆ)
"""
from __future__ import annotations

import sys
import threading
import time
from datetime import datetime, timedelta, timezone

_BKK = timezone(timedelta(hours=7))
QUIET_HOURS = range(2, 6)
EVERY_S = 20 * 3600
OVERDUE_S = 30 * 3600
KEEP_USAGE_DAYS = 7

_lock = threading.Lock()
_last: dict = {"at": None, "ts": 0.0, "done": {}, "skipped": []}


def _usage_daily(now: datetime) -> int:
    from DATABASE.db import get_conn
    cut = (now - timedelta(days=KEEP_USAGE_DAYS)).strftime("%Y-%m-%d")
    conn = get_conn()
    try:
        n = conn.execute("DELETE FROM usage_daily WHERE day < ?", (cut,)).rowcount
        conn.commit()
        return n
    finally:
        conn.close()


def _mail_memory(now: datetime) -> int:
    app = sys.modules.get("app")
    if not app or not hasattr(app, "_history_mail_last"):
        return 0
    t, gap = now.timestamp(), getattr(app, "_HISTORY_MAIL_GAP", 600)
    with app._history_mail_lock:
        old = [k for k, v in app._history_mail_last.items() if t - v >= gap]
        for k in old:
            app._history_mail_last.pop(k, None)
    return len(old)


def _expired_reports(now: datetime) -> int:
    """รายงานที่หมดอายุแล้ว — เดิมลบแค่ตอนเปิดเซิร์ฟเวอร์ ถ้ารันยาวหลายสัปดาห์จะค้างอยู่"""
    from DATABASE.db import get_conn
    conn = get_conn()
    try:
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='decision_reports'").fetchone():
            return 0
        n = conn.execute("DELETE FROM decision_reports WHERE expires_at IS NOT NULL AND expires_at <= datetime('now')").rowcount
        conn.commit()
        return n
    finally:
        conn.close()


def _report_questions(now: datetime) -> int:
    """ประโยคที่ผู้ใช้แนบมากับรายงาน — ลบเมื่อครบ 90 วัน"""
    from core.answer_reports import forget_old_questions
    return forget_old_questions(now.timestamp())


def _sqlite(now: datetime) -> str:
    from DATABASE.db import get_conn
    conn = get_conn()
    try:
        conn.execute("PRAGMA optimize")
        r = conn.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone()
        return "ok" if r is None else f"wal {r[1]}/{r[2]}"
    finally:
        conn.close()


STEPS = (("usage_daily", _usage_daily), ("mail_memory", _mail_memory), ("expired_reports", _expired_reports), ("report_questions", _report_questions), ("sqlite", _sqlite))


def due(now: datetime | None = None) -> bool:
    now = now or datetime.now(_BKK)
    since = now.timestamp() - _last["ts"]
    if since >= OVERDUE_S:
        return True
    return since >= EVERY_S and now.hour in QUIET_HOURS


def run(now: datetime | None = None, force: bool = False) -> dict:
    """ลอกท่อหนึ่งรอบ (ถ้าถึงเวลา) · คืนผลของแต่ละขั้น"""
    now = now or datetime.now(_BKK)
    if not _lock.acquire(blocking=False):
        return dict(_last)
    try:
        if not force and not due(now):
            return dict(_last)
        done, skipped = {}, []
        for name, fn in STEPS:
            try:
                done[name] = fn(now)
            except Exception as e:  # noqa: BLE001 — ขั้นไหนพังข้ามขั้นนั้น
                skipped.append(f"{name}: {type(e).__name__}")
        _last.update(at=now.strftime("%Y-%m-%d %H:%M"), ts=now.timestamp(), done=done, skipped=skipped)
        print(f"🧹 housekeeping: {done}" + (f" · ข้าม {skipped}" if skipped else ""))
        return dict(_last)
    finally:
        _lock.release()


def status() -> dict:
    return {k: v for k, v in _last.items() if k != "ts"}
