# ENGINE/survival_advisor.py
"""
KING DIADEM — Survival Advisor
FATE™ Axiom 4: Downside before Upside
ทางรอดก่อน ความรู้ทีหลัง
"""

from __future__ import annotations
from typing import Optional


# ── Thresholds ────────────────────────────────────────────────────
FOOD_CRITICAL  = 1    # มื้อ — ต่ำกว่านี้ = critical
FOOD_LOW       = 3
MONEY_CRITICAL = 50   # บาท
MONEY_LOW      = 200
RISK_HIGH      = 7    # 0-10
RISK_MODERATE  = 4


# ── Core survival scorer ──────────────────────────────────────────
def survival_advisor(
    food: float,
    money: float,
    risk: float,
    energy: float = 50,
    shelter: bool = True,
    network: int  = 1,   # จำนวนคนที่ติดต่อได้
) -> dict:
    """
    คำนวณ survival score จาก inputs จริง
    ไม่ใช้ hardcode score -= 20 แบบ flat
    """
    score    = 100.0
    actions  = []
    warnings = []

    # ── Food ──────────────────────────────────────────────────────
    if food <= FOOD_CRITICAL:
        score -= 35
        actions.append({
            "priority": 1,
            "action":   "หาอาหารทันที — entropy จะพุ่งถ้า energy = 0",
            "urgency":  "IMMEDIATE",
        })
        warnings.append("FOOD_CRITICAL")
    elif food <= FOOD_LOW:
        score -= 15
        actions.append({
            "priority": 2,
            "action":   "secure อาหารสำรองอย่างน้อย 3 มื้อ",
            "urgency":  "HIGH",
        })
        warnings.append("FOOD_LOW")

    # ── Money ─────────────────────────────────────────────────────
    if money <= MONEY_CRITICAL:
        score -= 30
        actions.append({
            "priority": 1,
            "action":   "หารายได้ทันที — threshold ต่ำกว่า 72h survival",
            "urgency":  "IMMEDIATE",
        })
        warnings.append("MONEY_CRITICAL")
    elif money <= MONEY_LOW:
        score -= 12
        actions.append({
            "priority": 3,
            "action":   "เพิ่มรายได้หรือลดรายจ่ายให้อยู่เกิน 72h",
            "urgency":  "HIGH",
        })
        warnings.append("MONEY_LOW")

    # ── Risk ──────────────────────────────────────────────────────
    if risk >= RISK_HIGH:
        score -= 25
        actions.append({
            "priority": 1,
            "action":   "ลด exposure — ย้ายออกจากจุดเสี่ยงถ้าทำได้",
            "urgency":  "IMMEDIATE",
        })
        warnings.append("RISK_HIGH")
    elif risk >= RISK_MODERATE:
        score -= 10
        actions.append({
            "priority": 3,
            "action":   "monitor สถานการณ์ — เตรียม exit route ไว้",
            "urgency":  "MODERATE",
        })
        warnings.append("RISK_MODERATE")

    # ── Energy ────────────────────────────────────────────────────
    if energy < 20:
        score -= 15
        actions.append({
            "priority": 2,
            "action":   "พักก่อน — decision quality พังถ้า energy < 20",
            "urgency":  "HIGH",
        })
        warnings.append("ENERGY_CRITICAL")

    # ── Shelter ───────────────────────────────────────────────────
    if not shelter:
        score -= 20
        actions.append({
            "priority": 1,
            "action":   "หาที่พักปลอดภัยก่อนทุกอย่าง",
            "urgency":  "IMMEDIATE",
        })
        warnings.append("SHELTER_MISSING")

    # ── Network ───────────────────────────────────────────────────
    if network == 0:
        score -= 10
        actions.append({
            "priority": 3,
            "action":   "ติดต่อคน 1 คนที่ไว้ใจได้ — อย่าแก้คนเดียวตอน entropy สูง",
            "urgency":  "MODERATE",
        })
        warnings.append("ISOLATED")

    score = max(0.0, min(100.0, score))

    # ── Survival tier ─────────────────────────────────────────────
    if score >= 75:
        tier   = "STABLE"
        expand = True
    elif score >= 50:
        tier   = "SUSTAIN"
        expand = False
    elif score >= 25:
        tier   = "CRITICAL"
        expand = False
    else:
        tier   = "COLLAPSE_RISK"
        expand = False

    # ── Sort actions by priority ──────────────────────────────────
    actions.sort(key=lambda x: x["priority"])

    if expand:
        actions.append({
            "priority": 9,
            "action":   "Stable — สามารถ expand options หรือ invest ได้",
            "urgency":  "LOW",
        })

    return {
        "survival_score":       round(score, 1),
        "tier":                 tier,
        "warnings":             warnings,
        "recommended_actions":  actions,
        "choice_preserved":     score > 0,
        "axiom":                "Choice(t) ≥ 1 → collapse = False",
    }


# ── Adapter — รับ pattern จาก DecisionEngine ─────────────────────
def advise(pattern: dict) -> dict:
    """
    Map DecisionEngine pattern → survival_advisor inputs
    pattern keys: resource, stability, entropy, + optional overrides
    """
    try:
        resource  = float(pattern.get("resource",  50))
        entropy   = float(pattern.get("entropy",   40))

        # ถ้า pattern ส่ง raw values มาตรงๆ ใช้เลย
        food    = float(pattern.get("food",   resource / 25))   # 0-4
        money   = float(pattern.get("money",  resource * 10))   # scale to บาท
        risk    = float(pattern.get("risk",   entropy  / 10))   # 0-10
        energy  = float(pattern.get("energy", 100 - entropy))
        shelter = bool(pattern.get("shelter", True))
        network = int(pattern.get("network",  1))

        return survival_advisor(
            food=food,
            money=money,
            risk=risk,
            energy=energy,
            shelter=shelter,
            network=network,
        )
    except Exception as e:
        return {"error": f"survival_advisor fail: {str(e)}"}
