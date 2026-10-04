# ENGINE/risk_engine.py
# KING DIADEM — Risk Engine
# เพิ่ม assess(pattern) ให้ตรงกับที่ app.py และ engine_router เรียก
# คง evaluate_risk(text) ไว้เพื่อ backward compat
from __future__ import annotations
from core.thai_signals import NOT_WANT_TO_LIVE, NO_MONEY_ESSENTIAL, has as _has
from core.lang_signals import SELF_HARM_INTL

_SELF_HARM = ("อยากตาย", "ฆ่าตัวตาย", "ฆ่าตัวเอง", "ทำร้ายตัวเอง", "ไม่อยากมีชีวิต",
              NOT_WANT_TO_LIVE, "จบชีวิต", "kill myself", "suicide", "self-harm", "end my life")
_SELF_HARM += SELF_HARM_INTL   # อังกฤษ จีน ญี่ปุ่น เกาหลี สเปน (core/lang_signals)
_SURVIVAL  = ("อดข้าว", "ไม่มีข้าวกิน", NO_MONEY_ESSENTIAL, "เงินหมด", "ไม่มีที่อยู่", "ถูกไล่ออก")
# ขาดปัจจัยพื้นฐาน (อาหาร/ที่อยู่) → ต้องไปเส้นทาง survival แม้ไม่ได้กรอก context
_BASIC_NEEDS = ("อดข้าว", "ไม่มีข้าวกิน", "ไม่มีอะไรกิน", "ไม่ได้กินข้าว", "ไม่มีที่อยู่", "ไม่มีที่นอน",
                "นอนข้างถนน", "ถูกไล่ออกจากบ้าน")
_STRESS    = ("พัง", "ล่ม", "ไม่ไหว", "ทนไม่ไหว", "หมดแรง")
_URGENT    = ("ด่วน", "เดี๋ยวนี้", "ทันที", "immediately", "urgent")


def _f(v, d):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def evaluate_risk(text: str) -> dict:
    """ประเมิน risk จาก text — scale score 0-10

    v2: เดิมนับคำของงาน dev ("error", "500", "deploy", "now") เป็นความเสี่ยงของคน
    ("เหลือ 500 บาท" = เสี่ยง, "know" ติด "now") และ "ตาย" แบบ substring ได้แค่ +3 (ระดับกลาง)
    ตอนนี้: สัญญาณทำร้ายตัวเอง = critical ทันที
    """
    t = str(text or "").casefold()
    score = 0
    self_harm = any(_has(t, k) for k in _SELF_HARM)
    if self_harm:
        score += 6
    basic_needs = any(k in t for k in _BASIC_NEEDS)
    if basic_needs or any(_has(t, k) for k in _SURVIVAL):
        score += 3
    if any(k in t for k in _STRESS):
        score += 2
    if any(k in t for k in _URGENT):
        score += 1
    level = "critical" if self_harm else "high" if score >= 4 else "medium" if score >= 2 else "low"
    return {
        "score": score,
        "level": level,
        "pause": level in ("high", "critical"),
        "self_harm": self_harm,
        "basic_needs": basic_needs,
    }

def assess(pattern: dict) -> dict:
    """
    ประเมิน risk จาก pattern dict (entropy/resource/stability/input)
    คืน dict ที่ engine_router และ decision_engine ใช้ได้ทันที
    scale risk_score 0-100 เหมือนกับ emptiness_guard
    """
    if not isinstance(pattern, dict):
        pattern = {}
    entropy   = _f(pattern.get("entropy"),   40)
    resource  = _f(pattern.get("resource"),  50)
    stability = _f(pattern.get("stability"), 60)
    risk_score = entropy * 0.5 + (100.0 - resource) * 0.5
    if risk_score >= 75:
        level = "CRITICAL"
    elif risk_score >= 55:
        level = "HIGH"
    elif risk_score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"
    # ข้อความดิบของผู้ใช้ — "input" ใน /run คือ prompt ที่ระบบต่อบริบทแล้ว
    text_risk = evaluate_risk(str(pattern.get("raw_input") or pattern.get("input", "")))
    if text_risk["level"] == "critical":
        level = "CRITICAL"
        risk_score = max(risk_score, 85.0)
    elif text_risk["level"] == "high" and level not in ("CRITICAL", "HIGH"):
        level = "HIGH"
        risk_score = max(risk_score, 60.0)
    remaining_choices = max(1, int((100 - risk_score) / 20))
    return {
        "risk_score":        round(risk_score, 2),
        "level":             level,
        "decision_level":    level,
        "remaining_choices": remaining_choices,
        "stability":         stability,
        "resource":          resource,
        "entropy":           entropy,
        "drift":             _f(pattern.get("drift"), 0),
        "text_risk":         text_risk,
    }

# ── ALIASES — backward compat ─────────────────────────────────────
# universal_engine imports analyze_risk → map ไป assess
def analyze_risk(data) -> dict:
    """Alias สำหรับ universal_engine — delegates to assess()"""
    if isinstance(data, str):
        return evaluate_risk(data)
    if isinstance(data, dict):
        return assess(data)
    return assess({})

# อื่นๆ ที่อาจ import ชื่อต่างกัน
assess_risk = assess
risk_assess = assess
