"""
core/dependency_cycle.py — KING DIADEM
Dependency Cycle Engine — Water Flow Model
น้ำไหลลงเสมอ — ถ้าไม่เติม waterline จะหาย
DriftZero Principle: 0.1% drift/day without intervention
"""

import time

DECAY_RATE = 0.999   # 0.1% drift per day
FLOOR      = 0.01    # ไม่เคยเป็นศูนย์ — ยังมีทางอยู่เสมอ
WATERLINE  = 30.0    # ต่ำกว่านี้ = LYLA ต้องแทรกแซง
COLLAPSE_LINE = 10.0 # ต่ำกว่านี้ = critical

# intervention ช่วยเพิ่ม resource ได้เท่าไร
INTERVENTION_BOOST = {
    "seek_help":    {"resource": +15, "stability": +5},
    "reduce_burn":  {"resource": +8,  "entropy":   -5},
    "community":    {"resource": +12, "stability": +8},
    "rest":         {"stability":+10, "entropy":   -8},
}


def dependent_cycle(state: dict, intervention: str = None) -> dict:
    """
    จำลอง 1 cycle ของ resource drift
    - ถ้ามี intervention → boost ก่อน decay
    - คืน: next_state + warnings + LYLA signal
    """
    if not isinstance(state, dict):
        return {"error": "invalid state", "floor_breached": True}

    working = {k: float(v) if isinstance(v, (int, float)) else v
               for k, v in state.items()}

    # apply intervention ก่อน
    if intervention and intervention in INTERVENTION_BOOST:
        boost = INTERVENTION_BOOST[intervention]
        for k, delta in boost.items():
            if k in working and isinstance(working[k], float):
                working[k] = max(FLOOR, min(100.0, working[k] + delta))

    # decay
    next_state = {}
    warnings   = []

    # น้ำไหลลงเสมอ: ทรัพยากร/เสถียรภาพ "ลด" 0.1% ต่อรอบ ส่วน entropy "เพิ่ม" 0.1%
    # เดิมลดทุกค่าเท่ากันรวมทั้ง entropy (ระบบดีขึ้นเองโดยไม่มีใครทำอะไร) และลด choices
    # จนเป็นเศษ 0.01 — จำนวนทางเลือกเป็นจำนวนนับ ไม่ไหลตามเวลา
    _RISING = ("entropy", "drift")
    _COUNTS = ("choices", "choice_count")
    for key, value in working.items():
        if isinstance(value, float) and key not in _COUNTS:
            if key in _RISING:
                next_state[key] = round(min(100.0, value / DECAY_RATE), 3)
                continue
            decayed = max(FLOOR, value * DECAY_RATE)
            next_state[key] = round(decayed, 3)

            if decayed < COLLAPSE_LINE:
                warnings.append(f"⚠ CRITICAL: {key} = {decayed:.1f} — ต่ำกว่า collapse line")
            elif decayed < WATERLINE:
                warnings.append(f"⚠ {key} = {decayed:.1f} — ใกล้ waterline")
        elif key in _COUNTS:
            next_state[key] = int(value) if isinstance(value, float) else value
            if isinstance(value, (int, float)) and value < 1:
                warnings.append(f"⚠ CRITICAL: {key} = {int(value)} — Choice(t) < 1")
        else:
            next_state[key] = value

    _levels = [v for k, v in next_state.items()
               if isinstance(v, float) and k not in _RISING and k not in _COUNTS]
    _no_choice = any(isinstance(next_state.get(k), (int, float)) and next_state[k] < 1 for k in _COUNTS if k in next_state)
    floor_breached  = any(v < COLLAPSE_LINE for v in _levels) or _no_choice
    below_waterline = any(v < WATERLINE for v in _levels) or floor_breached

    # LYLA signal
    if floor_breached:
        lyla_signal = "CRITICAL — แทรกแซงทันที"
        action      = "emergency_stabilize"
    elif below_waterline:
        lyla_signal = "INTERVENE — waterline ต่ำ"
        action      = "seek_help"
    else:
        lyla_signal = "MONITOR — ระบบยังเสถียร"
        action      = "maintain"

    return {
        "state":          next_state,
        "warnings":       warnings,
        "floor_breached": floor_breached,
        "below_waterline":below_waterline,
        "decay_rate":     "0.1%/day",
        "intervention":   intervention,
        "lyla_signal":    lyla_signal,
        "recommended_action": action,
        "metaphor":       "น้ำไหลลงเสมอ — ถ้าไม่เติม waterline จะหาย",
        "fate_principle": "Choice(t) ≥ 1 → collapse = False",
    }


def simulate_days(initial_state: dict, days: int = 30,
                  interventions: dict = None) -> list:
    """
    จำลอง n วัน พร้อม optional interventions
    interventions = {day_number: "intervention_name"}
    """
    days = max(1, min(days, 365))
    interventions = interventions or {}

    history = [{"day": 0, "state": initial_state.copy(),
                "floor_breached": False, "event": "initial"}]
    current = initial_state.copy()

    for d in range(1, days + 1):
        iv = interventions.get(d)
        result = dependent_cycle(current, intervention=iv)
        current = result["state"]

        history.append({
            "day":            d,
            "state":          current,
            "floor_breached": result["floor_breached"],
            "lyla_signal":    result["lyla_signal"],
            "event":          iv or "natural_drift",
            "warnings":       result["warnings"],
        })

        if result["floor_breached"]:
            history.append({
                "day": d, "event": "COLLAPSE_STOPPED",
                "message": "จำลองหยุดเพราะระบบถึง collapse line"
            })
            break

    return history


def drift_forecast(state: dict, days: int = 90) -> dict:
    """
    คาดการณ์สถานะใน N วัน โดยไม่มี intervention
    """
    history = simulate_days(state, days)
    final   = history[-1]
    collapsed = any(h.get("floor_breached") for h in history)
    collapse_day = next(
        (h["day"] for h in history if h.get("floor_breached")), None
    )

    return {
        "forecast_days":  days,
        "final_state":    final.get("state", {}),
        "collapsed":      collapsed,
        "collapse_day":   collapse_day,
        "survival_days":  collapse_day or days,
        "recommendation": (
            "ต้องการ intervention ภายใน 7 วัน" if collapse_day and collapse_day < 7
            else "ยังพอมีเวลา — วางแผน intervention ได้"
        ),
    }
