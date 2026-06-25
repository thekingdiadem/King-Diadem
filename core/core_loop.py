# core/core_loop.py — KING DIADEM v3.1
from core.time_engine import compute_time_to_failure, compute_decision_window
from core.silent_canon import SilentCanon

def clamp(v):
    return max(0, min(100, v))

def compute_drift(state):
    return clamp((state["entropy"] * 0.5) + ((100 - state["resource"]) * 0.5))

def update_entropy(state):
    state["entropy"] = clamp(state["entropy"] + state["drift"] * 0.1 - 1.5)
    return state

def update_stability(state):
    state["stability"] = clamp(state["stability"] - state["drift"] * 0.3 + 0.5)
    return state

def stop_the_line(state):
    return state["stability"] < 20 or state["resource"] < 10

def estimate_choice_count(state) -> int:
    score = 0
    if state["stability"] >= 40:
        score += 1
    if state["resource"] >= 20:
        score += 1
    if state.get("intervention") != "restore_minimum_path":
        score += 1
    return score

def run_core(state, user_prompt=None):
    # 1. Physics
    state["drift"] = compute_drift(state)
    state = update_entropy(state)
    state = update_stability(state)

    # 2. Stop-the-line
    if stop_the_line(state):
        return {"status": "HALT", "state": state}

    # 3. Silent Canon check
    choice_count = estimate_choice_count(state)
    canon_result = SilentCanon.evaluate(choice_count)

    if canon_result["status"] == "INTERVENE":
        state["intervention"] = "restore_minimum_path"
    else:
        state.pop("intervention", None)  # Canon บอกนิ่ง ล้าง flag เดิม

    # 4. Time engine
    ttf = compute_time_to_failure(state)
    window = compute_decision_window(ttf)

    return {
        "status": "RUNNING",
        "state": state,
        "time_to_failure": ttf,
        "decision_window": window,
        "canon": canon_result["status"],
        "choice_count": choice_count
    }
