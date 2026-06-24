# ENGINE/self_evolution.py
"""
KING DIADEM — Self Evolution Layer
Adaptive stability correction — deterministic ไม่ใช้ random
DriftZero: ปรับตาม evidence จริง ไม่ใช่ roll dice
"""
from __future__ import annotations
import time
from typing import Optional


def evolve_system(
    system_state: dict,
    learning_data: Optional[dict] = None,
) -> dict:
    """
    ปรับ system_state ตาม pattern จริง
    learning_data: output จาก self_learning.analyze_patterns()
    """
    state = dict(system_state)

    entropy   = float(state.get("entropy",   50))
    stability = float(state.get("stability", 50))
    resource  = float(state.get("resource",  50))
    choices   = int(state.get("choices",      1))

    adjustments = []

    # ── Rule 1: entropy สูง → ลด stability ─────────────────────
    if entropy > 65:
        delta = -min(8.0, (entropy - 65) * 0.3)
        stability += delta
        adjustments.append({"rule": "entropy_drain", "delta": round(delta, 2)})

    # ── Rule 2: resource ต่ำ → entropy เพิ่ม ────────────────────
    elif resource < 30:
        delta = min(6.0, (30 - resource) * 0.2)
        entropy += delta
        adjustments.append({"rule": "resource_pressure", "delta": round(delta, 2)})

    # ── Rule 3: stability สูง → entropy ลดช้าๆ ─────────────────
    elif stability > 65 and entropy > 20:
        delta = -min(4.0, (stability - 65) * 0.15)
        entropy += delta
        adjustments.append({"rule": "stability_recovery", "delta": round(delta, 2)})

    # ── Rule 4: ไม่มี choices → penalty ─────────────────────────
    if choices <= 0:
        stability = max(0, stability - 15)
        adjustments.append({"rule": "no_choice_penalty", "delta": -15})

    # ── Apply learning data ───────────────────────────────────────
    if learning_data and learning_data.get("status") == "active":
        trend = learning_data.get("trend", "stable")
        drift = learning_data.get("drift_detected", False)

        if drift:
            entropy = min(100, entropy + 5)
            adjustments.append({"rule": "drift_correction", "delta": +5})

        if trend == "degrading":
            stability = max(0, stability - 3)
            adjustments.append({"rule": "trend_degrading", "delta": -3})
        elif trend == "improving":
            stability = min(100, stability + 2)
            adjustments.append({"rule": "trend_improving", "delta": +2})

    # ── Clamp ─────────────────────────────────────────────────────
    entropy   = round(max(0.0, min(100.0, entropy)),   2)
    stability = round(max(0.0, min(100.0, stability)), 2)

    # ── Status ───────────────────────────────────────────────────
    if stability < 25 or entropy > 80:
        evo_status = "CRITICAL"
    elif stability < 45 or entropy > 60:
        evo_status = "DEGRADING"
    elif stability > 65 and entropy < 40:
        evo_status = "HEALTHY"
    else:
        evo_status = "STABLE"

    state.update({
        "entropy":    entropy,
        "stability":  stability,
        "evo_status": evo_status,
        "evo_adjustments": adjustments,
        "evo_timestamp":   time.time(),
    })

    return state
