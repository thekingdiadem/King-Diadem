# KING DIADEM™ — Core Axioms & Governance Constants
# Stability Layer for Decision Engine
# FATE™: "Fail less, not win more."

import time
from typing import Optional

# ── A1–A5 Axioms ──────────────────────────────────────────────────
AXIOMS = {
    "A1": "Collapse occurs when choices disappear",
    "A2": "Structure is for protection, not dominating. Good structure gives humans room to breathe — not zero choices.",
    "A3": "Do not optimize when survival floor is unstable",
    "A4": "Small drift compounds into system collapse",
    "A5": "Intervene only when choice approaches zero",
}

# ── DriftZero Governance Metrics ──────────────────────────────────
DHD_MAX_THRESHOLD    = 0.001   # Daily Harm Delta — max drift per day (0.1%)
CHOICE_MIN_THRESHOLD = 1       # Choice Safety Floor — intervention if below
STOP_THE_LINE        = True    # Halt all actions if drift exceeds threshold

# ── Extended constants (FATE™ operational layer) ──────────────────
WATERLINE_FLOOR      = 20.0    # ต่ำกว่านี้ = SURVIVAL territory
ENTROPY_CEILING      = 80.0    # สูงกว่านี้ = SYSTEM_PAUSE required
STABILITY_FLOOR      = 25.0    # ต่ำกว่านี้ = force reduce_exposure
COLLAPSE_PROB_LIMIT  = 0.75    # collapse_probability เกินนี้ = halt

# ISO Severity Scale (S0–S4)
SEVERITY = {
    "S0": "NOMINAL   — no action required",
    "S1": "ADVISORY  — monitor closely",
    "S2": "WARNING   — reduce exposure",
    "S3": "CRITICAL  — intervention required",
    "S4": "COLLAPSE  — halt all non-survival actions",
}


# ── Enforcement functions ─────────────────────────────────────────
def check_axioms(state: dict) -> dict:
    """
    ตรวจ A1–A5 ต่อ system state จริง
    คืน dict ของ axiom ที่ violated + severity + recommended action

    Article 3 — audit trail ต้องอธิบายได้ว่า axiom ไหน trigger ทำไม
    """
    state = state if isinstance(state, dict) else {}

    def _n(k, d):
        try:
            x = float(state.get(k, d))
        except (TypeError, ValueError):
            return d
        return x if x == x else d

    entropy           = _n("entropy",              50.0)
    stability         = _n("stability",            50.0)
    choices_available = int(_n("choices_available", 1))
    drift_delta       = _n("drift_delta",          0.0)
    collapse_prob     = _n("collapse_probability", 0.0)

    violations: list  = []
    stop_line: bool   = False

    # A1 — choices disappeared
    if choices_available < CHOICE_MIN_THRESHOLD:
        violations.append({
            "axiom":  "A1",
            "reason": f"choices_available={choices_available} < floor={CHOICE_MIN_THRESHOLD}",
            "action": "HALT — restore at least one viable option before proceeding",
        })
        stop_line = True

    # A2 — only one choice left (warning before A1 fires)
    elif choices_available == CHOICE_MIN_THRESHOLD:
        violations.append({
            "axiom":  "A2",
            "reason": "only one viable option remaining",
            "action": "WARNING — expand options before committing",
        })

    # A3 — optimizing while survival floor unstable
    if stability < STABILITY_FLOOR and entropy > ENTROPY_CEILING:
        violations.append({
            "axiom":  "A3",
            "reason": f"stability={stability} < {STABILITY_FLOOR} AND entropy={entropy} > {ENTROPY_CEILING}",
            "action": "STOP optimization — secure survival floor first",
        })
        stop_line = True

    # A4 — drift compounding
    if drift_delta > DHD_MAX_THRESHOLD:
        violations.append({
            "axiom":  "A4",
            "reason": f"drift_delta={drift_delta} > DHD_MAX={DHD_MAX_THRESHOLD}",
            "action": "INTERVENE — arrest drift before it compounds",
        })
        if STOP_THE_LINE:
            stop_line = True

    # A5 — collapse probability near threshold
    if collapse_prob >= COLLAPSE_PROB_LIMIT:
        violations.append({
            "axiom":  "A5",
            "reason": f"collapse_probability={collapse_prob} >= limit={COLLAPSE_PROB_LIMIT}",
            "action": "HALT — minimum intervention to restore choice",
        })
        stop_line = True

    # severity
    if stop_line:
        severity = "S4" if choices_available < 1 else "S3"
    elif violations:
        severity = "S2"
    elif entropy > 60 or stability < 40:
        severity = "S1"
    else:
        severity = "S0"

    return {
        "violations":   violations,
        "stop_line":    stop_line,
        "severity":     severity,
        "severity_desc": SEVERITY[severity],
        "axiom_count":  len(violations),
        "checked_at":   time.time(),
        "axiom":        "Choice(t) >= 1 -> collapse = False",
    }


def get_axiom(key: str) -> Optional[str]:
    """คืน axiom text — ใช้ใน audit trail / response lineage"""
    return AXIOMS.get(key)


def governance_summary() -> dict:
    """คืน constants ทั้งหมดสำหรับ /api/kernel_snapshot"""
    return {
        "axioms":             AXIOMS,
        "DHD_MAX_THRESHOLD":  DHD_MAX_THRESHOLD,
        "CHOICE_MIN_THRESHOLD": CHOICE_MIN_THRESHOLD,
        "STOP_THE_LINE":      STOP_THE_LINE,
        "WATERLINE_FLOOR":    WATERLINE_FLOOR,
        "ENTROPY_CEILING":    ENTROPY_CEILING,
        "STABILITY_FLOOR":    STABILITY_FLOOR,
        "COLLAPSE_PROB_LIMIT": COLLAPSE_PROB_LIMIT,
        "severity_scale":     SEVERITY,
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # healthy state — no violations
    r1 = check_axioms({"entropy": 40, "stability": 65, "choices_available": 3,
                        "drift_delta": 0.0005, "collapse_probability": 0.2})
    assert r1["stop_line"] is False
    assert r1["severity"] == "S0"

    # A1 — zero choices
    r2 = check_axioms({"choices_available": 0})
    assert r2["stop_line"] is True
    assert any(v["axiom"] == "A1" for v in r2["violations"])

    # A4 — drift exceeded
    r3 = check_axioms({"drift_delta": 0.005, "choices_available": 2})
    assert any(v["axiom"] == "A4" for v in r3["violations"])
    assert r3["stop_line"] is True

    # A5 — collapse prob high
    r4 = check_axioms({"collapse_probability": 0.80, "choices_available": 2})
    assert any(v["axiom"] == "A5" for v in r4["violations"])

    return {"status": "OK", "module": "axioms"}


if __name__ == "__main__":
    import json
    # simulate crisis state
    state = {
        "entropy": 82,
        "stability": 22,
        "choices_available": 1,
        "drift_delta": 0.003,
        "collapse_probability": 0.78,
    }
    print(json.dumps(check_axioms(state), indent=2, default=str))
    print(_self_test())
