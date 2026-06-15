# ENGINE/human_engine.py
# KING DIADEM — Human Analysis Engine (Entropy-aware) v2.0
# วิเคราะห์สถานะมนุษย์จริง -> แปลงเป็น entropy/resource/stability/risk_score
# เพื่อให้ analyze_pattern() / emptiness_guard ใช้ค่าจริง
# แทน default คงที่ 40/50/60 (ต้นเหตุของ RISK 45 ซ้ำทุกครั้ง)

from ENGINE.realhuman_survivorengine import (
    RealHumanSurvivorEngine,
    parse_state_from_context,
)

_survivor = RealHumanSurvivorEngine()


def analyze_human(context: dict) -> dict:
    """
    context: dict จาก frontend เช่น
      {energy, money, food_access, safe_place, mental_state,
       time_available, sleep_hours, days_in_crisis}

    คืนค่า dict ที่มี entropy/resource/stability/risk_score
    บวกข้อมูลจาก RealHumanSurvivorEngine (status, priority,
    can_decide, flags, context_for_lyla, waterline)
    """
    if not isinstance(context, dict):
        context = {}

    state = parse_state_from_context(context)
    out   = _survivor.run(state)

    waterline = out.waterline  # 0-100, 100 = ปลอดภัยสุด

    # ── แปลง waterline -> entropy / resource / stability ──
    entropy   = max(0.0, min(100.0, 100.0 - waterline))
    resource  = max(0.0, min(100.0, waterline))
    stability = max(0.0, min(100.0, waterline))

    # risk_score แบบเดียวกับ emptiness_guard
    # (entropy * 0.5 + (100 - resource) * 0.5)
    risk_score = entropy * 0.5 + (100.0 - resource) * 0.5

    return {
        "status":           out.status,
        "priority":         out.priority,
        "can_decide":       out.can_decide,
        "flags":            out.flags,
        "context_for_lyla": out.context_for_lyla,
        "waterline":        waterline,
        "entropy":          entropy,
        "resource":         resource,
        "stability":        stability,
        "risk_score":       risk_score,
        "human_state":      state.mental_state,
    }
