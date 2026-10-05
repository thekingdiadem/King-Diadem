# AI/planetary_dashboard.py — KING DIADEM
# FIX: graceful import fallback ทุกตัว — ไม่มี import ที่พังระบบ

from __future__ import annotations


def planetary_status() -> dict:
    """
    รวม signal จากทุก layer ที่มีอยู่จริง
    ถ้า module ไหนไม่โหลดได้ → ใช้ default ไม่พัง
    """
    # ── freedom_index ─────────────────────────────────────────
    freedom: float = 50.0
    try:
        from AI.freedom_signal import freedom_index  # type: ignore
        freedom = float(freedom_index())
    except Exception:
        try:
            from ENGINE.freedom_signal import freedom_index  # type: ignore
            freedom = float(freedom_index())
        except Exception:
            pass

    # ── learning summary ──────────────────────────────────────
    learning: dict = {"total": 0, "score": 50, "signal": "NO_DATA",
                      "drift_risk": "UNKNOWN", "win_rate": 0.0}
    try:
        from AI.reality_learning import learning_summary
        result = learning_summary()
        if isinstance(result, dict):
            learning = result
    except Exception:
        pass

    # ── decision nodes ────────────────────────────────────────
    decision_count: int = 0
    try:
        from AI.decision_memory import get_memory  # type: ignore
        decision_count = len(get_memory())
    except Exception:
        try:
            from ENGINE.memory import get_memory  # type: ignore
            decision_count = len(get_memory())
        except Exception:
            pass

    # ── network nodes ─────────────────────────────────────────
    node_count: int = 0
    try:
        from NETWORK.node_registry import get_nodes  # type: ignore
        node_count = len(get_nodes())
    except Exception:
        pass

    # ── civilization nodes ────────────────────────────────────
    civ_nodes: int = 0
    try:
        from AI.civilization_engine import get_nodes as get_civ_nodes  # type: ignore
        civ_nodes = len(get_civ_nodes())
    except Exception:
        pass

    # ── intent engine check ───────────────────────────────────
    intent_ok: bool = False
    try:
        from AI.intent_engine import analyze_intent  # noqa: F401
        intent_ok = True
    except Exception:
        pass

    # ── status signal ─────────────────────────────────────────
    try:
        learn_score: float = float(learning.get("score", 50))
    except (TypeError, ValueError):
        learn_score = 50.0
    drift_risk:  str   = str(learning.get("drift_risk", "UNKNOWN"))
    if learning.get("enough_data") is False or not learning.get("total"):
        learn_score = 50.0          # ยังไม่มีข้อมูลพอ = กลางๆ ไม่ใช่ "ใกล้ล่มสลาย"

    if freedom < 25 or learn_score < 25:
        status = "COLLAPSE_RISK"
    elif freedom < 40 or learn_score < 35:
        status = "COMPRESSION"
    elif freedom > 70 and learn_score > 65:
        status = "EXPANSION"
    else:
        status = "STABLE"

    lyla_signal = (
        "INTERVENE" if status == "COLLAPSE_RISK" else
        "MONITOR"   if status == "COMPRESSION"   else
        "OBSERVE"
    )

    choice_collapse = "HIGH" if freedom < 25 else "MODERATE" if freedom < 40 else "LOW"

    return {
        "planetary_status":    status,
        "freedom_index":       round(freedom, 1),
        "learning_score":      learn_score,
        "learning_signal":     learning.get("signal", "NO_DATA"),
        "drift_risk":          drift_risk,
        "win_rate":            learning.get("win_rate", 0.0),
        "recent_trend":        learning.get("recent_trend", "FLAT"),
        "decision_nodes":      decision_count,
        "civilization_nodes":  civ_nodes,
        "network_nodes":       node_count,
        "intent_engine_ok":    intent_ok,
        "learning":            learning,
        # 3 ค่านี้เป็นค่าคงที่ในโค้ด ไม่ได้วัดจากแหล่งจริง — ระบุให้ผู้อ่านรู้
        "global_food_security":"DECLINING",
        "water_stress_index":  72.4,
        "energy_drift_daily":  0.1,
        "static_reference":    ["global_food_security", "water_stress_index", "energy_drift_daily"],
        "choice_collapse_risk":choice_collapse,
        "lyla_signal":         lyla_signal,
    }
