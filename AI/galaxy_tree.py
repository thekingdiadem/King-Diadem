# AI/galaxy_tree.py
# KING DIADEM — Galaxy Option Tree
# FATE™ Axiom compliance: Determinism · Downside First · Choice(t) ≥ 1
# Fail less. Harm less. Restore more.

from typing import Optional


def _n(v, d: float) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d

# ── STRATEGY REGISTRY ─────────────────────────────────────────────
# deterministic weights: (base_risk, base_confidence)
# risk   = probability of downside (0.0–1.0)
# confidence = system confidence in recommendation (0.0–1.0)

_STRATEGY_TABLE: dict[str, dict] = {
    "observe situation":    {"base_risk": 0.15, "base_confidence": 0.80, "tier": "low",    "downside": "ข้อมูลอาจล้าสมัยก่อนตัดสินใจ"},
    "reduce risk":          {"base_risk": 0.10, "base_confidence": 0.85, "tier": "low",    "downside": "อาจพลาดโอกาสที่มีหน้าต่างแคบ"},
    "increase action":      {"base_risk": 0.55, "base_confidence": 0.60, "tier": "high",   "downside": "ใช้ resource มากขึ้น — สำรองต้องพร้อม"},
    "collect information":  {"base_risk": 0.12, "base_confidence": 0.78, "tier": "low",    "downside": "ใช้เวลา — ระวัง analysis paralysis"},
    "build alliance":       {"base_risk": 0.30, "base_confidence": 0.70, "tier": "medium", "downside": "ขึ้นอยู่กับความน่าเชื่อถือของพันธมิตร"},
    "pivot strategy":       {"base_risk": 0.40, "base_confidence": 0.65, "tier": "medium", "downside": "สูญเสีย momentum ที่สร้างไว้"},
    "hold position":        {"base_risk": 0.20, "base_confidence": 0.75, "tier": "low",    "downside": "สถานการณ์อาจเปลี่ยนโดยไม่ได้เตรียม"},
    "exit safely":          {"base_risk": 0.08, "base_confidence": 0.90, "tier": "safe",   "downside": "อาจสูญเสียส่วนที่ลงทุนไปแล้ว"},
}

_ROUTE_STRATEGY_MAP: dict[str, list[str]] = {
    "survival": ["exit safely",         "reduce risk",      "observe situation"],
    "collapse": ["exit safely",         "reduce risk",      "hold position"],
    "risk":     ["reduce risk",         "observe situation","collect information"],
    "general":  ["observe situation",   "collect information", "build alliance"],
    "civil":    ["build alliance",      "hold position",    "observe situation"],
    "vega":     ["collect information", "pivot strategy",   "increase action"],
}


def _risk_modifier(entropy: float, stability: float) -> float:
    """
    คำนวณ modifier จากสภาพ human state
    entropy สูง → risk เพิ่ม / stability สูง → risk ลด
    """
    e_factor = (entropy - 50.0) / 100.0    # -0.5 to +0.5
    s_factor = (stability - 50.0) / 100.0  # -0.5 to +0.5
    return round(e_factor - s_factor * 0.5, 3)


def expand_options(
    problem: str,
    route: str = "general",
    entropy: float = 40.0,
    stability: float = 60.0,
    max_options: int = 3,
) -> list[dict]:
    """
    สร้าง strategic options แบบ deterministic
    Input:  problem text, route, human state metrics
    Output: list of option dicts — เรียงตาม risk ASC (Downside First)

    FATE™ guarantee: Choice(t) ≥ 1 → always returns ≥ 1 option
    """
    problem = str(problem or "")
    route = str(route or "general")
    entropy, stability = _n(entropy, 40.0), _n(stability, 60.0)
    try:
        max_options = max(1, int(max_options))
    except (TypeError, ValueError):
        max_options = 3
    if not problem.strip():
        # FATE™ safe fallback — ไม่ block ทุกทางออก
        return [{
            "strategy":   "observe situation",
            "risk":       0.15,
            "confidence": 0.80,
            "tier":       "low",
            "downside":   "ยังไม่มีข้อมูลเพียงพอ — รอดูก่อน",
            "fate_note":  "FALLBACK: input ว่าง — ใช้ safe default",
        }]

    modifier   = _risk_modifier(entropy, stability)
    strategies = _ROUTE_STRATEGY_MAP.get(route, _ROUTE_STRATEGY_MAP["general"])
    strategies = strategies[:max_options]

    options = []
    for strat in strategies:
        base = _STRATEGY_TABLE.get(strat, _STRATEGY_TABLE["observe situation"])
        adj_risk  = round(min(max(base["base_risk"] + modifier, 0.05), 0.95), 3)
        adj_conf  = round(min(max(base["base_confidence"] - abs(modifier) * 0.3, 0.30), 0.95), 3)
        options.append({
            "strategy":   strat,
            "risk":       adj_risk,
            "confidence": adj_conf,
            "tier":       base["tier"],
            "downside":   base["downside"],
            "route":      route,
            "fate_note":  f"entropy={entropy:.0f} stability={stability:.0f} modifier={modifier:+.3f}",
        })

    # เรียง risk น้อย→มาก (Axiom 4: Downside before Upside)
    options.sort(key=lambda x: x["risk"])
    return options
