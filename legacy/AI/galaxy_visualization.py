# AI/galaxy_visualization.py — KING DIADEM
# FATE™ Axiom compliance: Determinism — ใช้ hash แทน random
# ตำแหน่ง node คงที่ต่อ question เดิม — ไม่กระโดดทุก render
# Fail less. Harm less. Restore more.

import hashlib
import time

_ROUTE_COLOR = {
    "survival": "#ff4444",
    "collapse": "#ff0000",
    "risk":     "#ff9900",
    "vega":     "#3a86f5",
    "civil":    "#44bb88",
    "general":  "#c8a440",
}
_ROUTE_WEIGHT = {"collapse": 3.0, "survival": 2.5, "risk": 2.0, "vega": 1.8, "general": 1.0}


def _stable_coord(seed: str, lo: float, hi: float) -> float:
    """string → float [lo,hi] deterministic via sha256"""
    h = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16)
    return round(lo + (h / 0xFFFFFFFF) * (hi - lo), 4)


def galaxy_nodes(limit: int = 80) -> list[dict]:
    """
    สร้าง galaxy visualization nodes จาก decision memory
    x/y คงที่ต่อ question เดิม — deterministic hash
    size ∝ จำนวน options × route weight

    Returns: list of node dicts
    """
    try:
        from AI.decision_memory import get_memory
        data = get_memory()
    except Exception:
        return []

    if not data:
        return []

    try:
        limit = max(1, int(limit))
    except (TypeError, ValueError):
        limit = 80
    nodes = []
    for i, d in enumerate(data[-limit:] if len(data) > limit else data):
        if not isinstance(d, dict):
            continue

        question = str(d.get("question", f"node_{i}"))[:80]
        options  = d.get("options", [])
        route    = str(d.get("route", "general"))
        seed     = question + route

        weight = _ROUTE_WEIGHT.get(route, 1.0)
        size   = round((len(options) + 1) * weight, 2)

        nodes.append({
            "x":          _stable_coord(seed + "_x", -100, 100),
            "y":          _stable_coord(seed + "_y", -100, 100),
            "size":       size,
            # memory รวมทุกผู้ใช้ — ไม่ใช้ข้อความคำถามเป็น label (ตำแหน่งยังคงที่ด้วย hash)
            "label":      f"{route}#{i + 1}",
            "route":      route,
            "color":      _ROUTE_COLOR.get(route, "#888888"),
            "options":    len(options),
            "fate_note":  "HIGH_PRESSURE" if size >= 6 else "NORMAL",
        })

    # เรียง size ใหญ่ก่อน — core nodes อยู่ศูนย์กลาง
    nodes.sort(key=lambda x: x["size"], reverse=True)
    return nodes


def galaxy_summary() -> dict:
    nodes = galaxy_nodes()
    if not nodes:
        return {"total": 0, "routes": [], "computed_at": int(time.time())}
    return {
        "total":      len(nodes),
        "routes":     list({n["route"] for n in nodes}),
        "max_size":   nodes[0]["size"] if nodes else 0,
        "computed_at": int(time.time()),
    }
