# AI/global_decision_map.py — KING DIADEM
# FATE™ Axiom compliance: Determinism · Explainability=100%
# Fail less. Harm less. Restore more.

import time

_ROUTE_WEIGHT = {"collapse": 3.0, "survival": 2.5, "risk": 2.0, "vega": 1.8, "general": 1.0}


def decision_map(limit: int = 100) -> list[dict]:
    """
    สร้าง decision map nodes จาก memory
    pressure = len(options) × route_weight — deterministic, ไม่ใช้ random

    Returns: list of nodes เรียง pressure สูง→ต่ำ
    """
    try:
        from AI.decision_memory import get_memory
        data = get_memory()
    except Exception:
        return []

    if not data:
        return []

    nodes = []
    for d in (data[-limit:] if len(data) > limit else data):
        if not isinstance(d, dict):
            continue

        options  = d.get("options", [])
        route    = str(d.get("route", "general"))
        question = str(d.get("question", ""))[:80]
        weight   = _ROUTE_WEIGHT.get(route, 1.0)
        pressure = round(len(options) * weight, 2)

        nodes.append({
            "question":    question,
            "pressure":    pressure,
            "option_count": len(options),
            "route":       route,
            "fate_signal": "HIGH_PRESSURE" if pressure >= 6 else "NORMAL",
        })

    nodes.sort(key=lambda x: x["pressure"], reverse=True)
    return nodes


def map_summary() -> dict:
    """สรุป decision map สำหรับ dashboard"""
    nodes = decision_map()
    if not nodes:
        return {"total": 0, "max_pressure": 0, "high_pressure_count": 0}

    high = [n for n in nodes if n["pressure"] >= 6]
    return {
        "total":               len(nodes),
        "max_pressure":        nodes[0]["pressure"],
        "avg_pressure":        round(sum(n["pressure"] for n in nodes) / len(nodes), 2),
        "high_pressure_count": len(high),
        "top_routes":          list({n["route"] for n in nodes[:10]}),
        "computed_at":         int(time.time()),
    }
