# AI/civilization_engine.py — KING DIADEM
# FATE™ Axiom compliance: Explainability=100% · Downside First
# Fail less. Harm less. Restore more.

import time
from collections import deque

_nodes: deque[dict] = deque(maxlen=500)

_VALID_TYPES = {"decision", "signal", "learning", "feedback", "event", "council"}


def add_node(node: dict) -> dict:
    """
    เพิ่ม node เข้า civilization graph
    validate ก่อน — ไม่รับ node ว่าง

    Returns: node ที่เพิ่ม (พร้อม id + timestamp)
    """
    if not isinstance(node, dict) or not node:
        return {"error": "FATE_VIOLATION: node must be non-empty dict"}

    enriched = {
        "id":          len(_nodes) + 1,
        "recorded_at": int(time.time()),
        "node_type":   node.get("type", "event"),
        **node,
    }

    if enriched["node_type"] not in _VALID_TYPES:
        enriched["node_type"] = "event"

    _nodes.append(enriched)
    return enriched


def get_nodes(limit: int = 100) -> list[dict]:
    """คืน nodes ล่าสุด N รายการ"""
    return list(_nodes)[-limit:]


def node_summary() -> dict:
    """สรุปภาพรวม civilization graph"""
    all_nodes = list(_nodes)
    total     = len(all_nodes)
    if total == 0:
        return {"total": 0, "by_type": {}, "fate_note": "NO_DATA"}

    by_type: dict[str, int] = {}
    for n in all_nodes:
        t = n.get("node_type", "event")
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total":      total,
        "by_type":    by_type,
        "latest_id":  all_nodes[-1]["id"] if all_nodes else 0,
        "fate_note":  "ACTIVE" if total > 0 else "EMPTY",
        "computed_at": int(time.time()),
    }
