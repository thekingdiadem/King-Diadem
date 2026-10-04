"""
AI/decision_memory.py — KING DIADEM
Decision memory: dedup + timestamp + search + persist-ready
"""

import itertools
import threading
import time

# หมายเหตุ: memory นี้รวมทุกผู้ใช้ในโปรเซส — ห้ามเปิด search/get ให้ client โดยตรง
_memory: list = []
_MAX = 200
_ids = itertools.count(1)        # เดิม len()+1 → id ซ้ำหลังตัดหัว (เกิน 200)
_lock = threading.Lock()


def store_decision(question: str, options: list, route: str = "general",
                   result: str = None, tags: list = None,
                   context: dict = None) -> dict:
    """
    บันทึกการตัดสินใจพร้อม metadata
    - dedup: ถ้า question เดิมเกิดใน 60s ล่าสุด ไม่บันทึกซ้ำ
    - คืน entry ที่บันทึก
    """
    question = str(question).strip()[:500]
    now = time.time()

    with _lock:
        # dedup — ป้องกัน question เดิมซ้ำในช่วง 60 วินาที
        if _memory:
            last = _memory[-1]
            if last["question"] == question and (now - last["timestamp"]) < 60:
                return last  # คืน entry เดิม ไม่บันทึกซ้ำ
        return _append(question, options, route, result, tags, context, now)


def _append(question, options, route, result, tags, context, now) -> dict:
    entry = {
        "id":        next(_ids),
        "timestamp": now,
        "question":  question,
        "options":   options if isinstance(options, list) else [str(options)],
        "route":     route,
        "result":    result,
        "tags":      tags if isinstance(tags, list) else [],
        "context":   context if isinstance(context, dict) else {},
    }
    _memory.append(entry)

    # trim เกิน max — เก็บ tail (ล่าสุด)
    if len(_memory) > _MAX:
        del _memory[0]

    return entry


def get_memory(limit: int = 50) -> list:
    """คืน n entries ล่าสุด"""
    try:
        limit = max(1, min(int(limit), _MAX))
    except (TypeError, ValueError):
        limit = 50
    return _memory[-limit:]


def get_by_id(entry_id: int) -> dict | None:
    """ค้นหาด้วย id"""
    for m in _memory:
        if m.get("id") == entry_id:
            return m
    return None


def search_memory(keyword: str, limit: int = 20) -> list:
    """ค้นหาจาก question, tags, หรือ result"""
    kw = str(keyword or "").lower().strip()
    if not kw:
        return get_memory(limit)

    results = [
        m for m in _memory
        if kw in m["question"].lower()
        or any(kw in str(t).lower() for t in m.get("tags", []))
        or kw in str(m.get("result", "")).lower()
        or kw in str(m.get("route", "")).lower()
    ]
    return results[-limit:]


def update_result(entry_id: int, result: str) -> bool:
    """อัปเดต result ของ entry ที่ตัดสินใจแล้ว"""
    for m in _memory:
        if m.get("id") == entry_id:
            m["result"] = result
            m["updated_at"] = time.time()
            return True
    return False


def clear_memory():
    """ล้าง memory ทั้งหมด"""
    _memory.clear()


def memory_stats() -> dict:
    if not _memory:
        return {"total": 0, "max": _MAX, "routes": {}, "oldest": None, "newest": None}

    return {
        "total":    len(_memory),
        "max":      _MAX,
        "usage_pct": round(len(_memory) / _MAX * 100, 1),
        "routes":   _count_routes(),
        "oldest":   _memory[0]["timestamp"],
        "newest":   _memory[-1]["timestamp"],
        "has_result": sum(1 for m in _memory if m.get("result")),
    }


def _count_routes() -> dict:
    counts: dict = {}
    for m in _memory:
        r = m.get("route", "general")
        counts[r] = counts.get(r, 0) + 1
    return counts
