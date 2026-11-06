"""บันทึกการตัดสินใจแบบเขียนต่อท้ายอย่างเดียว + ร้อยด้วย hash (Decision Audit Trail)

ตอบข้อ 8 ของ Compliance Mapping (ISO/IEC 42001 A.6.2.8 · EU AI Act Art. 12/19):
- เขียนต่อท้ายอย่างเดียว ไฟล์ละเดือน `audit-YYYY-MM.jsonl` อยู่ข้าง DB_PATH (ดิสก์ถาวรบน Render)
- แต่ละบรรทัดมี `prev` = hash ของบรรทัดก่อนหน้า และ `h` = sha256(prev + เนื้อบรรทัด)
  ถ้ามีคนแก้หรือลบบรรทัดกลางไฟล์ `verify()` จะบอกบรรทัดแรกที่โซ่ขาด
- ไม่เก็บข้อความของผู้ใช้หรืออีเมล — เก็บเฉพาะเส้นทาง แหล่งคำตอบ คะแนนความเสี่ยง และหัวข้อ
- ไม่ลบไฟล์เอง: ระยะเก็บขั้นต่ำ 6 เดือน (RETENTION_MONTHS) — `prunable()` แค่บอกว่าไฟล์ไหนเก่าพอจะย้ายไปเก็บถาวรได้
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import threading
import time

from core.paths import data_dir

RETENTION_MONTHS = 6
GENESIS = "0" * 64
_ALLOWED = ("route", "source", "W", "risk", "topics", "kind", "model", "rule")
_lock = threading.Lock()
_last: dict[str, str] = {}          # ไฟล์ → hash ล่าสุด (ไม่ต้องอ่านไฟล์ทั้งไฟล์ทุกครั้ง)


def _file(ts: float | None = None, root: str | None = None) -> str:
    return os.path.join(root or data_dir(), time.strftime("audit-%Y-%m.jsonl", time.gmtime(ts or time.time())))


def _digest(prev: str, body: dict) -> str:
    raw = prev + json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _tail_hash(path: str) -> str:
    if path in _last:
        return _last[path]
    h = GENESIS
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    h = json.loads(line).get("h", h)
    except (OSError, ValueError):
        pass
    return h


def record(event: dict, root: str | None = None) -> dict:
    """เพิ่ม 1 บรรทัด — รับเฉพาะฟิลด์ที่อนุญาต (กันข้อความผู้ใช้หลุดเข้ามาโดยไม่ตั้งใจ)"""
    body = {k: event[k] for k in _ALLOWED if k in event}
    if isinstance(body.get("topics"), list):
        body["topics"] = [str(t)[:40] for t in body["topics"][:5]]
    body["t"] = int(time.time())
    path = _file(body["t"], root)
    with _lock:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        prev = _tail_hash(path)
        body["prev"] = prev
        body["h"] = _digest(prev, {k: v for k, v in body.items() if k != "h"})
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(body, ensure_ascii=False, sort_keys=True) + "\n")
        _last[path] = body["h"]
    return body


def verify(path: str) -> dict:
    """ตรวจโซ่ทั้งไฟล์ → {"ok", "rows", "broken_at"} · broken_at = เลขบรรทัดแรกที่ถูกแก้/ลบ/สลับ"""
    prev, n = GENESIS, 0
    try:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate((l for l in f if l.strip()), 1):
                row = json.loads(line)
                h = row.pop("h", "")
                if row.get("prev") != prev or _digest(prev, row) != h:
                    return {"ok": False, "rows": n, "broken_at": n}
                prev = h
    except (OSError, ValueError):
        return {"ok": False, "rows": n, "broken_at": n + 1}
    return {"ok": True, "rows": n, "broken_at": None}


def status(root: str | None = None) -> dict:
    """สรุปสำหรับ /health หรือผู้ตรวจ: ไฟล์ จำนวนบรรทัด และโซ่ครบหรือไม่ (ไม่คืนเนื้อหา)"""
    files = sorted(glob.glob(os.path.join(root or data_dir(), "audit-*.jsonl")))
    out = [{"file": os.path.basename(p), **verify(p)} for p in files]
    return {"retention_months": RETENTION_MONTHS, "files": out, "ok": all(f["ok"] for f in out)}


def prunable(root: str | None = None, now: float | None = None) -> list[str]:
    """ไฟล์ที่เก่ากว่าระยะเก็บขั้นต่ำ — ระบบไม่ลบเอง ให้คนย้ายไปเก็บถาวรก่อน"""
    t = time.gmtime(now or time.time())
    cutoff = (t.tm_year * 12 + t.tm_mon - 1) - RETENTION_MONTHS
    keep = []
    for p in sorted(glob.glob(os.path.join(root or data_dir(), "audit-*.jsonl"))):
        y, m = os.path.basename(p)[6:13].split("-")
        if int(y) * 12 + int(m) - 1 < cutoff:
            keep.append(os.path.basename(p))
    return keep
