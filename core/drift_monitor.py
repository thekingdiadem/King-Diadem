"""
core/drift_monitor.py
KING DIADEM™ — DriftZero Waterline Governance Standard
Structural drift detection with FATE™ Axiom integration
v2.0 | Deterministic | No random | No stubs
"""

from datetime import datetime, timezone
from typing import Optional

# ─── FATE™ Axiom Constants ────────────────────────────────────────────────────

AXIOM_DRIFT_CEILING     = 0.001   # Axiom 6: 0.1% max tolerated drift per cycle
CHOICE_FLOOR            = 1       # Prime axiom: Choice(t) ≥ 1 → collapse = False
WATERLINE_BREACH_LABEL  = "WATERLINE_BREACH"
STOP_THE_LINE_LABEL     = "STOP_THE_LINE"

# ─── Drift Dimension Weights ──────────────────────────────────────────────────
# Each dimension maps to a FATE™ failure mode
DIMENSION_WEIGHTS = {
    "entropy":          0.30,   # system disorder (Axiom 3: Determinism)
    "choice_reduction": 0.25,   # options collapsing toward zero (Prime Axiom)
    "explainability":   0.20,   # opacity growing (Axiom 5: Explainability=100%)
    "rule_violation":   0.15,   # logic override attempts (Axiom 2: Rule > Authority)
    "downside_ignored": 0.10,   # upside-first reasoning (Axiom 4: Downside first)
}

# ─── Thresholds ───────────────────────────────────────────────────────────────
DRIFT_THRESHOLDS = {
    "stable":           (0.00, 0.10),
    "early_warning":    (0.10, 0.25),
    "elevated":         (0.25, 0.45),
    "critical_drift":   (0.45, 0.70),
    "waterline_breach": (0.70, 1.00),
}


# ─── Core Detection ───────────────────────────────────────────────────────────

def _normalize(value: float, floor: float = 0.0, ceiling: float = 100.0) -> float:
    """Clamp and normalize any raw metric to [0.0, 1.0]."""
    return max(0.0, min(1.0, (value - floor) / (ceiling - floor)))


def _compute_weighted_drift(dimensions: dict) -> float:
    """
    Deterministic weighted drift score.
    Each dimension contributes proportionally to its FATE™ risk weight.
    Returns float in [0.0, 1.0].
    """
    score = 0.0
    for key, weight in DIMENSION_WEIGHTS.items():
        raw = dimensions.get(key, 0.0)
        score += _normalize(raw) * weight
    return round(score, 6)


def _classify_drift(score: float) -> str:
    for label, (low, high) in DRIFT_THRESHOLDS.items():
        if low <= score < high:
            return label
    return "waterline_breach"


def _resolve_action(status: str, choice_count: int) -> str:
    """
    Action is deterministic by status + choice availability.
    If choice_count < CHOICE_FLOOR → force STOP_THE_LINE regardless of status.
    """
    if choice_count < CHOICE_FLOOR:
        return STOP_THE_LINE_LABEL

    action_map = {
        "stable":           "observe",
        "early_warning":    "increase_vigilance",
        "elevated":         "trigger_audit",
        "critical_drift":   "stabilize_system",
        "waterline_breach": STOP_THE_LINE_LABEL,
    }
    return action_map.get(status, STOP_THE_LINE_LABEL)


def _violated_axioms(dimensions: dict) -> list[str]:
    """Return list of axioms with dimension value above safe threshold (>0.5 normalized)."""
    violations = []
    axiom_map = {
        "entropy":          "Axiom 3 — Determinism",
        "choice_reduction": "Prime Axiom — Choice(t) ≥ 1",
        "explainability":   "Axiom 5 — Explainability = 100%",
        "rule_violation":   "Axiom 2 — Rule over Authority",
        "downside_ignored": "Axiom 4 — Downside before Upside",
    }
    for key, label in axiom_map.items():
        if _normalize(dimensions.get(key, 0.0)) > 0.5:
            violations.append(label)
    return violations


# ─── History Buffer (in-process; wire to db.py for persistence) ──────────────
_drift_history: list[dict] = []
MAX_HISTORY = 50


def _push_history(record: dict) -> None:
    _drift_history.append(record)
    if len(_drift_history) > MAX_HISTORY:
        _drift_history.pop(0)


def get_drift_history() -> list[dict]:
    return list(_drift_history)


def _trend(score: float) -> str:
    """Compare current score against last recorded score."""
    if len(_drift_history) < 2:
        return "insufficient_data"
    delta = score - _drift_history[-2].get("drift_score", score)
    if delta > 0.05:
        return "worsening"
    if delta < -0.05:
        return "recovering"
    return "stable"


# ─── Public API ───────────────────────────────────────────────────────────────

def detect_drift(
    system_state: dict,
    user_email: Optional[str] = None,
    session_id: Optional[str] = None,
) -> dict:
    """
    Main drift detection entry point.

    system_state keys (all optional, default 0.0):
        entropy          — system disorder level          [0–100]
        choice_reduction — how many options have closed   [0–100]
        explainability   — opacity / black-box score      [0–100]
        rule_violation   — override attempt frequency     [0–100]
        downside_ignored — upside-first reasoning count   [0–100]
        choice_count     — current available choices      [int ≥ 0]

    Returns structured DriftZero report dict.
    """
    dimensions = {k: system_state.get(k, 0.0) for k in DIMENSION_WEIGHTS}
    choice_count = int(system_state.get("choice_count", CHOICE_FLOOR))

    drift_score = _compute_weighted_drift(dimensions)
    status      = _classify_drift(drift_score)
    action      = _resolve_action(status, choice_count)
    violations  = _violated_axioms(dimensions)
    trend       = _trend(drift_score)

    # Waterline breach override: status escalates if choice floor broken
    if choice_count < CHOICE_FLOOR:
        status = WATERLINE_BREACH_LABEL
        action = STOP_THE_LINE_LABEL

    result = {
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "user_email":     user_email,
        "session_id":     session_id,
        "drift_score":    drift_score,
        "status":         status,
        "action":         action,
        "trend":          trend,
        "choice_count":   choice_count,
        "axiom_violations": violations,
        "dimensions":     {k: round(_normalize(v), 4) for k, v in dimensions.items()},
        "fate_lock":      "Fail less, not win more",
        "titan_prime":    f"Choice({choice_count}) ≥ {CHOICE_FLOOR} → collapse = {choice_count < CHOICE_FLOOR}",
    }

    _push_history(result)
    return result


# ─── Batch / Continuous Monitoring ────────────────────────────────────────────

def monitor_batch(states: list[dict], **kwargs) -> list[dict]:
    """Run detect_drift across a list of system states. Returns list of reports."""
    return [detect_drift(s, **kwargs) for s in states]


def drift_summary() -> dict:
    """Aggregate summary across all buffered history."""
    if not _drift_history:
        return {"error": "no_history"}

    scores = [r["drift_score"] for r in _drift_history]
    statuses = [r["status"] for r in _drift_history]

    return {
        "samples":        len(scores),
        "avg_drift":      round(sum(scores) / len(scores), 6),
        "max_drift":      round(max(scores), 6),
        "min_drift":      round(min(scores), 6),
        "breach_count":   statuses.count(WATERLINE_BREACH_LABEL),
        "critical_count": statuses.count("critical_drift"),
        "last_status":    statuses[-1] if statuses else None,
    }


# ─── Quick smoke test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json

    cases = [
        {"entropy": 5,  "choice_reduction": 2,  "explainability": 5,  "choice_count": 5},
        {"entropy": 40, "choice_reduction": 30, "explainability": 55, "choice_count": 2},
        {"entropy": 80, "choice_reduction": 70, "explainability": 90, "choice_count": 1},
        {"entropy": 95, "choice_reduction": 95, "explainability": 95, "choice_count": 0},  # prime axiom breach
    ]

    for i, case in enumerate(cases, 1):
        result = detect_drift(case, user_email="test@kingdiadem.ai", session_id=f"test-{i}")
        print(f"\n─── Case {i} ───")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n─── Summary ───")
    print(json.dumps(drift_summary(), indent=2))
