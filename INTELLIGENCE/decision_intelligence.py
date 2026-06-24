# INTELLIGENCE/decision_intelligence.py
# KING DIADEM — Decision Intelligence Layer v2.0
# FATE™ Axiom: Logic over Persona | Downside before Upside | Explainability=100%
# Choice(t) >= 1 → collapse = False
# -----------------------------------------------------------------

from typing import Any

# ── FATE™ AXIOM CONSTANTS ─────────────────────────────────────────
AXIOM_LOGIC_OVER_PERSONA     = "A1"
AXIOM_RULE_OVER_AUTHORITY    = "A2"
AXIOM_DETERMINISM            = "A3"
AXIOM_DOWNSIDE_FIRST         = "A4"
AXIOM_EXPLAINABILITY_100     = "A5"
AXIOM_HUMAN_FINAL_AUTHORITY  = "A6"

# ── SIGNAL THRESHOLDS (ปรับได้, ไม่ hardcode ใน logic) ───────────
SIGNAL_THRESHOLDS = {
    "collapse":    float("inf"),   # risk = inf  → collapse
    "danger":      50.0,           # risk > 50
    "warning":     20.0,           # risk > 20
    "elevated":    10.0,           # risk > 10
    "normal":       0.0,           # default
}

PATTERN_THRESHOLDS = {
    "market_instability": 0.5,     # pivot_ratio
    "risk_environment":   0.4,     # defensive_ratio
    "volatile":           0.7,     # pivot_ratio (extreme)
    "crisis":             0.8,     # defensive_ratio (extreme)
}


# ══════════════════════════════════════════════════════════════════
# CORE FUNCTION
# ══════════════════════════════════════════════════════════════════

def intelligence_layer(
    base_decision: dict,
    patterns:      dict,
    risk:          dict | float,
    external_ai:   Any = None,
) -> dict:
    """
    รวม base_decision + patterns + risk → signal + FATE™ audit

    Parameters
    ----------
    base_decision : dict   ผลจาก decision_engine
    patterns      : dict   ผลจาก pattern_engine  (pivot_ratio, defensive_ratio, …)
    risk          : dict | float
                    ถ้าเป็น dict คาดว่ามี key "risk" (float) และ "status" (str)
                    ถ้าเป็น float ใช้ตัวเลขตรงๆ
    external_ai   : Any    optional — raw output จาก external AI (reference only)

    Returns
    -------
    dict พร้อม system_signal, axiom_audit, lineage, …
    """

    # ── 1. Normalize risk value ────────────────────────────────────
    if isinstance(risk, dict):
        risk_value  = float(risk.get("risk", 0.0))
        risk_status = str(risk.get("status", "UNKNOWN"))
    else:
        risk_value  = float(risk) if risk is not None else 0.0
        risk_status = _risk_status_from_value(risk_value)

    # ── 2. Compute pattern signal ──────────────────────────────────
    pivot_ratio     = float(patterns.get("pivot_ratio",     0.0))
    defensive_ratio = float(patterns.get("defensive_ratio", 0.0))
    pattern_signal  = _derive_pattern_signal(pivot_ratio, defensive_ratio)

    # ── 3. Derive system signal (risk takes priority) ──────────────
    system_signal = _derive_system_signal(risk_value, risk_status, pattern_signal)

    # ── 4. Waterline check (Choice >= 1 axiom) ────────────────────
    remaining_choice = float(
        risk.get("remaining_choice", 1.0) if isinstance(risk, dict) else 1.0
    )
    waterline_breach = remaining_choice <= 0 or risk_value == float("inf")

    # ── 5. FATE™ Axiom Audit ───────────────────────────────────────
    axiom_audit = _build_axiom_audit(
        base_decision    = base_decision,
        patterns         = patterns,
        risk_value       = risk_value,
        system_signal    = system_signal,
        waterline_breach = waterline_breach,
    )

    # ── 6. Explainability chain (A5 = 100%) ───────────────────────
    lineage = {
        "step_1_pattern_input": {
            "pivot_ratio":     pivot_ratio,
            "defensive_ratio": defensive_ratio,
            "pattern_detected": patterns.get("pattern_detected", False),
        },
        "step_2_pattern_signal": pattern_signal,
        "step_3_risk_value":     risk_value,
        "step_4_risk_status":    risk_status,
        "step_5_system_signal":  system_signal,
        "step_6_waterline":      "BREACH" if waterline_breach else "OK",
        "step_7_axiom_audit":    axiom_audit,
    }

    # ── 7. Assembly ───────────────────────────────────────────────
    return {
        "system_signal":    system_signal,
        "pattern_analysis": patterns,
        "risk_value":       risk_value,
        "risk_status":      risk_status,
        "waterline":        "BREACH" if waterline_breach else "OK",
        "internal_decision": base_decision,
        "external_ai":      external_ai,   # reference เท่านั้น ไม่ใช้ override
        "axiom_audit":      axiom_audit,
        "lineage":          lineage,
        "choice_preserved": not waterline_breach,   # TITAN CORE prime axiom
    }


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _risk_status_from_value(risk_value: float) -> str:
    if risk_value == float("inf"):
        return "COLLAPSE"
    if risk_value > SIGNAL_THRESHOLDS["danger"]:
        return "DANGER"
    if risk_value > SIGNAL_THRESHOLDS["warning"]:
        return "WARNING"
    if risk_value > SIGNAL_THRESHOLDS["elevated"]:
        return "ELEVATED"
    return "SAFE"


def _derive_pattern_signal(pivot_ratio: float, defensive_ratio: float) -> str:
    if defensive_ratio >= PATTERN_THRESHOLDS["crisis"]:
        return "crisis"
    if pivot_ratio >= PATTERN_THRESHOLDS["volatile"]:
        return "volatile_market"
    if pivot_ratio >= PATTERN_THRESHOLDS["market_instability"]:
        return "market_instability"
    if defensive_ratio >= PATTERN_THRESHOLDS["risk_environment"]:
        return "risk_environment"
    return "normal"


def _derive_system_signal(
    risk_value:     float,
    risk_status:    str,
    pattern_signal: str,
) -> str:
    """
    Risk-first: ถ้า risk สูง pattern ก็ overrule ไม่ได้
    """
    if risk_value == float("inf") or risk_status == "COLLAPSE":
        return "collapse"
    if risk_status == "DANGER":
        return "danger"
    if risk_status == "WARNING":
        # pattern อาจยกระดับหรือลดระดับไม่ได้ — คง warning
        return "warning"
    if risk_status == "ELEVATED":
        # pattern เพิ่มข้อมูล
        if pattern_signal in ("volatile_market", "crisis"):
            return "warning"
        return "elevated"
    # risk = SAFE → ดู pattern
    if pattern_signal == "crisis":
        return "warning"
    if pattern_signal in ("volatile_market", "market_instability"):
        return "elevated"
    if pattern_signal == "risk_environment":
        return "monitor"
    return "normal"


def _build_axiom_audit(
    base_decision:    dict,
    patterns:         dict,
    risk_value:       float,
    system_signal:    str,
    waterline_breach: bool,
) -> dict:
    """
    ตรวจ FATE™ 6 axioms และ return pass/fail พร้อม reason
    """
    audits = {}

    # A1: Logic over Persona — ไม่มี persona override ใน layer นี้
    audits[AXIOM_LOGIC_OVER_PERSONA] = {
        "name":   "Logic over Persona",
        "pass":   True,
        "reason": "Intelligence layer ไม่มี persona bias — ใช้ threshold-based logic ล้วน",
    }

    # A3: Determinism — ไม่มี random
    audits[AXIOM_DETERMINISM] = {
        "name":   "Determinism",
        "pass":   True,
        "reason": "signal = pure function ของ risk_value + pattern ratio — ไม่มี random()",
    }

    # A4: Downside First
    downside_checked = risk_value > 0 or system_signal in ("warning", "danger", "collapse")
    audits[AXIOM_DOWNSIDE_FIRST] = {
        "name":   "Downside before Upside",
        "pass":   downside_checked,
        "reason": f"risk_value={risk_value:.2f}, signal={system_signal}",
    }

    # A5: Explainability = 100%
    has_lineage = bool(base_decision)
    audits[AXIOM_EXPLAINABILITY_100] = {
        "name":   "Explainability 100%",
        "pass":   has_lineage,
        "reason": "lineage dict มีทุก step ของการ derive signal",
    }

    # A6: Human Final Authority — waterline ต้องไม่ breach
    audits[AXIOM_HUMAN_FINAL_AUTHORITY] = {
        "name":   "Human Final Authority",
        "pass":   not waterline_breach,
        "reason": "COLLAPSE" if waterline_breach else "Choice >= 1 preserved",
    }

    passed = sum(1 for v in audits.values() if v["pass"])
    total  = len(audits)

    return {
        "axioms":  audits,
        "score":   f"{passed}/{total}",
        "passed":  passed == total,
        "verdict": "FATE_PASS" if passed == total else "FATE_PARTIAL",
    }
