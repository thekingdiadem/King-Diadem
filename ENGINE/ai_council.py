# ENGINE/ai_council.py
# KING DIADEM — AI Council (Multi-perspective deterministic voting)
# ไม่มี random — ทุก vote มาจาก logic ที่ตรวจสอบได้
# Council: WATERLINE · VEGA · HALT · CIVIL · FATE

from __future__ import annotations


def _f(v, d: float) -> float:
    """แปลงเป็นตัวเลขแบบไม่ล้ม — None/ข้อความ → ค่าเริ่มต้น"""
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def ai_council(
    location:  str   = "",
    food:      float = 50.0,
    money:     float = 0.0,
    risk:      str   = "moderate",
    context:   dict  | None = None,
) -> dict:
    """
    5-voice council — แต่ละ voice ตัดสินจาก logic ของตัวเอง
    return dict พร้อม votes, consensus, final_action, confidence
    """
    ctx = context or {}
    entropy    = _f(ctx.get("entropy"),    40)
    waterline  = _f(ctx.get("waterline"),  50)
    energy     = _f(ctx.get("energy"),     50)
    has_shelter = ctx.get("safe_place", True) is not False
    money_known = money is not None          # None = ผู้ใช้ไม่ได้บอกเงิน → ไม่นับว่า "ไม่มีเงิน"
    money, food = _f(money, 0.0), _f(food, 50.0)

    risk_score = {"low": 20, "moderate": 45, "high": 70, "critical": 90}.get(
        str(risk or "").lower(), 45
    )

    votes = []

    # ── WATERLINE VOICE — โฟกัส survival floor ────────────────────
    if waterline < 25 or not has_shelter:
        wl_vote = "halt_and_stabilize"
        wl_reason = "waterline ต่ำวิกฤต — ต้องหยุดก่อน"
    elif food <= 0 or (money_known and food > 1 and money < food):
        # food = 0/1 (มีอาหารไหม จาก survivor engine) หรือเป็นค่าอาหาร (>1)
        # เดิมเทียบ money < food ตรงๆ → คนที่มีอาหาร (food=1) แต่เงิน 0 ถูกบอกให้ "หาอาหารก่อน"
        wl_vote = "secure_food_first"
        wl_reason = "ยังไม่มีอาหาร หรือเงินน้อยกว่าค่าอาหาร — ต้องหาอาหารก่อน"
    elif waterline > 70:
        wl_vote = "proceed_with_plan"
        wl_reason = "waterline ดี — ดำเนินแผนได้"
    else:
        wl_vote = "conserve_resources"
        wl_reason = "รักษาทรัพยากรไว้ก่อน"
    votes.append({"voice": "WATERLINE", "vote": wl_vote, "reason": wl_reason})

    # ── VEGA VOICE — strategic analysis ───────────────────────────
    if risk_score >= 70:
        vega_vote = "defensive_position"
        vega_reason = f"risk score {risk_score} — ถอยตั้งรับก่อน"
    elif money > 100 and waterline > 50:
        vega_vote = "calculated_advance"
        vega_reason = "ทรัพยากรพอ waterline ดี — เดินหน้าได้อย่างระมัดระวัง"
    else:
        vega_vote = "hold_position"
        vega_reason = "ยังไม่มีข้อมูลพอจะ advance"
    votes.append({"voice": "VEGA", "vote": vega_vote, "reason": vega_reason})

    # ── HALT VOICE — ตรวจ collapse threshold ──────────────────────
    critical_flags = sum([
        waterline < 20,
        energy < 15,
        risk_score >= 85,
        not has_shelter,
        money_known and money <= 0 and food <= 0,
    ])
    if critical_flags >= 2:
        halt_vote = "HALT"
        halt_reason = f"พบ {critical_flags} critical flags — ห้ามตัดสินใจใหญ่"
    elif critical_flags == 1:
        halt_vote = "caution"
        halt_reason = "มี 1 critical flag — ระวัง"
    else:
        halt_vote = "clear"
        halt_reason = "ไม่มี critical flag"
    votes.append({"voice": "HALT", "vote": halt_vote, "reason": halt_reason})

    # ── CIVIL VOICE — ผลกระทบต่อคนรอบข้าง ───────────────────────
    relationships = _f(ctx.get("relationships"), 50)
    if relationships < 30:
        civil_vote = "rebuild_support_network"
        civil_reason = "ความสัมพันธ์ต่ำ — หาแรงสนับสนุนก่อน"
    elif location and ("อยู่คนเดียว" in str(location) or "alone" in str(location).lower()):
        civil_vote = "seek_community"
        civil_reason = "อยู่คนเดียว — หาคนช่วยได้ก่อนดีกว่า"
    else:
        civil_vote = "maintain_current_network"
        civil_reason = "เครือข่ายโอเค — รักษาไว้"
    votes.append({"voice": "CIVIL", "vote": civil_vote, "reason": civil_reason})

    # ── FATE VOICE — Choice(t) ≥ 1 ────────────────────────────────
    # ตรวจว่ายังมีทางเลือกอยู่ไหม
    choice_count = sum([
        money > 0 or not money_known,
        food > 0,
        has_shelter,
        energy > 20,
        waterline > 30,
    ])
    if choice_count == 0:
        fate_vote = "collapse_imminent"
        fate_reason = "Choice(t) = 0 — collapse inevitable ถ้าไม่ได้รับความช่วยเหลือทันที"
    elif choice_count <= 2:
        fate_vote = "preserve_remaining_choices"
        fate_reason = f"Choice(t) = {choice_count} — อย่าใช้ทรัพยากรที่เหลืออย่างสุ่มสี่สุ่มห้า"
    else:
        fate_vote = "choices_available"
        fate_reason = f"Choice(t) = {choice_count} ≥ 1 — ยังมีทางเลือกพอ"
    votes.append({"voice": "FATE", "vote": fate_vote, "reason": fate_reason})

    # ── Consensus ─────────────────────────────────────────────────
    halt_triggered = halt_vote == "HALT" or fate_vote == "collapse_imminent"

    if halt_triggered:
        final_action = "HALT — หยุดและขอความช่วยเหลือทันที"
        confidence   = 0.95
    elif wl_vote in ("halt_and_stabilize", "secure_food_first"):
        final_action = wl_vote
        confidence   = 0.85
    elif vega_vote == "defensive_position":
        final_action = "defensive_position"
        confidence   = 0.75
    elif choice_count >= 4 and waterline > 60:
        final_action = "proceed_with_plan"
        confidence   = 0.80
    else:
        final_action = "conserve_and_observe"
        confidence   = 0.65

    return {
        "votes":        votes,
        "final_action": final_action,
        "confidence":   round(confidence, 2),
        "halt":         halt_triggered,
        "choice_count": choice_count,
        "waterline":    waterline,
        "risk_score":   risk_score,
        "axiom":        f"Choice(t) = {choice_count} → collapse = {choice_count == 0}",
    }
