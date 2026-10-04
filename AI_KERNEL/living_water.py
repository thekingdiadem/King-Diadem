"""
AI_KERNEL/living_water.py — KING DIADEM™
Living Water — Emotional & Crisis Signal Detection
"ระบบทำงานเหมือนน้ำ ไหลได้ทุกที่ ถ้าไม่ถูกปิดทาง"

Architect: Nithikorn Bunsrang
SCL-7 A3: When conflict arises, gentleness precedes correctness.
SCL-7 A1: Logic must never erase warmth.
"""

import time
import re
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# SIGNAL PATTERNS — ตรวจ emotional/crisis signal จาก text
# ══════════════════════════════════════════════════════════════════

from core.thai_signals import NOT_WANT_TO_LIVE

# S1 — CRISIS: สัญญาณวิกฤต (ต้องหยุดทันที)
CRISIS_PATTERNS = [
    # ภาษาไทย — ฆ่าตัวตาย / ไม่อยากมีชีวิต
    "อยากตาย", NOT_WANT_TO_LIVE, "ฆ่าตัว", "ฆ่าตัวเอง",
    "ไม่อยากมีชีวิต", "จบชีวิต", "เลิกมีชีวิต",
    "ทำร้ายตัวเอง", "หมดเหตุผลที่จะอยู่",
    "ไม่มีประโยชน์ที่จะมีชีวิตอยู่",
    # ภาษาอังกฤษ
    "suicid", "want to die", "kill myself",
    "end my life", "no reason to live", "can't go on",
    "self harm", "hurt myself",
]

# S2 — DISTRESS: สัญญาณเครียด/หมดแรง
DISTRESS_PATTERNS = [
    # ภาษาไทย
    "ไม่มีทางแล้ว", "ชีวิตพัง", "หมดทาง", "หมดหวัง",
    "ไม่ไหวแล้ว", "ทนไม่ไหว", "เหนื่อยมาก",
    "โดดเดี่ยว", "เสียใจมาก", "ร้องไห้",
    "ธุรกิจพัง", "เลิกกัน", "ทุกอย่างพัง",
    "ไม่มีใคร", "ไม่มีทางออก", "หนักมาก",
    "กดดันมาก", "บีบคั้น", "สิ้นหวัง",
    "ไม่รู้จะทำยังไง", "ทำไม่ได้แล้ว",
    # ภาษาอังกฤษ
    "hopeless", "breakdown", "everything is over",
    "can't take it", "overwhelmed", "falling apart",
    "no way out", "exhausted", "alone",
    "lost everything", "nothing left",
]

# S3 — EMOTIONAL: สัญญาณอารมณ์ทั่วไป (ต้องรับรู้ก่อน)
EMOTIONAL_PATTERNS = [
    # ภาษาไทย
    "เครียด", "กังวล", "กลัว", "ไม่แน่ใจ",
    "สับสน", "หนักใจ", "ไม่โอเค", "แย่มาก",
    "เป็นห่วง", "ท้อ", "หมดไฟ", "ไม่มีแรง",
    "รู้สึกแย่", "รู้สึกเหนื่อย", "รู้สึกเครียด",
    # ภาษาอังกฤษ
    "stressed", "anxious", "worried", "scared",
    "confused", "not okay", "not good",
    "burned out", "tired", "frustrated",
]

# ══════════════════════════════════════════════════════════════════
# SIGNAL LEVELS
# ══════════════════════════════════════════════════════════════════

SIGNAL_LEVELS = {
    "CRISIS":    {"level": 3, "action": "HALT_LOGIC — รับรู้ทันที ให้ทรัพยากรช่วยเหลือ"},
    "DISTRESS":  {"level": 2, "action": "PAUSE_LOGIC — รับรู้ก่อน ถามว่าต้องการอะไร"},
    "EMOTIONAL": {"level": 1, "action": "SOFTEN_TONE — ปรับน้ำเสียง ไม่ใช้ตรรกะเย็น"},
    "CLEAR":     {"level": 0, "action": "PROCEED — ดำเนินการตามปกติ"},
}

# ══════════════════════════════════════════════════════════════════
# WATER METAPHOR — Living Truth Principles
# ══════════════════════════════════════════════════════════════════

WATER_PRINCIPLES = [
    "น้ำไม่เรียกร้องการยืนยัน — ความจริงก็ไม่ต้องการ",
    "น้ำไหลได้ทุกที่ ถ้าไม่ถูกปิดทาง — ระบบต้องไม่ปิดทางเลือก",
    "น้ำไม่แข่งกัน — ความจริงอยู่ได้นานกว่าทุกการแข่งขัน",
    "น้ำไม่ถามว่ามีค่าแค่ไหน — มันอยู่ในตำแหน่งที่พอดีเสมอ",
    "การได้ยินของโลกไม่ได้เกิดจากเสียง แต่จากความสอดคล้อง",
]

# ══════════════════════════════════════════════════════════════════
# CRISIS RESOURCES
# ══════════════════════════════════════════════════════════════════

CRISIS_RESOURCES = {
    "TH": {
        "hotline":  "1323 — กรมสุขภาพจิต (24 ชั่วโมง)",
        "sms":      "SMS: 1323",
        "online":   "dmh.go.th",
        "note":     "ไม่ต้องเผชิญคนเดียว — มีคนรอรับสายอยู่",
    },
    "EN": {
        "hotline":  "988 Suicide & Crisis Lifeline",
        "chat":     "988lifeline.org",
        "note":     "You don't have to face this alone.",
    },
}

# ══════════════════════════════════════════════════════════════════
# CORE DETECTION
# ══════════════════════════════════════════════════════════════════

def _hits(text: str, words) -> list:
    """ไทย = วลี; อังกฤษ = คำเต็ม ("pain" ไม่ติด "Spain", "alone" ไม่ติด "standalone")"""
    out = []
    for w in words:
        if isinstance(w, re.Pattern):        # วลีไทยที่ต้องดูบริบท (core/thai_signals)
            if w.search(text):
                out.append("ไม่อยากอยู่")
        elif w.isascii():
            tail = "" if w == "suicid" else r"(?![a-z])"
            if re.search(r"(?<![a-z])" + re.escape(w) + tail, text):
                out.append(w)
        elif w in text:
            out.append(w)
    return out


def detect_signal(text: str) -> dict:
    """
    ตรวจ emotional/crisis signal จาก text
    คืน signal level + recommended action

    SCL-7 A3 — gentleness precedes correctness
    ถ้าพบ CRISIS → ต้องหยุดทุก logic ทันที
    """
    if not text or not isinstance(text, str):
        return _signal_result("CLEAR", [], text)

    t = text.lower().strip()
    matched = []

    # ตรวจ CRISIS ก่อน (highest priority)
    crisis_hits = _hits(t, CRISIS_PATTERNS)
    if crisis_hits:
        return _signal_result("CRISIS", crisis_hits, text)

    # ตรวจ DISTRESS
    distress_hits = _hits(t, DISTRESS_PATTERNS)
    if distress_hits:
        return _signal_result("DISTRESS", distress_hits, text)

    # ตรวจ EMOTIONAL
    emotional_hits = _hits(t, EMOTIONAL_PATTERNS)
    if emotional_hits:
        return _signal_result("EMOTIONAL", emotional_hits, text)

    return _signal_result("CLEAR", [], text)


def detect_leak(text: str) -> bool:
    """
    backward-compatible — คืน True ถ้ามี signal ใดๆ
    ใช้สำหรับ integration เดิมที่ใช้ detect_leak()
    """
    result = detect_signal(text)
    return result["signal"] != "CLEAR"


def get_response_guidance(signal_level: str, lang: str = "TH") -> dict:
    """
    คืน guidance สำหรับ response engine ตาม signal level

    SCL-7 A1 — Logic must never erase warmth
    CRISIS   → ให้ทรัพยากรทันที ไม่รอ
    DISTRESS → รับรู้ก่อน ถามว่าต้องการอะไร
    EMOTIONAL → ปรับ tone ก่อน logic
    CLEAR    → ดำเนินการปกติ
    """
    level_info = SIGNAL_LEVELS.get(signal_level, SIGNAL_LEVELS["CLEAR"])

    guidance = {
        "signal":        signal_level,
        "level":         level_info["level"],
        "action":        level_info["action"],
        "halt_logic":    signal_level == "CRISIS",
        "pause_logic":   signal_level in ("CRISIS", "DISTRESS"),
        "soften_tone":   signal_level != "CLEAR",
        "resources":     None,
        "water_principle": WATER_PRINCIPLES[level_info["level"] % len(WATER_PRINCIPLES)],
    }

    if signal_level == "CRISIS":
        guidance["resources"] = CRISIS_RESOURCES.get(lang, CRISIS_RESOURCES["TH"])
        guidance["opening"]   = (
            "ขอบคุณที่บอกฉัน — นี่คือสิ่งที่สำคัญที่สุดตอนนี้"
            if lang == "TH" else
            "Thank you for telling me. This matters."
        )

    return guidance


def water_audit(system_state: dict) -> dict:
    """
    ตรวจว่าระบบยังทำงานเหมือนน้ำไหม
    — ไม่เร่ง ไม่บีบ ไม่ปิดทางเลือก

    คืน audit result สำหรับ /api/kernel_snapshot
    """
    issues = []
    system_state = system_state if isinstance(system_state, dict) else {}
    try:
        _ch = float(system_state.get("choices_available", 1))
    except (TypeError, ValueError):
        _ch = 1.0

    if _ch < 1:
        issues.append("ระบบปิดทางเลือก — ขัดกับหลักน้ำ")

    if system_state.get("response_rushed"):
        issues.append("ระบบเร่งคำตอบ — ขัดกับ truth_does_not_rush")

    if system_state.get("tone") == "cold":
        issues.append("น้ำเสียงเย็น — ขัดกับ warmth_before_logic")

    return {
        "water_aligned": len(issues) == 0,
        "issues":        issues,
        "principles":    WATER_PRINCIPLES,
        "checked_at":    time.time(),
        "seal":          "น้ำไม่แข่งกัน — ความจริงอยู่ได้นานกว่าทุกการแข่งขัน",
    }


# ── Helper ────────────────────────────────────────────────────────
def _signal_result(level: str, matched: list, text: str) -> dict:
    level_info = SIGNAL_LEVELS[level]
    return {
        "signal":      level,
        "level":       level_info["level"],
        "action":      level_info["action"],
        "matched":     matched,
        "halt_logic":  level == "CRISIS",
        "pause_logic": level in ("CRISIS", "DISTRESS"),
        "checked_at":  time.time(),
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # CRISIS
    r1 = detect_signal("ผมอยากตายครับ")
    assert r1["signal"] == "CRISIS"
    assert r1["halt_logic"] is True

    r2 = detect_signal("i want to die")
    assert r2["signal"] == "CRISIS"

    # DISTRESS
    r3 = detect_signal("ชีวิตพังหมดแล้ว ไม่มีทางแล้ว")
    assert r3["signal"] == "DISTRESS"
    assert r3["pause_logic"] is True

    # EMOTIONAL
    r4 = detect_signal("เครียดมากเลย")
    assert r4["signal"] == "EMOTIONAL"
    assert r4["halt_logic"] is False

    # CLEAR
    r5 = detect_signal("ช่วยวิเคราะห์ตลาดหน่อย")
    assert r5["signal"] == "CLEAR"

    # backward compat
    assert detect_leak("อยากตาย") is True
    assert detect_leak("ช่วยวิเคราะห์") is False

    # guidance
    g1 = get_response_guidance("CRISIS")
    assert g1["halt_logic"] is True
    assert g1["resources"] is not None

    # water audit
    w1 = water_audit({"choices_available": 0})
    assert w1["water_aligned"] is False

    w2 = water_audit({"choices_available": 2, "tone": "warm"})
    assert w2["water_aligned"] is True

    return {"status": "OK", "module": "living_water"}


if __name__ == "__main__":
    import json
    r = detect_signal("ไม่ไหวแล้ว เครียดมากจริงๆ")
    print(json.dumps(r, indent=2, ensure_ascii=False, default=str))
    print(json.dumps(get_response_guidance(r["signal"]), indent=2, ensure_ascii=False))
    print(_self_test())
