# ENGINE/choice_optimizer.py
# KING DIADEM — Choice Optimizer
# FATE Axiom: Choice(t) ≥ 1 → collapse = False
# เรียงทางเลือกตาม waterline impact จริง ไม่ใช่ score -= 10

from __future__ import annotations


def _f(v, d: float) -> float:
    """แปลงเป็นตัวเลขแบบไม่ล้ม — None/ข้อความ → ค่าเริ่มต้น"""
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def optimize_choice(
    actions: list,
    context: dict | None = None,
) -> list:
    """
    รับ list of action (str หรือ dict) + context
    return list เรียงจาก survivable → risky
    ทุก action มี score, reason, collapse_risk

    context keys ที่ใช้:
        waterline   float 0-100  (สถานะปัจจุบัน)
        entropy     float 0-100
        resources   float 0-100
        time_hours  float        (เวลาที่มี)
        money       float
    """
    ctx = context or {}
    waterline  = _f(ctx.get("waterline"),  50)
    entropy    = _f(ctx.get("entropy"),    40)
    resources  = _f(ctx.get("resources"),  50)
    time_hours = _f(ctx.get("time_hours"),  8)
    money      = _f(ctx.get("money"),       0)

    # ── normalize action → dict ────────────────────────────────
    normalized = []
    for a in (actions or []):
        if isinstance(a, str):
            normalized.append({"action": a, "cost": 0, "time": 1, "reversible": True})
        elif isinstance(a, dict):
            normalized.append(a)

    # ── score each action ──────────────────────────────────────
    scored = []
    for act in normalized:
        name      = act.get("action", str(act))
        cost      = _f(act.get("cost"),      0)
        time_req  = _f(act.get("time"),      1)
        reversible = bool(act.get("reversible", True))

        score = 50.0  # baseline

        # waterline bonus — ถ้า waterline ต่ำ ชอบ action ที่ conservative
        if waterline < 30:
            score += 20 if reversible else -15
        elif waterline > 70:
            score += 10  # มีพื้นที่ risk มากขึ้น

        # entropy penalty — ถ้า entropy สูง action ที่กินแรงมากโดนลงโทษ
        entropy_penalty = (entropy / 100) * time_req * 5
        score -= entropy_penalty

        # resource check
        if cost > 0 and money > 0:
            affordability = min(1.0, money / (cost + 1))
            score += affordability * 15
        elif cost > 0 and money <= 0:
            score -= 25  # ไม่มีเงินแต่ต้องใช้เงิน

        # time check
        if time_req > time_hours:
            score -= 20  # ไม่มีเวลาพอ

        # reversible bonus
        if reversible:
            score += 8

        # collapse risk
        if score < 20:
            collapse_risk = "HIGH"
        elif score < 45:
            collapse_risk = "MODERATE"
        else:
            collapse_risk = "LOW"

        # reason
        if collapse_risk == "HIGH":
            reason = "ทรัพยากรไม่พอหรือ waterline ต่ำเกินไป"
        elif not reversible and waterline < 50:
            reason = "action นี้ย้อนกลับไม่ได้ในสถานการณ์นี้ — ระวัง"
        elif score >= 60:
            reason = "ใช้ทรัพยากรน้อย ย้อนกลับได้ เหมาะกับสถานการณ์"
        else:
            reason = "ทำได้แต่ต้องระวังทรัพยากร"

        scored.append({
            "action":        name,
            "score":         round(max(0.0, min(100.0, score)), 1),
            "collapse_risk": collapse_risk,
            "reversible":    reversible,
            "reason":        reason,
            "cost":          cost,
            "time_required": time_req,
        })

    # เรียงจาก score สูงสุด (survivable ที่สุด) ก่อน
    scored.sort(key=lambda x: x["score"], reverse=True)

    # FATE guarantee: ถ้าไม่มี action ไหนผ่านเลย ยังต้อง return อย่างน้อย 1
    if not scored:
        scored = [{
            "action":        "หยุดและประเมินใหม่",
            "score":         30.0,
            "collapse_risk": "MODERATE",
            "reversible":    True,
            "reason":        "ไม่มีทางเลือกที่ดี — หยุดก่อนดีกว่าเดินต่อโดยไม่มีข้อมูล",
            "cost":          0,
            "time_required": 0.5,
        }]

    return scored
