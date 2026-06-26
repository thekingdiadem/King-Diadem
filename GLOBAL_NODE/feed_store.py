# GLOBAL_NODE/feed_store.py
# KING DIADEM™ — Global Feed Store
# Article 3: Every decision leaves a traceable record.
# Article 6: Bounded memory — no unbounded growth allowed.

import threading
import time
from collections import deque
from typing import Optional

# ── Constants ────────────────────────────────────────────────────
FEED_MAX_SIZE  = 1000
FEED_FETCH_CAP = 50

# ── State ─────────────────────────────────────────────────────────
_feed: deque = deque(maxlen=FEED_MAX_SIZE)
_lock = threading.Lock()


# ── Core API ──────────────────────────────────────────────────────
def add_feed_entry(source: str, decision: dict, route: Optional[str] = None) -> None:
    """
    บันทึก decision event เข้า feed
    - source  : ตัวเรียก เช่น "gateway", "eternal_snapshot", "consensus_engine"
    - decision: dict จาก engine ใดก็ได้
    - route   : GENERAL / RISK / SURVIVAL / COLLAPSE / CIVIL / VEGA (optional)

    Article 3 — ทุก decision ต้องมี trace ย้อนกลับได้
    """
    if not isinstance(decision, dict):
        decision = {"raw": str(decision)}

    entry = {
        "time":     time.time(),
        "source":   source or "unknown",
        "route":    route or decision.get("route", "GENERAL"),
        "decision": decision,
    }

    with _lock:
        _feed.append(entry)


def get_feed(limit: int = FEED_FETCH_CAP) -> list:
    """
    คืน feed ล่าสุด N รายการ
    Article 6 — bounded fetch ห้าม dump ทั้งหมด
    """
    limit = max(1, min(limit, FEED_FETCH_CAP))
    with _lock:
        return list(_feed)[-limit:]


def get_feed_by_route(route: str, limit: int = 20) -> list:
    """
    filter feed ตาม route — ใช้ใน /api/feed?route=RISK
    """
    with _lock:
        filtered = [e for e in _feed if e.get("route") == route]
    return filtered[-limit:]


def clear_feed() -> int:
    """
    ล้าง feed — ใช้ใน test / admin reset เท่านั้น
    คืนจำนวนรายการที่ถูกลบ
    """
    with _lock:
        count = len(_feed)
        _feed.clear()
    return count


def feed_stats() -> dict:
    """snapshot สถานะ feed สำหรับ /api/kernel_snapshot"""
    with _lock:
        total = len(_feed)
        routes: dict = {}
        for e in _feed:
            r = e.get("route", "GENERAL")
            routes[r] = routes.get(r, 0) + 1
    return {
        "total_entries": total,
        "by_route":      routes,
        "capacity":      FEED_MAX_SIZE,
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    clear_feed()
    add_feed_entry("test", {"action": "ping"}, route="GENERAL")
    add_feed_entry("test", {"action": "warn"}, route="RISK")
    feed = get_feed()
    assert len(feed) == 2, "feed count mismatch"
    assert feed[-1]["route"] == "RISK"
    by_route = get_feed_by_route("RISK")
    assert len(by_route) == 1
    stats = feed_stats()
    assert stats["total_entries"] == 2
    clear_feed()
    return {"status": "OK", "module": "feed_store"}


if __name__ == "__main__":
    print(_self_test())
