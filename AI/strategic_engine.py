# AI/strategic_engine.py
# KING DIADEM — Strategic Analysis Engine
# FATE™ Axiom compliance: Downside First · Choice(t) ≥ 1 · Explainability=100%
# กฎ: Preserve life. Avoid harm. Seek cooperation before conflict.
# Fail less. Harm less. Restore more.

SAFETY_RULE = (
    "All strategies must preserve life and avoid harm. "
    "Forbidden: Violence, War, Harm to people, Harm to animals, "
    "Destruction of property, Environmental damage. "
    "Preferred: Cooperation, Stability, Survival, Restoration."
)

# ── RISK SCORING ──────────────────────────────────────────────────
# risk = danger-weighted pressure minus food buffer
# threshold ที่ใช้ตัดสิน route

_RISK_THRESHOLDS = {
    "CRITICAL": 12.0,
    "HIGH":      7.0,
    "MODERATE":  3.0,
    # ต่ำกว่า 3.0 = LOW
}


def _risk_label(risk: float) -> str:
    if risk >= _RISK_THRESHOLDS["CRITICAL"]: return "CRITICAL"
    if risk >= _RISK_THRESHOLDS["HIGH"]:     return "HIGH"
    if risk >= _RISK_THRESHOLDS["MODERATE"]: return "MODERATE"
    return "LOW"


def _route_from_risk(label: str) -> str:
    return {
        "CRITICAL": "collapse",
        "HIGH":     "survival",
        "MODERATE": "risk",
        "LOW":      "general",
    }.get(label, "general")


def strategic_analysis(
    location: str,
    food: float,
    money: float,
    danger: float,
    context: dict | None = None,
) -> dict:
    """
    วิเคราะห์สถานการณ์เชิงกลยุทธ์ — deterministic, Downside First

    Args:
        location: พื้นที่/บริบท
        food:     ระดับอาหาร (0–10, ต่ำ = วิกฤต)
        money:    ทรัพยากรเงิน (บาท/หน่วย)
        danger:   ระดับอันตราย (0–10, สูง = วิกฤต)
        context:  dict เพิ่มเติม (optional)

    Returns:
        risk_score, risk_level, route, options, principles, fate_audit
    """
    # clamp inputs
    food   = max(0.0, min(float(food),   10.0))
    money  = max(0.0, float(money))
    danger = max(0.0, min(float(danger), 10.0))

    risk        = round((danger * 2.0) - food, 2)
    risk_label  = _risk_label(risk)
    route       = _route_from_risk(risk_label)

    # ── OPTIONS — เรียง Downside First (ต่ำ risk ก่อน) ─────────────
    options: list[dict] = []

    if food <= 1.0:
        options.append({
            "action":     "หาอาหารจากแหล่งที่ปลอดภัยและถูกกฎหมาย เช่น ตลาดท้องถิ่นหรือชุมชน",
            "priority":   "CRITICAL",
            "reversible": True,
        })

    if danger >= 7.0:
        options.append({
            "action":     "ลดการเผชิญอันตราย — ย้ายไปสภาพแวดล้อมที่ปลอดภัยกว่าทันที",
            "priority":   "CRITICAL",
            "reversible": True,
        })

    if money <= 100.0:
        options.append({
            "action":     "มองหางานระยะสั้นหรือความร่วมมือในชุมชน",
            "priority":   "HIGH",
            "reversible": True,
        })

    if risk < 5.0:
        options.append({
            "action":     "ขยายโอกาสอย่างระมัดระวัง รักษาความปลอดภัยไว้ก่อน",
            "priority":   "MODERATE",
            "reversible": True,
        })

    # safe fallback เสมอ (FATE™ Choice ≥ 1)
    options.append({
        "action":     "หาความร่วมมือกับคนท้องถิ่นก่อนเพิ่มความขัดแย้ง",
        "priority":   "LOW",
        "reversible": True,
    })
    options.append({
        "action":     "ให้ความสำคัญกับทางออกที่ปกป้องคน สัตว์ ทรัพย์สิน สิ่งแวดล้อม",
        "priority":   "LOW",
        "reversible": True,
    })

    fate_audit = {
        "choice_count":       len(options),
        "choice_floor_ok":    len(options) >= 1,
        "all_reversible":     all(o["reversible"] for o in options),
        "downside_first":     True,
        "safety_rule_active": True,
    }

    return {
        "risk_score":          risk,
        "risk_level":          risk_label,
        "route":               route,
        "location":            location,
        "inputs":              {"food": food, "money": money, "danger": danger},
        "recommended_actions": options,
        "principle":           "Survival without harm",
        "safety_rule":         SAFETY_RULE,
        "fate_audit":          fate_audit,
    }
