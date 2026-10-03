# AI/decision_engine.py — KING DIADEM
# FATE™ Axiom compliance: Determinism · Downside First · Choice(t) ≥ 1
# Fail less. Harm less. Restore more.

from AI.decision_memory import store_decision

# ── OPTION REGISTRY — deterministic, route-aware ──────────────────
_OPTIONS_BY_ROUTE: dict[str, list[dict]] = {
    "survival": [
        {"action": "exit safely",          "risk": 0.08, "reversible": True},
        {"action": "reduce immediate risk", "risk": 0.12, "reversible": True},
        {"action": "gather emergency info", "risk": 0.15, "reversible": True},
        {"action": "seek safe shelter",     "risk": 0.18, "reversible": True},
    ],
    "collapse": [
        {"action": "exit safely",          "risk": 0.08, "reversible": True},
        {"action": "reduce immediate risk", "risk": 0.12, "reversible": True},
        {"action": "wait and stabilize",   "risk": 0.20, "reversible": True},
        {"action": "seek collaboration",   "risk": 0.30, "reversible": True},
    ],
    "risk": [
        {"action": "gather more information", "risk": 0.12, "reversible": True},
        {"action": "take cautious action",    "risk": 0.25, "reversible": True},
        {"action": "wait and observe",        "risk": 0.20, "reversible": True},
        {"action": "seek collaboration",      "risk": 0.30, "reversible": True},
    ],
    "general": [
        {"action": "gather more information", "risk": 0.12, "reversible": True},
        {"action": "wait and observe",        "risk": 0.20, "reversible": True},
        {"action": "seek collaboration",      "risk": 0.30, "reversible": True},
        {"action": "take cautious action",    "risk": 0.25, "reversible": True},
    ],
    "vega": [
        {"action": "gather more information", "risk": 0.12, "reversible": True},
        {"action": "seek collaboration",      "risk": 0.30, "reversible": True},
        {"action": "take cautious action",    "risk": 0.25, "reversible": True},
        {"action": "strategic advance",       "risk": 0.50, "reversible": False},
    ],
}

_SAFE_FALLBACK = _OPTIONS_BY_ROUTE["general"]


def process_decision(
    question: str,
    route: str = "general",
    context: dict | None = None,
) -> list[dict]:
    """
    สร้าง decision options แบบ deterministic — เรียง Downside First

    Args:
        question: คำถาม / สถานการณ์
        route:    active route
        context:  human context dict (optional)

    Returns:
        list of option dicts เรียง risk ASC
    FATE™: Choice(t) ≥ 1 เสมอ
    """
    question = str(question or "")
    if not question.strip():
        options = _SAFE_FALLBACK
    else:
        options = list(_OPTIONS_BY_ROUTE.get(route, _SAFE_FALLBACK))

    # เรียง Downside First (Axiom 4)
    options = sorted(options, key=lambda x: x["risk"])

    store_decision(question, [o["action"] for o in options], route=route,
                   context=context if isinstance(context, dict) else {})
    return options
