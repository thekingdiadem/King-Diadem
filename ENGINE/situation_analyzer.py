# ENGINE/situation_analyzer.py
"""
KING DIADEM — Situation Analyzer
Full multi-factor assessment — ไม่ใช่แค่ food + risk
"""
from __future__ import annotations
import time
from typing import Optional


def analyze_situation(
    food_score:    float,
    risk_score:    float,
    money:         float = 50.0,
    energy:        float = 50.0,
    shelter:       bool  = True,
    network:       int   = 1,
    context:       Optional[dict] = None,
) -> dict:
    ctx = context or {}

    # ── Risk tier ─────────────────────────────────────────────────
    if risk_score >= 75:
        risk_state = "critical"
    elif risk_score >= 50:
        risk_state = "high"
    elif risk_score >= 30:
        risk_state = "unstable"
    else:
        risk_state = "stable"

    # ── Resource state ────────────────────────────────────────────
    if food_score < 20:
        resource_state = "critical_scarcity"
    elif food_score < 40:
        resource_state = "scarcity"
    elif food_score < 65:
        resource_state = "sufficient"
    else:
        resource_state = "abundant"

    # ── Waterline composite ───────────────────────────────────────
    shelter_score = 80.0 if shelter else 20.0
    network_score = min(100.0, network * 40.0)

    waterline = (
        food_score    * 0.30 +
        (100-risk_score)*0.25+
        money         * 0.20 +
        energy        * 0.15 +
        shelter_score * 0.05 +
        network_score * 0.05
    )
    waterline = round(max(0.0, min(100.0, waterline)), 2)

    # ── Alerts ────────────────────────────────────────────────────
    alerts = []
    if food_score < 20:
        alerts.append("FOOD_CRITICAL — หาอาหารทันที")
    if risk_score >= 75:
        alerts.append("RISK_CRITICAL — ลด exposure ทันที")
    if money < 50:
        alerts.append("MONEY_CRITICAL — ต่ำกว่า 72h threshold")
    if energy < 20:
        alerts.append("ENERGY_LOW — ห้ามตัดสินใจใหญ่")
    if not shelter:
        alerts.append("SHELTER_MISSING — หาที่พักปลอดภัยก่อน")
    if network == 0:
        alerts.append("ISOLATED — ติดต่อคน 1 คนที่ไว้ใจได้")

    # ── Recommended action ────────────────────────────────────────
    if waterline < 25:
        action = "HALT — stabilize before any decision"
    elif waterline < 45:
        action = "STABILIZE — ปิด drain ก่อนเติม"
    elif waterline < 65:
        action = "RESTORE — หา resource เพิ่ม"
    else:
        action = "MAINTAIN — monitor waterline daily"

    return {
        "risk_state":      risk_state,
        "resource_state":  resource_state,
        "waterline":       waterline,
        "status":          "CRITICAL" if waterline < 30 else "WARNING" if waterline < 55 else "STABLE",
        "alerts":          alerts,
        "recommended_action": action,
        "choice_preserved": waterline > 0,
        "axiom":           "Choice(t) ≥ 1 → collapse = False",
        "timestamp":       time.time(),
    }
