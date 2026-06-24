# ENGINE/self_learning.py
"""
KING DIADEM — Self Learning Engine
บันทึก + วิเคราะห์ pattern จาก decision history จริง
atomic write + trend detection
"""
from __future__ import annotations
import json
import os
import time
from typing import Optional

MEMORY_FILE = "data/decision_history.json"
MAX_RECORDS = 500


# ── Atomic I/O ────────────────────────────────────────────────────
def load_history() -> list:
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history: list) -> bool:
    try:
        os.makedirs(os.path.dirname(MEMORY_FILE) or ".", exist_ok=True)
        tmp = MEMORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history[-MAX_RECORDS:], f, indent=2, ensure_ascii=False)
        os.replace(tmp, MEMORY_FILE)
        return True
    except Exception:
        return False


# ── Record ────────────────────────────────────────────────────────
def record_decision(result: dict) -> bool:
    history = load_history()
    history.append({
        "survival_score": float(result.get("survival_score", 0)),
        "strategy":       str(result.get("strategy",        "unknown")),
        "location":       str(result.get("location",        "unknown")),
        "risk_level":     str(result.get("risk_level",      "low")),
        "waterline":      float(result.get("waterline",      50)),
        "entropy":        float(result.get("entropy",        40)),
        "resource":       float(result.get("resource",       50)),
        "timestamp":      time.time(),
    })
    return save_history(history)


# ── Analyze ───────────────────────────────────────────────────────
def analyze_patterns() -> dict:
    history = load_history()
    n = len(history)

    if n < 3:
        return {
            "status":   "insufficient_data",
            "records":  n,
            "required": 3,
        }

    scores     = [h["survival_score"] for h in history]
    waterlines = [h.get("waterline", 50) for h in history]
    entropies  = [h.get("entropy",   40) for h in history]

    avg_score = sum(scores) / n
    avg_wl    = sum(waterlines) / n
    avg_ent   = sum(entropies)  / n

    # Trend — เทียบ 20% แรก vs 20% หลัง
    split = max(1, n // 5)
    early_avg = sum(scores[:split])  / split
    late_avg  = sum(scores[-split:]) / split

    if late_avg > early_avg + 5:
        trend = "improving"
    elif late_avg < early_avg - 5:
        trend = "degrading"
    else:
        trend = "stable"

    # Most common strategy
    from collections import Counter
    strategy_counts = Counter(h["strategy"] for h in history)
    top_strategy    = strategy_counts.most_common(1)[0][0]

    # High-risk ratio
    high_risk = sum(1 for h in history if h.get("risk_level") in ("HIGH","CRITICAL"))
    high_risk_ratio = round(high_risk / n, 3)

    # Drift detection — entropy เพิ่มต่อเนื่อง 5 records
    drift_detected = False
    if n >= 5:
        last5_ent = [h.get("entropy", 40) for h in history[-5:]]
        drift_detected = all(last5_ent[i] < last5_ent[i+1] for i in range(4))

    return {
        "status":           "active",
        "records":          n,
        "avg_survival":     round(avg_score, 2),
        "avg_waterline":    round(avg_wl,    2),
        "avg_entropy":      round(avg_ent,   2),
        "trend":            trend,
        "top_strategy":     top_strategy,
        "high_risk_ratio":  high_risk_ratio,
        "drift_detected":   drift_detected,
        "drift_warning":    "entropy เพิ่มต่อเนื่อง 5 รอบ — ตรวจ waterline ทันที" if drift_detected else None,
        "axiom":            "Fail less. Harm less. Restore more.",
    }


# ── Query helpers ─────────────────────────────────────────────────
def get_location_history(location: str) -> list:
    return [h for h in load_history() if h.get("location") == location]

def get_recent(n: int = 10) -> list:
    return load_history()[-n:]
