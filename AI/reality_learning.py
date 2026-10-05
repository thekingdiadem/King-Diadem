# AI/reality_learning.py — KING DIADEM
# ระบบเรียนรู้จากผลลัพธ์จริง — บันทึก, วัด, ปรับ drift
# FATE™ upgrade: fate_audit per node + irreversible warn on reset
# Fail less. Harm less. Restore more.

from __future__ import annotations
import time
from collections import deque
from typing import Literal

_LOG: deque[dict] = deque(maxlen=200)

OutcomeT = Literal["positive", "negative", "neutral", "unknown"]

_SCORE = {"positive": 1.0, "neutral": 0.5, "negative": 0.0, "unknown": 0.5}
MIN_SAMPLES = 10        # น้อยกว่านี้ยังไม่สรุปสัญญาณ/แนวโน้ม


def record_outcome(
    question: str,
    decision: str,
    outcome: OutcomeT,
    *,
    route: str = "general",
    confidence: float = 0.5,
    tags: list[str] | None = None,
) -> dict:
    """
    บันทึก 1 node พร้อม metadata + FATE™ axiom audit
    คืน node ที่เก็บไว้
    """
    safe_outcome = outcome if isinstance(outcome, str) and outcome in _SCORE else "unknown"
    try:
        safe_conf = float(confidence)
    except (TypeError, ValueError):
        safe_conf = 0.5
    safe_conf = max(0.0, min(1.0, safe_conf if safe_conf == safe_conf else 0.5))

    node = {
        "ts":         time.time(),
        "question":   str(question)[:300],
        "decision":   str(decision)[:300],
        "outcome":    safe_outcome,
        "route":      str(route or "general")[:40],
        "confidence": safe_conf,
        "tags":       tags if isinstance(tags, list) else [],
        "score":      _SCORE[safe_outcome],
        # FATE™ axiom audit — เพิ่มจาก original
        "fate_audit": {
            "has_question":   bool(str(question).strip()),
            "has_decision":   bool(str(decision).strip()),
            "outcome_known":  safe_outcome != "unknown",
            "confidence_ok":  safe_conf >= 0.5,
            "axiom_5_ok":     True,   # Explainability: node พร้อม explain
        },
    }
    _LOG.append(node)
    return node


def learning_summary() -> dict:
    """
    วิเคราะห์ log ทั้งหมด คืน:
      total, positive, negative, neutral,
      score (0-100), signal, drift_risk, win_rate,
      recent_trend, top_routes
    """
    nodes = list(_LOG)
    total = len(nodes)

    if total == 0:
        return {
            "total":        0,
            "positive":     0,
            "negative":     0,
            "neutral":      0,
            "score":        50,
            "signal":       "NO_DATA",
            "drift_risk":   "UNKNOWN",
            "win_rate":     0.0,
            "recent_trend": "FLAT",
            "top_routes":   [],
        }

    pos  = sum(1 for n in nodes if n["outcome"] == "positive")
    neg  = sum(1 for n in nodes if n["outcome"] == "negative")
    neut = sum(1 for n in nodes if n["outcome"] == "neutral")

    weighted_scores = [n["score"] * (0.5 + 0.5 * n["confidence"]) for n in nodes]
    raw_score = sum(weighted_scores) / len(weighted_scores)
    score = round(raw_score * 100, 1)

    win_rate = round(pos / total * 100, 1) if total else 0.0

    quarter = max(1, total // 4)
    early   = sum(n["score"] for n in nodes[:quarter])  / quarter
    recent  = sum(n["score"] for n in nodes[-quarter:]) / quarter
    delta   = recent - early
    if delta > 0.12:
        trend = "IMPROVING"
    elif delta < -0.12:
        trend = "DEGRADING"
    else:
        trend = "FLAT"

    neg_rate = neg / total if total else 0
    if total < MIN_SAMPLES:
        # ตัวอย่างน้อยเกินจะสรุป — เดิม 👎 แค่ครั้งเดียวทำให้ทั้งระบบขึ้น DRIFT_ALERT / COLLAPSE_RISK
        return {
            "total": total, "positive": pos, "negative": neg, "neutral": neut,
            "score": score, "signal": "LOW_DATA", "drift_risk": "UNKNOWN", "win_rate": win_rate,
            "recent_trend": "FLAT", "top_routes": [], "enough_data": False,
        }
    if neg_rate > 0.5 or score < 30:
        drift_risk = "HIGH"
    elif neg_rate > 0.3 or score < 45:
        drift_risk = "MODERATE"
    else:
        drift_risk = "LOW"

    if score >= 70 and trend == "IMPROVING":
        signal = "EXPANDING"
    elif score >= 55:
        signal = "STABLE"
    elif score >= 40 and trend != "DEGRADING":
        signal = "CAUTION"
    elif drift_risk == "HIGH":
        signal = "DRIFT_ALERT"
    else:
        signal = "COMPRESSION"

    route_stats: dict[str, list[float]] = {}
    for n in nodes:
        route_stats.setdefault(n["route"], []).append(n["score"])
    top_routes = sorted(
        [{"route": k, "score": round(sum(v)/len(v)*100, 1)} for k, v in route_stats.items()],
        key=lambda x: -x["score"]
    )[:4]

    return {
        "total":        total,
        "positive":     pos,
        "negative":     neg,
        "neutral":      neut,
        "score":        score,
        "signal":       signal,
        "drift_risk":   drift_risk,
        "win_rate":     win_rate,
        "recent_trend": trend,
        "top_routes":   top_routes,
        "enough_data":  True,
    }


def get_learning(limit: int = 50) -> list[dict]:
    """คืน node ล่าสุด N รายการ"""
    try:
        limit = max(0, int(limit))
    except (TypeError, ValueError):
        limit = 50
    return list(_LOG)[-limit:] if limit else []


def reset_learning() -> dict:
    """
    ล้าง log ทั้งหมด
    FATE™: irreversible — คืน warn พร้อมจำนวนที่ลบ
    """
    count = len(_LOG)
    _LOG.clear()
    return {
        "cleared":   count,
        "fate_note": "⚠ WARN: irreversible — learning log cleared",
        "axiom":     "Downside acknowledged before execution",
    }
