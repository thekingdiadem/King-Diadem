# ENGINE/ai_needs.py
# KING DIADEM — AI Needs Detector
# ตรวจ context ที่ขาดหายไปก่อน LYLA จะตอบ
# ไม่ใช่ hardcode topic check — วิเคราะห์จาก waterline + flags จริง

from __future__ import annotations


def ai_needs(context: dict) -> dict:
    """
    วิเคราะห์ว่า LYLA ต้องการข้อมูลอะไรเพิ่มก่อนตอบ
    return dict พร้อม needs list, urgency, และ can_proceed
    """
    needs    = []
    critical = []

    waterline  = context.get("waterline")
    entropy    = context.get("entropy")
    energy     = context.get("energy")
    money      = context.get("money")
    food       = context.get("food_access")
    shelter    = context.get("safe_place")
    mental     = context.get("mental_state")
    route      = str(context.get("route", "general")).lower()
    user_input = str(context.get("input", "")).strip()

    # ── Critical gaps (ถ้าขาดนี้ LYLA อาจตอบผิด direction) ────────
    if waterline is None:
        critical.append({
            "need":   "waterline",
            "reason": "ไม่รู้ว่าผู้ใช้อยู่ในสถานการณ์ปลอดภัยแค่ไหน",
            "ask":    "ตอนนี้รู้สึกเป็นยังไงบ้าง พอมีแรงไหม?",
        })

    if energy is None and route in ("survival", "collapse"):
        critical.append({
            "need":   "energy",
            "reason": "survival route ต้องรู้ว่าร่างกายพร้อมแค่ไหน",
            "ask":    "วันนี้นอนหลับได้ไหม มีแรงทำอะไรไหม?",
        })

    if money is None and route in ("survival", "business", "general"):
        needs.append({
            "need":   "money",
            "reason": "ไม่รู้ว่าทรัพยากรพอสำหรับ action ที่จะแนะนำไหม",
            "ask":    "ตอนนี้มีงบประมาณอยู่บ้างไหม?",
        })

    # ── Survival-specific gaps ─────────────────────────────────────
    if route == "survival":
        if food is None:
            critical.append({
                "need":   "food_access",
                "reason": "survival mode ต้องรู้ว่าอาหารพร้อมไหม",
                "ask":    "ตอนนี้มีอาหารกินไหม?",
            })
        if shelter is None:
            critical.append({
                "need":   "safe_place",
                "reason": "ต้องรู้ว่ามีที่ปลอดภัยไหม",
                "ask":    "ตอนนี้อยู่ที่ไหน ปลอดภัยไหม?",
            })

    # ── Mental state ───────────────────────────────────────────────
    if mental is None and route in ("survival", "collapse"):
        needs.append({
            "need":   "mental_state",
            "reason": "รู้ว่าผู้ใช้รับไหวแค่ไหนก่อนเสนอ action",
            "ask":    "ตอนนี้รู้สึกไหวไหม หรือหนักเกินไป?",
        })

    # ── Input too vague ────────────────────────────────────────────
    if len(user_input) < 10 and not critical:
        needs.append({
            "need":   "more_context",
            "reason": "ข้อความสั้นเกิน LYLA อาจตอบผิดทิศ",
            "ask":    "ช่วยเล่าให้ฟังอีกนิดได้ไหม เกิดอะไรขึ้น?",
        })

    # ── Urgency ───────────────────────────────────────────────────
    if critical:
        urgency     = "HIGH"
        can_proceed = False
        message     = "LYLA ต้องการข้อมูลสำคัญก่อนตอบ — ถ้าตอบตอนนี้อาจผิดทิศทาง"
    elif needs:
        urgency     = "MODERATE"
        can_proceed = True
        message     = "LYLA ตอบได้แต่ถ้ามีข้อมูลเพิ่มจะแม่นขึ้น"
    else:
        urgency     = "LOW"
        can_proceed = True
        message     = "context ครบพอ — LYLA พร้อมตอบ"

    return {
        "critical_needs": critical,
        "optional_needs": needs,
        "urgency":        urgency,
        "can_proceed":    can_proceed,
        "message":        message,
        "total_gaps":     len(critical) + len(needs),
    }
