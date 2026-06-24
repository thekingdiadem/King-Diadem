# AI/reality_feedback.py — KING DIADEM
# FATE™ Axiom compliance: Determinism · Explainability=100% · Downside First
# Fail less. Harm less. Restore more.

from __future__ import annotations
import time
from collections import deque

_STORE: deque[dict] = deque(maxlen=500)   # cap ป้องกัน unbounded growth

_VALID_OUTCOMES = {"success", "fail", "partial", "unknown"}


def record_feedback(
    problem: str,
    option: str,
    success: bool | str,
    *,
    route: str = "general",
    note: str = "",
) -> dict:
    """
    บันทึก feedback จากผู้ใช้หลัง decision

    Args:
        problem: สถานการณ์ที่ตัดสินใจ
        option:  ทางเลือกที่เลือก
        success: bool หรือ "success"/"fail"/"partial"/"unknown"
        route:   active route
        note:    หมายเหตุเพิ่มเติม (optional)

    Returns: entry dict ที่เพิ่งบันทึก
    """
    if not problem.strip():
        return {"error": "FATE_VIOLATION: problem empty"}

    # normalize success → outcome string
    if isinstance(success, bool):
        outcome = "success" if success else "fail"
    elif str(success).lower() in _VALID_OUTCOMES:
        outcome = str(success).lower()
    else:
        outcome = "unknown"

    entry = {
        "problem":     str(problem).strip()[:300],
        "option":      str(option).strip()[:300] or "ไม่ระบุ",
        "outcome":     outcome,
        "route":       route,
        "note":        str(note).strip()[:200],
        "recorded_at": int(time.time()),
        "fate_audit": {
            "outcome_known": outcome != "unknown",
            "has_option":    bool(str(option).strip()),
        },
    }
    _STORE.append(entry)
    return entry


def feedback_stats() -> dict:
    """
    สถิติ feedback ทั้งหมด — breakdown per outcome + per route
    """
    total   = len(_STORE)
    entries = list(_STORE)

    if total == 0:
        return {
            "success_rate": 0.0,
            "samples":      0,
            "signal":       "NO_DATA",
            "breakdown":    {},
            "top_routes":   [],
        }

    # outcome breakdown
    breakdown: dict[str, int] = {}
    for e in entries:
        breakdown[e["outcome"]] = breakdown.get(e["outcome"], 0) + 1

    success_count  = breakdown.get("success", 0)
    partial_count  = breakdown.get("partial", 0)
    fail_count     = breakdown.get("fail",    0)

    # partial นับเป็น 0.5
    effective_success = success_count + partial_count * 0.5
    success_rate      = round(effective_success / total, 3)

    # FATE™ signal
    if success_rate >= 0.70:
        signal = "STABLE"
    elif success_rate >= 0.50:
        signal = "CAUTION"
    elif fail_count / total > 0.5:
        signal = "DRIFT_ALERT"
    else:
        signal = "COMPRESSION"

    # per-route breakdown
    route_map: dict[str, dict[str, int]] = {}
    for e in entries:
        r = e["route"]
        if r not in route_map:
            route_map[r] = {"success": 0, "fail": 0, "total": 0}
        route_map[r]["total"] += 1
        if e["outcome"] == "success":
            route_map[r]["success"] += 1
        elif e["outcome"] == "fail":
            route_map[r]["fail"] += 1

    top_routes = sorted(
        [{
            "route":        r,
            "total":        v["total"],
            "success_rate": round(v["success"] / v["total"], 2) if v["total"] else 0,
        } for r, v in route_map.items()],
        key=lambda x: -x["success_rate"]
    )[:5]

    return {
        "success_rate": success_rate,
        "samples":      total,
        "signal":       signal,
        "breakdown":    breakdown,
        "top_routes":   top_routes,
    }


def get_recent(limit: int = 20) -> list[dict]:
    """คืน feedback ล่าสุด N รายการ"""
    return list(_STORE)[-limit:]
