# ENGINE/relationship_engine.py
"""
KING DIADEM — Relationship Engine
FATE™: Human entropy ใน relationship = ส่วนหนึ่งของ waterline
ไม่ใช่แค่ risk += 30 แบบ flat
"""
from __future__ import annotations
from typing import Optional
import time


def analyze_relationship(
    context: dict,
    detail:  bool = True,
) -> dict:
    ctx = context or {}

    depression     = bool(ctx.get("depression",    False))
    fear           = bool(ctx.get("fear",          False))
    dependency     = bool(ctx.get("dependency",    False))
    violence_risk  = bool(ctx.get("violence_risk", False))
    isolation      = bool(ctx.get("isolation",     False))
    trust_broken   = bool(ctx.get("trust_broken",  False))
    financial_ctrl = bool(ctx.get("financial_control", False))

    # ── Weighted risk score ───────────────────────────────────────
    score = 0.0
    flags = []

    if violence_risk:
        score += 80
        flags.append("VIOLENCE_RISK — ความปลอดภัยทางกายภาพ priority 1")
    if financial_ctrl:
        score += 45
        flags.append("FINANCIAL_CONTROL — ถูกควบคุมทรัพยากร")
    if dependency:
        score += 40
        flags.append("DEPENDENCY — ต้องพึ่งพาฝ่ายเดียว")
    if trust_broken:
        score += 35
        flags.append("TRUST_BROKEN — ฐานความสัมพันธ์พัง")
    if isolation:
        score += 30
        flags.append("ISOLATION — ถูกตัดออกจาก network")
    if depression:
        score += 25
        flags.append("DEPRESSION — entropy ส่วนตัวสูง")
    if fear:
        score += 20
        flags.append("FEAR — ตัดสินใจภายใต้ความกลัว")

    score = min(100.0, score)

    # ── Status ───────────────────────────────────────────────────
    if score >= 80:
        status = "collapse_risk"
        action = "ออกจากสถานการณ์นี้ก่อน — ความปลอดภัยทางกายภาพ priority 1"
    elif score >= 60:
        status = "critical"
        action = "หา support system ภายนอก — อย่าแก้คนเดียว"
    elif score >= 40:
        status = "unstable"
        action = "ตั้งขอบเขต + หาคนที่ไว้ใจได้ช่วยประเมิน"
    elif score >= 20:
        status = "warning"
        action = "monitor — สังเกต pattern ที่เริ่มเป็นปัญหา"
    else:
        status = "stable"
        action = "maintain — รักษา trust + communication"

    # ── Entropy impact ────────────────────────────────────────────
    # ความสัมพันธ์ที่มีปัญหา → เพิ่ม personal entropy
    entropy_impact = round(score * 0.4, 1)

    result = {
        "status":          status,
        "risk_score":      round(score, 1),
        "flags":           flags,
        "recommended_action": action,
        "entropy_impact":  entropy_impact,
        "choice_preserved": score < 100,
        "axiom":           "Choice(t) ≥ 1 → collapse = False",
        "timestamp":       time.time(),
    }

    return result
