"""
core/core_loop.py
CORE LOOP — KING DIADEM v3.1

แก้จาก v3.0:
  - ตัด EmotionState object ใน dict → serialize พัง (JSON ไม่รู้จัก object)
  - ตัด record_outcome ออกจาก core → side effect ใน core loop ผิด FATE Axiom 3
  - เพิ่ม SilentCanon.evaluate() — ทุก tick ต้องผ่าน Canon
  - เพิ่ม evaluate_laws() — ตรวจ Reality Laws ทุก tick
  - estimate_choice_count() derive จาก state เองโดยไม่รอ user input
"""

from core.time_engine import compute_time_to_failure, compute_decision_window
from core.silent_canon import SilentCanon, CanonStatus
from core.reality_laws import evaluate_laws


def clamp(v: float) -> float:
    return max(0.0, min(100.0, v))


def _f(v, d: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def compute_drift(state: dict) -> float:
    return clamp((state["entropy"] * 0.5) + ((100 - state["resource"]) * 0.5))


def update_entropy(state: dict) -> dict:
    state["entropy"] = clamp(_f(state.get("entropy"), 40) + _f(state.get("drift"), 0) * 0.1 - 1.5)
    return state


def update_stability(state: dict) -> dict:
    state["stability"] = clamp(_f(state.get("stability"), 60) - _f(state.get("drift"), 0) * 0.3 + 0.5)
    return state


def stop_the_line(state: dict) -> bool:
    """DriftZero stop-the-line: stability < 20 หรือ resource < 10"""
    return state["stability"] < 20 or state["resource"] < 10


def estimate_choice_count(state: dict) -> int:
    """
    Derive choice_count จาก system state
    ไม่รอ user input — ระบบ estimate เองได้
    score 0–3 → Canon ใช้ตัวนี้ evaluate
    """
    score = 0
    if state["stability"] >= 40:
        score += 1
    if state["resource"] >= 20:
        score += 1
    if state.get("intervention") != "restore_minimum_path":
        score += 1
    return score


def run_core(state: dict, user_prompt: str = None) -> dict:
    """
    KING DIADEM Core Loop v3.1
    Pipeline: physics → reality laws → silent canon → time engine
    """
    # สำเนา + แปลงเป็นตัวเลข: เดิมแก้ dict ของผู้เรียกตรงๆ และค่า str/None ทำให้พังทั้ง loop
    state = dict(state) if isinstance(state, dict) else {}
    for k, d in (("entropy", 40), ("resource", 50), ("stability", 60)):
        state[k] = clamp(_f(state.get(k), d))

    # 1. Physics — entropy / stability / drift
    state["drift"]     = compute_drift(state)
    state              = update_entropy(state)
    state              = update_stability(state)

    # 2. Reality Laws check — ตรวจก่อน canon
    law_result = evaluate_laws({
        "entropy":       state["entropy"],
        "stability":     state["stability"],
        "resource":      state["resource"],
        "choice_count":  estimate_choice_count(state),
        "explainable":   state.get("explainable", True),
        "ego_in_signal": state.get("ego_in_signal", False),
    })
    state["law_violations"] = law_result["violations"]

    # 3. Stop-the-line — DriftZero hard floor
    if stop_the_line(state):
        return {
            "status":         "HALT",
            "reason":         "stop_the_line: stability or resource below floor",
            "state":          state,
            "law_violations": law_result["violations"],
        }

    # 4. Silent Canon — prime law enforcement
    choice_count = estimate_choice_count(state)
    canon_result = SilentCanon.evaluate(choice_count)

    if canon_result.status == CanonStatus.INTERVENE:
        state["intervention"] = "restore_minimum_path"
    else:
        state.pop("intervention", None)

    # 5. Time engine
    ttf    = compute_time_to_failure(state)
    window = compute_decision_window(ttf)

    return {
        "status":          "RUNNING",
        "state":           state,
        "time_to_failure": ttf,
        "decision_window": window,
        "canon":           canon_result.status.value,
        "choice_count":    choice_count,
        "law_violations":  law_result["violations"],
        "reality_aligned": law_result["reality_aligned"],
    }
