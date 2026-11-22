"""
core/progress.py — สถานะเบื้องหลังจริงระหว่างผู้ใช้รอคำตอบ (แบบ "Percolating…")

เจ้าของโปรเจกต์: ระหว่างรอ อยากเห็นว่าระบบกำลังทำอะไรจริง เรียกส่วนไหนก็ขึ้นส่วนนั้น
แต่ในเนื้อแชทไม่มีศัพท์ยาก — สถานะโชว์เฉพาะในฟองรอ แล้วหายไปเมื่อคำตอบมา

ทำงานอย่างไร:
- เบราว์เซอร์สร้างเลขคำขอ (rid) ส่งมากับข้อความ
- /run ตั้ง rid ของเธรดนั้น แล้วเรียก mark("risk") ฯลฯ ตรงขั้นที่ทำจริง
- เบราว์เซอร์ถาม /api/progress/<rid> ทุก ~0.4 วินาที ได้ขั้นที่ผ่านมาแล้ว
ไม่เก็บข้อความของผู้ใช้ · เก็บในหน่วยความจำ ลบเองหลัง 2 นาที · พลาดแล้วงานหลักต้องไม่ล้ม
"""
from __future__ import annotations

import re
import threading
import time

STAGES = ("receive", "risk", "numbers", "people", "options", "ai", "safety")
KEEP_SECONDS = 120
MAX_REQUESTS = 2000
_RID = re.compile(r"^[a-z0-9]{8,32}$")
_lock = threading.Lock()
_runs: dict[str, dict] = {}
_local = threading.local()


def valid(rid) -> bool:
    return isinstance(rid, str) and bool(_RID.match(rid))


def _sweep(now: float) -> None:
    old = [k for k, v in _runs.items() if now - v["t0"] > KEEP_SECONDS]
    for k in old:
        _runs.pop(k, None)
    if len(_runs) > MAX_REQUESTS:                      # กันหน่วยความจำโตจากคำขอปลอมจำนวนมาก
        for k in sorted(_runs, key=lambda k: _runs[k]["t0"])[: len(_runs) - MAX_REQUESTS]:
            _runs.pop(k, None)


def begin(rid) -> None:
    """ผูก rid กับเธรดที่กำลังตอบข้อความนี้ — rid ไม่ถูกรูปแบบ = ไม่ติดตาม (ไม่มีผลกับคำตอบ)"""
    _local.rid = rid if valid(rid) else None
    if not _local.rid:
        return
    now = time.time()
    with _lock:
        _sweep(now)
        _runs[rid] = {"t0": now, "stages": [], "done": False}
    mark("receive")


def mark(stage: str) -> None:
    rid = getattr(_local, "rid", None)
    if not rid or stage not in STAGES:
        return
    with _lock:
        r = _runs.get(rid)
        if r and (not r["stages"] or r["stages"][-1][0] != stage):
            r["stages"].append((stage, round(time.time() - r["t0"], 2)))


def end() -> None:
    rid = getattr(_local, "rid", None)
    _local.rid = None
    if not rid:
        return
    with _lock:
        r = _runs.get(rid)
        if r:
            r["done"] = True


def read(rid) -> dict:
    if not valid(rid):
        return {"stages": [], "done": False}
    with _lock:
        r = _runs.get(rid)
        if not r:
            return {"stages": [], "done": False}
        return {"stages": [{"stage": s, "at": t} for s, t in r["stages"]], "done": r["done"]}
