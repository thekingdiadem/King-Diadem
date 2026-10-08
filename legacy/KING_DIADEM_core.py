# ============================================================
# KING DIADEM CORE — v2.2  (wiring fix)
# Author: Nithikorn Bunsrang
# Architecture: UDOK × DriftZero × Silent Canon
#
# Layer 0 Law: Choice(t) >= 1 → collapse = False
# Kernel Law : หยุดที่เวทนา ก่อนมันสร้างตัวตน
# Silent Canon: Preserve choice. Non-interference.
#               Only act when choice approaches zero.
#
# --- PATCH v2.1 ---
# FIX 1: SurvivalThreshold — ย้าย import ให้ตรง path จริง
# FIX 2: predict_collapse() — ส่ง risk_score (float) แทน human_state (dict)
# FIX 3: generate_paths() — ส่ง lat/lng แทน dict, เพิ่ม "viable" key
#
# --- PATCH v2.2 ---
# เดิม import ไม่ได้เลย: find_escape_routes, ENGINE.drift_monitor, check_energy,
# SILENT_CANON, validate_against_reality, SIMULATIONS.collapse_predictor ไม่มีอยู่จริง
# และเรียก analyze_situation(question) / assess_risk(a, b) / intervention(paths, escape)
# ผิด signature ทั้งหมด → ต่อกับฟังก์ชันที่มีจริง (โครงเดิมคงไว้)
# ไม่สร้างพิกัด 0,0 เอง (อ่าวกินี) — ไม่มีพิกัด = ไม่สร้างเส้นทางบนแผนที่
# ============================================================

from ENGINE.situation_analyzer import analyze_situation
from ENGINE.human_state_engine import analyze_human_state
from ENGINE.collapse_predictor import predict_collapse
from ENGINE.escape_routes import generate_escape_routes
from ENGINE.path_generator import generate_paths
from ENGINE.intervention_engine import intervene
from ENGINE.risk_engine import assess_risk

from core.emptiness_guard import emptiness_guard
from core.silent_canon import SilentCanon
from core.drift_monitor import detect_drift, log_drift_event
from core.survival_threshold import SurvivalThreshold

SILENT_CANON = {
    "law":       SilentCanon.PRIME_LAW,
    "limit":     SilentCanon.INTERVENTION_LIMIT,
    "silence":   SilentCanon.SILENCE_IS,
}


def _f(v, d: float) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d


# ─────────────────────────────────────────────
# LAYER 0: PRE-KERNEL CHECK
# ─────────────────────────────────────────────

def _layer0_check(question: str) -> dict:
    # Reality = Universe − {Impossible}: ข้อความว่าง/ไม่ใช่ข้อความ = ไม่มีอะไรให้ตรวจ
    valid = isinstance(question, str) and bool(question.strip())
    return {
        "reality_verified": valid,
        "energy_level": "n/a",      # ไม่มีตัววัดพลังงานจริงในระบบ (check_energy ไม่เคยมี)
        "proceed": valid,
    }


# ─────────────────────────────────────────────
# KERNEL: CAUSAL INTERRUPT
# ─────────────────────────────────────────────

def _kernel_interrupt(human_state: dict, state: dict) -> dict:
    craving = bool(state.get("craving_signal"))
    if craving:
        human_state["kernel_flag"] = "CRAVING_DETECTED — pause before act"
        human_state["recommended_action"] = "re-evaluate from fact layer"
    else:
        human_state["kernel_flag"] = "CLEAR"
    # emptiness_guard คืนรายงานของตัวเอง — เดิมเอาไปเขียนทับ human_state ทั้งก้อน
    human_state["guard"] = emptiness_guard(state)
    return human_state


# ─────────────────────────────────────────────
# DRIFT MONITOR
# ─────────────────────────────────────────────

def _monitor_drift(human_state: dict, state: dict, session_id=None) -> dict:
    drift = detect_drift({
        "entropy":      state.get("entropy", 40),
        "choice_count": state.get("choice_count", 1),
    }, session_id=session_id)
    if drift.get("status") not in ("stable", None):
        log_drift_event(drift, session_id)
        human_state["drift_warning"] = drift.get("status")
        human_state["drift_severity"] = drift.get("drift_score", 0)
    else:
        human_state["drift_warning"] = None
    return human_state


# ─────────────────────────────────────────────
# CHOICE GUARD — Layer 0 Law
# ─────────────────────────────────────────────

def _choice_guard(paths: list, escape: list) -> dict:
    # ทางเลือกจริง = เส้นทางบนแผนที่ที่มีปลายทาง + เส้นทางออกที่ทำได้ (feasibility ไม่ใช่ LOW)
    viable_paths  = [p for p in paths if p.get("viable") is True]
    viable_escape = [e for e in escape if isinstance(e, dict) and e.get("feasibility") != "LOW"]
    choice_count  = len(viable_paths) + len(viable_escape)

    threshold = SurvivalThreshold.MINIMUM_CHOICES  # default: 1

    status = {
        "choice_count": choice_count,
        "below_threshold": choice_count < threshold,
        "law": SILENT_CANON["law"],
        "intervention_required": False
    }

    if status["below_threshold"]:
        status["intervention_required"] = True
        status["alert"] = f"⚠️ Choice(t) = {choice_count} — collapse imminent"

    return status


# ─────────────────────────────────────────────
# MAIN CORE FUNCTION
# ─────────────────────────────────────────────

def king_diadem(question: str, context: dict = None, session_id: str = None,
                with_decision: bool = False) -> dict:
    """
    context (optional): entropy/resource/stability/food/money/energy/shelter/network/
                        lat/lng/location/craving_signal
    with_decision=True จะเรียก DecisionEngine (มี LLM call) — ปิดไว้เป็นค่าเริ่มต้น
    """
    ctx = context if isinstance(context, dict) else {}

    # ── PRE-KERNEL ─────────────────────────────
    layer0 = _layer0_check(question)
    if not layer0["proceed"]:
        return {
            "status": "BLOCKED",
            "reason": "Reality check failed — cannot proceed without verified input",
            "layer0": layer0
        }

    state = {
        "entropy":   _f(ctx.get("entropy"), 40.0),
        "resource":  _f(ctx.get("resource"), 50.0),
        "stability": _f(ctx.get("stability"), 60.0),
        "craving_signal": ctx.get("craving_signal", False),
    }

    # ── HUMAN STATE ────────────────────────────
    human_state = analyze_human_state(question)
    human_state = _kernel_interrupt(human_state, state)

    # ── RISK & COLLAPSE ────────────────────────
    risk = assess_risk({**state, "raw_input": question})
    risk_score_value = _f(risk.get("risk_score"), 40.0)
    state["choice_count"] = risk.get("remaining_choices", 1)
    human_state = _monitor_drift(human_state, state, session_id)
    collapse_signal = predict_collapse(risk_score_value)

    # ── SITUATION ──────────────────────────────
    situation = analyze_situation(
        food_score=ctx.get("food", 50.0),
        risk_score=risk_score_value,
        money=ctx.get("money", 50.0),
        energy=ctx.get("energy", 50.0),
        shelter=ctx.get("shelter", True) is not False,
        network=ctx.get("network", 1),
        context=ctx,
    )

    # ── PATHS ──────────────────────────────────
    paths = []
    if ctx.get("lat") is not None and ctx.get("lng") is not None:
        gp = generate_paths(_f(ctx.get("lat"), 0.0), _f(ctx.get("lng"), 0.0))
        paths = [
            {**p, "viable": bool(p.get("type") and (p.get("target_lat") is not None or p.get("waypoints")))}
            for p in (gp.get("paths", []) if isinstance(gp, dict) else [])
        ]

    escape = generate_escape_routes(
        location=str(ctx.get("location", "")),
        risk=risk_score_value / 10.0,
        context=ctx,
    )

    # ── CHOICE GUARD ───────────────────────────
    choice_status = _choice_guard(paths, escape)

    # ── INTERVENTION (only if choice → 0) ─────
    help_plan = None
    if choice_status["intervention_required"]:
        help_plan = intervene(situation.get("risk_state", "critical"), ctx)

    # ── DECISION (optional — LLM) ──────────────
    decision = None
    if with_decision:
        from ENGINE.decision_engine import run_decision
        decision = run_decision({
            "input":        question,
            "raw_input":    question,
            "session_id":   session_id,
            "context":      ctx,
        })

    # ── OUTPUT ─────────────────────────────────
    return {
        "kernel_status":   human_state.get("kernel_flag"),
        "drift_warning":   human_state.get("drift_warning"),
        "situation":       situation,
        "human_state":     human_state,
        "risk":            risk,
        "collapse_signal": collapse_signal,
        "choice_status":   choice_status,
        "paths":           paths,
        "escape_routes":   escape,
        "intervention":    help_plan,
        "decision":        decision,
        "canon":           SILENT_CANON
    }
