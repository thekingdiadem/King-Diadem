"""
AI/decision_heatmap.py — KING DIADEM
Heatmap ของ decision pressure จาก memory
ไม่ใช้ random.uniform แบบ naive — ใช้ hash จาก context เพื่อให้ตำแหน่งคงที่ต่อ decision เดิม
"""
import hashlib


def _stable_coord(seed: str, lo: float, hi: float) -> float:
    """แปลง string → float ในช่วง [lo, hi] แบบ deterministic"""
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    return round(lo + (h / 0xFFFFFFFF) * (hi - lo), 6)


def heatmap() -> list:
    """
    คืน list of nodes สำหรับ render heatmap
    แต่ละ node: lat, lon, pressure, label, route
    """
    try:
        from AI.decision_memory import get_memory
        memory = get_memory()
    except Exception:
        memory = []

    if not memory:
        return []

    map_data = []
    for i, m in enumerate(memory):
        if not isinstance(m, dict):
            continue

        options  = m.get("options", [])
        context  = str(m.get("context") or m.get("input") or f"decision_{i}")
        route    = str(m.get("route") or "general")
        label    = str(m.get("label") or context[:40])

        # pressure = จำนวน options × ความซับซ้อน route
        route_weight = {"collapse": 3, "survival": 2.5, "risk": 2, "vega": 1.8, "general": 1}
        pressure = len(options) * route_weight.get(route, 1)

        node = {
            "lat":      _stable_coord(context + "_lat", -90, 90),
            "lon":      _stable_coord(context + "_lon", -180, 180),
            "pressure": round(pressure, 2),
            "label":    label,
            "route":    route,
            "options":  len(options),
        }
        map_data.append(node)

    # เรียงตาม pressure สูง → ต่ำ
    map_data.sort(key=lambda x: x["pressure"], reverse=True)
    return map_data


def heatmap_summary() -> dict:
    """สรุปภาพรวม heatmap สำหรับ dashboard"""
    data = heatmap()
    if not data:
        return {"total": 0, "max_pressure": 0, "hotspots": []}

    hotspots = [n for n in data if n["pressure"] >= 4]
    return {
        "total":        len(data),
        "max_pressure": data[0]["pressure"] if data else 0,
        "avg_pressure": round(sum(n["pressure"] for n in data) / len(data), 2),
        "hotspots":     hotspots[:5],
        "routes":       list({n["route"] for n in data}),
    }
