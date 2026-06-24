# ENGINE/universal_engine.py
"""
KING DIADEM — Universal Engine
Orchestration layer — wire ทุก engine เข้าด้วยกัน
Safe imports — ไม่ crash ถ้า module ยังไม่พร้อม
"""
from __future__ import annotations
import time

# ── Safe imports ──────────────────────────────────────────────────
try:
    from ENGINE.pattern_engine import analyze_pattern
    _PATTERN = True
except ImportError:
    _PATTERN = False

try:
    from ENGINE.risk_engine import analyze_risk
    _RISK = True
except ImportError:
    _RISK = False

try:
    from ENGINE.decision_engine import decision_intelligence
    _DECISION = True
except ImportError:
    _DECISION = False

try:
    from ENGINE.council_engine import council_engine
    _COUNCIL = True
except ImportError:
    _COUNCIL = False

try:
    from ENGINE.consensus_engine import consensus_engine
    _CONSENSUS = True
except ImportError:
    _CONSENSUS = False

try:
    from core.emptiness_guard import emptiness_guard
    _GUARD = True
except ImportError:
    _GUARD = False


# ── Fallbacks ─────────────────────────────────────────────────────
def _pattern_fallback(raw: dict) -> dict:
    entropy   = float(raw.get("entropy",   40))
    resource  = float(raw.get("resource",  50))
    stability = float(raw.get("stability", 60))
    route = "survival" if entropy > 65 or resource < 25 else \
            "business" if "ธุรกิจ" in str(raw.get("input","")) or "business" in str(raw.get("input","")).lower() else \
            "general"
    return {**raw, "route": route, "pattern_source": "fallback"}

def _risk_fallback(state: dict) -> dict:
    entropy   = float(state.get("entropy",   40))
    resource  = float(state.get("resource",  50))
    stability = float(state.get("stability", 60))
    score = round(max(0, min(100,
        entropy * 0.40 + (100 - resource) * 0.35 + (100 - stability) * 0.25
    )), 1)
    level = "critical" if score >= 75 else "high" if score >= 55 else \
            "moderate" if score >= 35 else "low"
    return {"score": score, "level": level, "pause": score >= 75}

def _decision_fallback(state: dict, risk: dict) -> dict:
    level = risk.get("level", "low")
    if level == "critical":
        action = "HALT — stabilize before any new decision"
    elif level == "high":
        action = "REDUCE — cut exposure, secure baseline resources"
    elif level == "moderate":
        action = "MONITOR — watch waterline daily"
    else:
        action = "PROCEED — maintain current strategy"
    return {"action": action, "risk_level": level, "source": "fallback"}

def _council_fallback(decision: dict, state: dict) -> dict:
    return {
        "votes": [decision.get("action", "—")],
        "quorum": 1,
        "source": "fallback",
    }

def _consensus_fallback(council: dict, state: dict) -> dict:
    votes = council.get("votes", [])
    return {
        "final_action": votes[0] if votes else "no_consensus",
        "confidence":   0.6,
        "source":       "fallback",
    }

def _guard_fallback(packet: dict) -> dict:
    choices = int(packet.get("choices", 1))
    if choices <= 0:
        return {**packet, "blocked": True,
                "reason": "Choice(t) = 0 — SYSTEM_PAUSE",
                "output": {"axiom": "Choice(t) ≥ 1 → collapse = False"}}
    return {**packet, "blocked": False}


# ── Normalize ─────────────────────────────────────────────────────
def _normalize(payload) -> dict:
    if not isinstance(payload, dict):
        payload = {}
    return {
        "input":            str(payload.get("input", payload.get("question", ""))).strip(),
        "entropy":          float(payload.get("entropy",    40)),
        "resource":         float(payload.get("resource",   50)),
        "stability":        float(payload.get("stability",  60)),
        "choices":          int(payload.get("choices",       1)),
        "confidence":       float(payload.get("confidence", 0.5)),
        "decision":         payload.get("decision"),
        "previous_decision":payload.get("previous_decision"),
        "decision_history": payload.get("decision_history", []),
        "warnings":         payload.get("warnings",         []),
        "alternatives":     payload.get("alternatives",     []),
        "locked":           bool(payload.get("locked",      False)),
    }


# ── Main ──────────────────────────────────────────────────────────
def run_engine(payload) -> dict:
    t0  = time.time()
    raw = _normalize(payload)

    pattern  = analyze_pattern(raw)       if _PATTERN  else _pattern_fallback(raw)
    state    = {**raw, **pattern}
    state    = emptiness_guard(state)     if _GUARD    else _guard_fallback(state)

    risk     = analyze_risk(state)        if _RISK     else _risk_fallback(state)
    decision = decision_intelligence(state, risk) if _DECISION else _decision_fallback(state, risk)
    council  = council_engine(decision, state)    if _COUNCIL  else _council_fallback(decision, state)
    consensus= consensus_engine(council, state)   if _CONSENSUS else _consensus_fallback(council, state)

    packet = emptiness_guard({
        **state,
        "risk": risk, "decision": decision,
        "council": council, "consensus": consensus,
    }) if _GUARD else _guard_fallback({
        **state,
        "risk": risk, "decision": decision,
        "council": council, "consensus": consensus,
    })

    base = {
        "state":     state,
        "risk":      risk,
        "decision":  decision,
        "council":   council,
        "consensus": consensus,
        "latency_ms":round((time.time() - t0) * 1000, 1),
        "modules":   {
            "pattern": _PATTERN, "risk": _RISK, "decision": _DECISION,
            "council": _COUNCIL, "consensus": _CONSENSUS, "guard": _GUARD,
        },
    }

    if packet.get("blocked"):
        return {"status": "blocked", "reason": packet.get("reason"), **base}

    return {"status": "ok", "output": packet.get("output", {}), **base}
