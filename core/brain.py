"""
core/brain.py — KING DIADEM v2.0
Decision brain — wired to LLM + FATE™ engine
เดิม (v1): hardcode risk, choices คงที่ "A/B/C"
ใหม่ (v2): route-aware, keyword detection, connect to llm_gemini
"""

from typing import Optional

# ── ROUTE RISK DEFAULTS ──────────────────────────────────────────
_ROUTE_BASE_RISK = {
    "general":  0.20,
    "risk":     0.65,
    "survival": 0.55,
    "collapse": 0.80,
    "civil":    0.30,
    "vega":     0.35,
}

# ── KEYWORD RISK MODIFIERS ───────────────────────────────────────
_HIGH_RISK_KW = [
    "เสี่ยง","วิกฤต","พัง","หมดแรง","ล้มละลาย","ตกงาน","หนี้","ไม่ไหว",
    "ฉุกเฉิน","อันตราย","หนีออก","ช่วยด่วน","urgent","crisis","emergency"
]
# เดิม "ตาย" เดี่ยว → "ขำจะตาย" "ร้อนจะตาย" ได้คำตอบวิกฤต 1323 แทนคำตอบจริง
from core.thai_signals import NOT_WANT_TO_LIVE, has as _has

_CRITICAL_KW = [
    "อยากตาย","ฆ่าตัว",NOT_WANT_TO_LIVE,"จบชีวิต","หมดหวังแล้ว",
    "suicid","want to die","end my life"
]

# ── ROUTE CHOICES ────────────────────────────────────────────────
_ROUTE_CHOICES = {
    "general":  ["วิเคราะห์เพิ่ม", "ขอความช่วยเหลือ", "รอดูสถานการณ์"],
    "risk":     ["ประเมินความเสียหาย", "หาทางออกสำรอง", "ลดความเสี่ยงก่อน"],
    "survival": ["ทรัพยากรที่มี", "ขอความช่วยเหลือด่วน", "ลดค่าใช้จ่ายทันที"],
    "collapse": ["หยุดและประเมิน", "ติดต่อผู้เชี่ยวชาญ", "รักษา choice ≥ 1"],
    "civil":    ["หาพันธมิตร", "สื่อสารให้ชัด", "สร้างระบบรองรับ"],
    "vega":     ["วิเคราะห์เชิงกลยุทธ์", "มองภาพ 90 วัน", "ประเมิน downside ก่อน"],
}

_CRITICAL_CHOICES = ["โทร 1323 (สายด่วนสุขภาพจิต ฟรี 24 ชม.)", "หาคนใกล้ชิดทันที", "ไม่ต้องเผชิญคนเดียว"]
_STOP_CHOICES     = ["หยุด", "ถอย", "ออก"]


def run_brain(
    message: str,
    route: str = "general",
    user_email: str = "",
    history: list = None,
) -> dict:
    """
    Main decision brain.
    Returns: {text, risk, choices, route, persona}
    """
    if not message:
        return {
            "text": "ไม่มีข้อมูล",
            "risk": 0.0,
            "choices": _ROUTE_CHOICES.get(route, ["A", "B", "C"]),
            "route": route,
            "persona": "LYLA",
        }

    msg_lower = str(message).lower()
    route = route if route in _ROUTE_BASE_RISK else "general"

    # ── CRITICAL: crisis keywords ───────────────────────────────
    if any(_has(msg_lower, kw) for kw in _CRITICAL_KW):
        return {
            "text": (
                "ฉันได้ยินค่ะ สิ่งที่คุณรู้สึกอยู่ตอนนี้มันหนักมาก "
                "และคุณไม่ต้องแบกมันคนเดียว "
                "โทร 1323 ได้เลยนะคะ ฟรี 24 ชั่วโมง — LYLA ◈"
            ),
            "risk": 1.0,
            "choices": _CRITICAL_CHOICES,
            "route": "collapse",
            "persona": "CRISIS",
        }

    # ── RISK CALCULATION ────────────────────────────────────────
    risk = _ROUTE_BASE_RISK.get(route, 0.20)

    # Keyword modifiers
    high_kw_count = sum(1 for kw in _HIGH_RISK_KW if kw in msg_lower)
    risk = min(0.94, risk + high_kw_count * 0.08)

    # STOP threshold
    if risk >= 0.95:
        return {
            "text": "ระบบตรวจพบความเสี่ยงสูงมาก — แนะนำให้หยุดก่อนดำเนินการใดๆ",
            "risk": risk,
            "choices": _STOP_CHOICES,
            "route": route,
            "persona": "VEGA",
        }

    # ── LLM CALL (ถ้ามี) ────────────────────────────────────────
    ai_text = _call_llm(message, route, user_email, history, risk)

    return {
        "text": ai_text or f"วิเคราะห์: {message[:80]}",
        "risk": round(risk, 3),
        "choices": _ROUTE_CHOICES.get(route, ["A", "B", "C"]),
        "route": route,
        "persona": "VEGA" if route == "vega" else "LYLA",
    }


def _call_llm(
    message: str,
    route: str,
    user_email: str,
    history: Optional[list],
    risk: float,
) -> Optional[str]:
    """เรียก LLM — ถ้า import ไม่ได้ return None (fallback gracefully)"""
    try:
        from core.llm_gemini import get_llm
        llm = get_llm()
        voice_mode = "vega" if route == "vega" else "lyla"
        return llm.generate_with_governance(
            prompt=message,
            route=route,
            voice_mode=voice_mode,
            history=history or [],
            user_email=user_email,
        )
    except Exception as e:
        print(f"[brain] LLM call failed: {type(e).__name__}")
        return None
