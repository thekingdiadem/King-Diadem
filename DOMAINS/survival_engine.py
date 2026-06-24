# DOMAINS/survival_engine.py
# KING DIADEM — Survival Domain Engine
# เชื่อมกับ ENGINE/realhuman_survivorengine.py จริง
# ไม่มี random — entropy คำนวณจาก state จริง

import time

try:
    from ENGINE.realhuman_survivorengine import (
        RealHumanSurvivorEngine,
        parse_state_from_context,
    )
    _engine = RealHumanSurvivorEngine()
    _REAL_ENGINE = True
except Exception:
    _engine = None
    _REAL_ENGINE = False


def analyze_survival(context: dict) -> dict:

    # ── ถ้า RealHumanSurvivorEngine โหลดได้ ──────────────────────
    if _REAL_ENGINE and _engine:
        state  = parse_state_from_context(context)
        output = _engine.run(state)

        return {
            "domain":           "survival",
            "timestamp":        time.time(),
            "status":           output.status,
            "priority":         output.priority,
            "waterline":        round(output.waterline, 1),
            "can_decide":       output.can_decide,
            "flags":            output.flags,
            "context_for_lyla": output.context_for_lyla,
            "recommended_path": _status_to_path(output.status),
            "input":            context,
        }

    # ── Fallback: deterministic จาก context ──────────────────────
    energy   = float(context.get("energy",   50))
    stress   = float(context.get("stress",   50))
    sleep    = float(context.get("sleep_hours", 6))
    money    = float(context.get("money",    0))
    food     = bool(context.get("food_access", True))
    shelter  = bool(context.get("safe_place",  True))

    # entropy = ความไม่แน่นอน/ความเสื่อม
    entropy = (stress * 0.5) + ((100 - energy) * 0.3) + (max(0, 6 - sleep) * 3.3)
    if not food:    entropy += 25
    if not shelter: entropy += 35
    if money <= 0:  entropy += 10
    entropy = min(100.0, entropy)

    stability = max(0.0, 100.0 - entropy)
    survival_score = stability - (entropy * 0.3)

    if survival_score > 55:
        path = "stable_survival"
    elif survival_score > 30:
        path = "adapt"
    else:
        path = "critical_risk"

    return {
        "domain":           "survival",
        "timestamp":        time.time(),
        "entropy":          round(entropy, 1),
        "stability":        round(stability, 1),
        "survival_score":   round(survival_score, 1),
        "waterline":        round(stability, 1),
        "recommended_path": path,
        "can_decide":       entropy < 60,
        "input":            context,
    }


def _status_to_path(status: str) -> str:
    mapping = {
        "STABLE":              "stable_survival",
        "STRESSED_FUNCTIONAL": "adapt",
        "LOW_ENERGY":          "recover_first",
        "CRITICAL_NO_FOOD":    "find_food_now",
        "CRITICAL_NO_SHELTER": "find_shelter_now",
        "RESET_REQUIRED":      "critical_risk",
    }
    return mapping.get(status, "adapt")
