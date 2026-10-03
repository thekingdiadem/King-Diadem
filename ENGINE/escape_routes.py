# ENGINE/escape_routes.py
# KING DIADEM — Escape Route Generator
# คำนวณเส้นทางออกจาก context จริง ไม่ใช่ threshold hardcode

from __future__ import annotations


def generate_escape_routes(
    location: str  = "",
    risk:     float = 5.0,
    context:  dict | None = None,
) -> list:
    """
    สร้าง escape routes จาก risk + context จริง
    แต่ละ route มี priority, feasibility, resource_cost, reason
    """
    ctx        = context if isinstance(context, dict) else {}
    def _f(v, d):
        try:
            return float(v)
        except (TypeError, ValueError):
            return d
    money      = _f(ctx.get("money"),        0)
    energy     = _f(ctx.get("energy"),      50)
    has_vehicle = bool(ctx.get("has_vehicle", False))
    network    = _f(ctx.get("relationships"), 50)  # คนที่ช่วยได้
    waterline  = _f(ctx.get("waterline"),    50)

    risk_norm = min(10.0, max(0.0, _f(risk, 5.0)))
    routes = []

    # ── Route 1: ขอความช่วยเหลือจากเครือข่าย (เสมอ) ─────────────
    network_feasibility = "HIGH" if network > 60 else "MODERATE" if network > 30 else "LOW"
    routes.append({
        "route":         "seek_trusted_network",
        "label":         "ติดต่อคนที่ไว้ใจได้",
        "priority":      1,
        "feasibility":   network_feasibility,
        "resource_cost": "low",
        "reason":        "คนที่รู้จักช่วยได้เร็วกว่าระบบใดๆ",
        "condition":     network > 0,
    })

    # ── Route 2: ออกจากพื้นที่ (ถ้า risk สูง) ────────────────────
    if risk_norm > 6:
        move_feasibility = "HIGH" if (energy > 40 and (money > 0 or has_vehicle)) else "LOW"
        routes.append({
            "route":         "evacuate",
            "label":         "ออกจากพื้นที่ทันที",
            "priority":      2,
            "feasibility":   move_feasibility,
            "resource_cost": "high" if not has_vehicle else "moderate",
            "reason":        f"risk={risk_norm:.1f} เกิน threshold — อยู่ต่อไม่ปลอดภัย",
            "condition":     energy > 20,
        })

    # ── Route 3: ลดการมองเห็น / รอให้สถานการณ์เบาลง ─────────────
    if 4 < risk_norm <= 7:
        routes.append({
            "route":         "reduce_exposure",
            "label":         "ลดการเปิดเผยตัว รอจังหวะ",
            "priority":      2,
            "feasibility":   "HIGH",
            "resource_cost": "low",
            "reason":        "สถานการณ์กลางๆ — รอดูก่อนดีกว่าเสี่ยง",
            "condition":     True,
        })

    # ── Route 4: หาทรัพยากรเพิ่ม ─────────────────────────────────
    if money <= 0 and waterline < 50:
        routes.append({
            "route":         "acquire_resources",
            "label":         "หาทรัพยากรเร่งด่วน (อาหาร/เงิน)",
            "priority":      1,
            "feasibility":   "MODERATE",
            "resource_cost": "low",
            "reason":        "ไม่มีทรัพยากร — ต้องหาก่อนที่จะทำอะไรได้",
            "condition":     True,
        })

    # ── Route 5: คงที่ รักษาสถานะปัจจุบัน ────────────────────────
    if risk_norm <= 4:
        routes.append({
            "route":         "maintain_position",
            "label":         "คงสถานะปัจจุบันไว้",
            "priority":      1,
            "feasibility":   "HIGH",
            "resource_cost": "none",
            "reason":        "risk ต่ำ — การเปลี่ยนแปลงตอนนี้อาจเสี่ยงกว่า",
            "condition":     True,
        })

    # ── Route 6: digital escape (ถ้า physical risk ต่ำ) ──────────
    if risk_norm < 5 and location:
        routes.append({
            "route":         "digital_resource",
            "label":         "ใช้ทรัพยากรออนไลน์",
            "priority":      3,
            "feasibility":   "HIGH",
            "resource_cost": "low",
            "reason":        "หน่วยงาน/ระบบช่วยเหลือออนไลน์เข้าถึงได้ทันที",
            "condition":     True,
        })

    # กรอง condition = False ออก แล้วเรียง priority
    valid = [r for r in routes if r.get("condition", True)]
    valid.sort(key=lambda x: (x["priority"], x["feasibility"] != "HIGH"))

    # FATE: ต้องมีอย่างน้อย 1 เสมอ
    if not valid:
        valid = [{
            "route":         "assess_and_wait",
            "label":         "หยุดและประเมินใหม่",
            "priority":      1,
            "feasibility":   "MODERATE",
            "resource_cost": "none",
            "reason":        "ไม่มีข้อมูลพอ — หยุดก่อนดีกว่าเดินผิดทาง",
            "condition":     True,
        }]

    return valid
