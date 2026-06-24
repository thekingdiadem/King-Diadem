# AI/strategic_memory.py
# KING DIADEM — Strategic Memory Graph
# FATE™ Axiom compliance: Determinism · Explainability=100% · Downside First
# Fail less. Harm less. Restore more.

import time
from typing import Optional

# ── MEMORY STORE ──────────────────────────────────────────────────
# key = normalized question string
# value = full pattern record

memory_graph: dict[str, dict] = {}

_MAX_DECISIONS_PER_KEY = 50   # ป้องกัน unbounded growth


def _normalize(question: str) -> str:
    """Normalize key — lowercase + strip — deterministic"""
    return question.lower().strip()


def record_pattern(
    question: str,
    decision: str,
    planet: Optional[dict] = None,
    outcome: Optional[bool] = None,
) -> dict:
    """
    บันทึก pattern การตัดสินใจ พร้อม timestamp + outcome tracking

    Args:
        question: คำถาม / สถานการณ์
        decision: การตัดสินใจที่เลือก
        planet:   planetary context dict (optional)
        outcome:  True=success, False=fail, None=pending

    Returns:
        entry ที่เพิ่ง record
    """
    if not question.strip():
        return {"error": "FATE_VIOLATION: question empty"}

    key = _normalize(question)

    if key not in memory_graph:
        memory_graph[key] = {
            "question_raw": question.strip(),
            "count":        0,
            "decisions":    [],
            "planetary":    [],
            "outcomes":     [],
            "first_seen":   int(time.time()),
            "last_seen":    int(time.time()),
        }

    node = memory_graph[key]

    # cap เพื่อป้องกัน memory leak
    if len(node["decisions"]) >= _MAX_DECISIONS_PER_KEY:
        node["decisions"].pop(0)
        node["planetary"].pop(0)
        node["outcomes"].pop(0)

    entry = {
        "decision":    decision.strip() or "ไม่ระบุ",
        "planet":      planet or {},
        "outcome":     outcome,
        "recorded_at": int(time.time()),
    }

    node["count"]     += 1
    node["last_seen"]  = int(time.time())
    node["decisions"].append(entry["decision"])
    node["planetary"].append(entry["planet"])
    node["outcomes"].append(outcome)

    return entry


def get_patterns() -> dict:
    """Return full memory graph"""
    return dict(memory_graph)


def pattern_summary() -> dict:
    """
    สรุปแต่ละ pattern: count + success_rate + most_common_decision
    """
    summary = {}
    for key, node in memory_graph.items():
        outcomes  = [o for o in node["outcomes"] if o is not None]
        successes = sum(1 for o in outcomes if o is True)
        success_rate = round(successes / len(outcomes) * 100, 1) if outcomes else None

        decisions = node["decisions"]
        most_common = max(set(decisions), key=decisions.count) if decisions else "—"

        summary[key] = {
            "count":             node["count"],
            "most_common":       most_common,
            "success_rate":      success_rate,
            "outcomes_recorded": len(outcomes),
            "last_seen":         node["last_seen"],
            "fate_signal": (
                "STABLE"        if success_rate is not None and success_rate >= 60
                else "DRIFT"    if success_rate is not None
                else "PENDING"
            ),
        }

    return summary


def get_pattern(question: str) -> Optional[dict]:
    """ดึง pattern สำหรับ question เดียว"""
    key = _normalize(question)
    return memory_graph.get(key)


def clear_memory() -> dict:
    """Clear all — ใช้ระวัง irreversible"""
    count = len(memory_graph)
    memory_graph.clear()
    return {"cleared": count, "fate_note": "WARN: irreversible — memory cleared"}
