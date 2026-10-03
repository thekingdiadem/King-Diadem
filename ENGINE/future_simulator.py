# ENGINE/future_simulator.py
# KING DIADEM Future Simulator
#
# v2 — แก้ 2 บั๊ก:
#  1. load_model()/build_world_state() ถูกเรียกซ้ำ 200+ ครั้งใน
#     collapse_probability()/forecast() (เพราะ simulate_future
#     เรียกข้างใน loop) -> โหลดครั้งเดียว แคชไว้ ลด I/O
#     ป้องกัน 502/timeout เวลาเรียกจาก request path
#  2. food_patterns/risk_patterns lookup ด้วย str(float) เช่น
#     "52.347..." ไม่ตรงกับ key แบบ int-string เช่น "52"
#     -> ปัดเป็น int ก่อน lookup

import random
from statistics import fmean

from ENGINE.world_model import build_world_state
# learning_engine ไม่มี load_model() — มีแค่ _load_model() (เดิม import ล้ม ทั้งไฟล์ใช้ไม่ได้)
from ENGINE.learning_engine import _load_model as load_model

# FATE Axiom: Determinism — input เดียวกันต้องได้ผลเดียวกัน
# เดิมใช้ random ของทั้ง process → collapse_probability เปลี่ยนทุกครั้งที่เรียก
_SEED = 20260704


_MODEL_CACHE = None
_WORLD_CACHE = None


def _get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        try:
            _MODEL_CACHE = load_model() or {}
        except Exception:
            _MODEL_CACHE = {}
    return _MODEL_CACHE


def _get_world():
    global _WORLD_CACHE
    if _WORLD_CACHE is None:
        try:
            _WORLD_CACHE = build_world_state() or {}
        except Exception:
            _WORLD_CACHE = {}
    return _WORLD_CACHE


def simulate_step(state, model, rng=None):
    rng = rng or random.Random(_SEED)

    risk_patterns = model.get("risk_patterns", {})
    food_patterns = model.get("food_patterns", {})

    food_index = state.get("food_index", 50)
    risk_index = state.get("risk_index", 50)

    food_noise = rng.uniform(-3, 3)
    risk_noise = rng.uniform(-3, 3)

    # v2 FIX: ปัดเป็น int ก่อน lookup (เดิม str(float) ไม่ตรง key)
    food_key = str(int(round(food_index)))
    risk_key = str(int(round(risk_index)))

    if food_key in food_patterns:
        food_noise += food_patterns[food_key] * 0.01

    if risk_key in risk_patterns:
        risk_noise += risk_patterns[risk_key] * 0.01

    food_index = max(0, min(100, food_index + food_noise))
    risk_index = max(0, min(100, risk_index + risk_noise))

    return {
        "food_index": food_index,
        "risk_index": risk_index,
    }


def simulate_future(steps=30, model=None, start_state=None, rng=None):
    """
    v2: รับ model จากภายนอกได้ (ไม่ต้อง load_model() ทุกครั้ง)
    """
    if model is None:
        model = _get_model()
    rng = rng or random.Random(_SEED)

    state = start_state or {"food_index": 50, "risk_index": 50}

    history = []
    for _ in range(int(steps)):
        state = simulate_step(state, model, rng)
        history.append({
            "food_index": state["food_index"],
            "risk_index": state["risk_index"],
        })

    return history


def _run_batch(simulations, steps, model):
    """โหลด model ครั้งเดียว รัน simulation หลายรอบในรอบเดียว"""
    collapse_count = 0
    food_finals = []
    risk_finals = []
    rng = random.Random(_SEED)     # ลำดับสุ่มตายตัว → ผลซ้ำได้ (deterministic replay)

    for _ in range(int(simulations)):
        future = simulate_future(steps, model=model, rng=rng)
        last = future[-1]
        food_finals.append(last["food_index"])
        risk_finals.append(last["risk_index"])
        if last["risk_index"] > 80:
            collapse_count += 1

    return collapse_count, food_finals, risk_finals


def collapse_probability(simulations=200, steps=30, model=None):
    """คง interface เดิม — คืน float (collapse rate)"""
    if model is None:
        model = _get_model()

    collapse_count, _, _ = _run_batch(simulations, steps, model)
    return collapse_count / max(1, int(simulations))


def forecast(simulations=200, steps=30):
    """
    v2: รัน batch เดียว แล้วใช้ผลทั้ง food/risk projection
    + collapse_probability จากชุดเดียวกัน
    (เดิมรัน simulate_future แยก 1 ครั้ง + collapse_probability อีก 200 ครั้ง
     = 201 รอบ, แต่ละรอบโหลด model/world ใหม่ — สิ้นเปลือง I/O มาก)
    """
    model = _get_model()

    collapse_count, food_finals, risk_finals = _run_batch(simulations, steps, model)

    return {
        "food_projection":      float(fmean(food_finals)) if food_finals else 50.0,
        "risk_projection":      float(fmean(risk_finals)) if risk_finals else 50.0,
        "collapse_probability": collapse_count / max(1, int(simulations)),
    }
