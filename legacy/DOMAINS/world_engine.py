# DOMAINS/world_engine.py
# KING DIADEM — World Domain Engine
# ใช้ข้อมูลจริง ไม่มี random — volatility คำนวณจาก input จริง

import time


def _num(v, d: float) -> float:
    """ตัวเลขจาก context — ค่าเสีย/NaN/inf → ค่าเริ่มต้น"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x and abs(x) != float("inf") else d


def analyze_world(context: dict) -> dict:
    context = context if isinstance(context, dict) else {}
    # ── รับ world signals จาก context ────────────────────────────
    food_security   = _num(context.get("food_security"), 0.6)  # 0-1 (1 = มั่นคง)
    energy_price    = _num(context.get("energy_price"), 0.5)  # 0-1 (1 = แพงมาก)
    political_risk  = _num(context.get("political_risk"), 0.4)  # 0-1
    climate_stress  = _num(context.get("climate_stress"), 0.4)  # 0-1
    supply_chain    = _num(context.get("supply_chain"), 0.6)  # 0-1 (1 = ดี)
    conflict_level  = _num(context.get("conflict_level"), 0.3)  # 0-1

    # ── Volatility score (deterministic) ─────────────────────────
    # ปัจจัยที่เพิ่ม volatility
    volatility = (
        (1 - food_security) * 0.25 +
        energy_price        * 0.20 +
        political_risk      * 0.20 +
        climate_stress      * 0.15 +
        (1 - supply_chain)  * 0.10 +
        conflict_level      * 0.10
    )
    volatility = max(0.0, min(1.0, volatility))

    # ── Choice collapse index ─────────────────────────────────────
    # เมื่อ resource หายาก → ทางเลือกของมนุษย์ลดลง (FATE Axiom)
    choice_index = max(0.0, 1.0 - volatility)

    # ── Trend ─────────────────────────────────────────────────────
    if volatility < 0.30:
        trend        = "stable_cycle"
        lyla_signal  = "ระบบโลกเสถียร — วางแผนระยะยาวได้"
    elif volatility < 0.55:
        trend        = "moderate_stress"
        lyla_signal  = "ความผันผวนปานกลาง — เน้น flexibility"
    elif volatility < 0.75:
        trend        = "high_instability"
        lyla_signal  = "ความไม่แน่นอนสูง — ลดการผูกมัดระยะยาว"
    else:
        trend        = "systemic_collapse_risk"
        lyla_signal  = "วิกฤตระดับระบบ — เน้น survival ก่อน"

    # ── DriftZero waterline ───────────────────────────────────────
    waterline = round(choice_index * 100, 1)

    return {
        "domain":           "world",
        "timestamp":        time.time(),
        "global_volatility": round(volatility, 3),
        "choice_index":     round(choice_index, 3),
        "waterline":        waterline,
        "trend":            trend,
        "lyla_signal":      lyla_signal,
        "drift_risk":       "HIGH" if volatility > 0.65 else "MODERATE" if volatility > 0.40 else "LOW",
        "factors": {
            "food_security":  food_security,
            "energy_price":   energy_price,
            "political_risk": political_risk,
            "climate_stress": climate_stress,
            "supply_chain":   supply_chain,
            "conflict_level": conflict_level,
        },
        "input": context,
    }
