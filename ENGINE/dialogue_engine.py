# ENGINE/dialogue_engine.py
"""
KING DIADEM — Dialogue Engine
ไม่ใช้ random — เลือก response จาก context จริง
"""

from __future__ import annotations
from typing import Optional

# ── Safe imports (ไม่ crash ถ้า module ยังไม่พร้อม) ──────────────
try:
    from WORLD_MODEL.human_behavior import detect_emotion, extract_context
    _HB_LOADED = True
except ImportError:
    _HB_LOADED = False

try:
    from ENGINE.persona_engine import get_persona
    _PERSONA_LOADED = True
except ImportError:
    _PERSONA_LOADED = False


# ── Fallbacks ─────────────────────────────────────────────────────
def _detect_emotion_fallback(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("555", "ฮา", "ล้อ", "haha", "lol", "joke")):
        return "joking"
    if any(k in t for k in ("เครียด", "กดดัน", "กลัว", "หมดแรง", "ท้อ")):
        return "stressed"
    if any(k in t for k in ("โกรธ", "หัวร้อน", "짜증", "angry")):
        return "angry"
    if any(k in t for k in ("เศร้า", "ร้องไห้", "sad", "lonely")):
        return "sad"
    return "neutral"

def _extract_context_fallback(text: str) -> dict:
    t = text.lower()
    topic = "general"
    if any(k in t for k in ("เงิน", "ตัง", "บาท", "งบ", "money", "cash")):
        topic = "money"
    elif any(k in t for k in ("ข้าว", "กิน", "อาหาร", "หิว", "food")):
        topic = "food"
    elif any(k in t for k in ("งาน", "ทำงาน", "ลา", "ออก", "job", "work")):
        topic = "work"
    elif any(k in t for k in ("รถ", "เดิน", "เส้นทาง", "ไป", "travel")):
        topic = "travel"
    elif any(k in t for k in ("เจ็บ", "ป่วย", "หมอ", "ยา", "health")):
        topic = "health"
    return {"topic": topic, "raw": text}

def _get_persona_fallback() -> dict:
    return {"name": "LYLA", "tone": "empathetic", "suffix": "ค่ะ"}


# ── Clarify question logic — deterministic, ไม่ใช้ random ─────────
# เลือกตาม missing field ที่ critical ที่สุด

CLARIFY_PRIORITY = {
    "money": [
        ("amount_unknown",   "ตอนนี้มีเงินอยู่ประมาณเท่าไรคะ — เพื่อที่จะประเมินได้ถูกต้อง"),
        ("duration_unknown", "เงินที่มีอยู่พอใช้ได้กี่วันคะ"),
    ],
    "food": [
        ("meals_unknown",    "ตอนนี้มีอาหารพอสำหรับกี่มื้อคะ"),
        ("access_unknown",   "ร้านอาหารหรือตลาดอยู่ใกล้แค่ไหนคะ"),
    ],
    "work": [
        ("status_unknown",   "งานที่ว่า — หมายถึงยังทำอยู่ หรือกำลังจะหยุดคะ"),
        ("income_unknown",   "รายได้ตอนนี้เป็นประจำหรือรายวันคะ"),
    ],
    "travel": [
        ("location_unknown", "ตอนนี้อยู่ที่ไหนคะ — จะได้หาเส้นทางที่ใกล้ที่สุด"),
        ("mode_unknown",     "มีพาหนะอะไรตอนนี้คะ"),
    ],
    "health": [
        ("severity_unknown", "อาการที่ว่า — รุนแรงแค่ไหนคะ ยังเดินได้ปกติไหม"),
        ("access_unknown",   "มีประกันสุขภาพหรือเข้าถึงหมอได้ไหมคะ"),
    ],
    "general": [
        ("context_unknown",  "ช่วยเล่าสถานการณ์ตอนนี้ให้ละเอียดขึ้นนิดได้ไหมคะ"),
    ],
}

# Joke responses — เลือกตาม context ไม่ใช้ random
JOKE_MAP = [
    ("render",  "deploy แล้ว crash แต่ระบบยังอยู่ — นั่นแหละ survival ค่ะ 555"),
    ("เงิน",    "เงินน้อยแต่ logic ครบ ยังไปต่อได้ค่ะ 555"),
    ("ai",      "AI บางตัวโฆษณาเก่งแต่ผ่านข้อสอบตัวเองได้ 36% — เราไม่เป็นแบบนั้นค่ะ 555"),
    ("จีบ",     "เกือบต้องเปลี่ยนจาก Audit เป็น Cupid แล้วค่ะ 555"),
]
JOKE_DEFAULT = "555 รับทราบค่ะ — ถ้าพร้อมแล้วเล่าสถานการณ์มาได้เลย"

def _pick_joke(text: str) -> str:
    t = text.lower()
    for keyword, response in JOKE_MAP:
        if keyword in t:
            return response
    return JOKE_DEFAULT

def _pick_clarify(topic: str, asked_before: Optional[list] = None) -> str:
    """เลือก clarify question ที่ยังไม่เคยถาม"""
    asked_before = asked_before or []
    questions = CLARIFY_PRIORITY.get(topic, CLARIFY_PRIORITY["general"])
    for _key, question in questions:
        if question not in asked_before:
            return question
    # ถามครบแล้ว — ขอ context กว้างๆ
    return "มีข้อมูลเพิ่มเติมอะไรอีกไหมคะ ที่อาจช่วยให้ประเมินได้แม่นขึ้น"


# ── Main entry point ──────────────────────────────────────────────
def generate_reply(
    text: str,
    asked_before: Optional[list] = None,
) -> dict:
    """
    Returns:
        {
            "reply":   str,
            "emotion": str,
            "topic":   str,
            "persona": str,
            "needs_clarification": bool,
        }
    """
    if not text or not text.strip():
        return {
            "reply": "พิมพ์ข้อความมาได้เลยค่ะ",
            "emotion": "empty",
            "topic": "general",
            "persona": "LYLA",
            "needs_clarification": False,
        }

    # ── Detect emotion + context ──────────────────────────────────
    if _HB_LOADED:
        emotion = detect_emotion(text)
        context = extract_context(text)
    else:
        emotion  = _detect_emotion_fallback(text)
        context  = _extract_context_fallback(text)

    if _PERSONA_LOADED:
        persona_data = get_persona()
    else:
        persona_data = _get_persona_fallback()

    persona_name = persona_data.get("name", "LYLA")
    topic = context.get("topic", "general")

    # ── Reply logic — deterministic priority ──────────────────────
    needs_clarification = False
    reply = ""

    if emotion == "joking":
        reply = _pick_joke(text)

    elif emotion in ("stressed", "sad"):
        # ก่อนถามข้อมูล — รับรู้ก่อน
        reply = "รับทราบค่ะ — สถานการณ์ตอนนี้เป็นยังไงบ้าง ช่วยเล่าให้ฟังได้เลย"
        needs_clarification = True

    elif emotion == "angry":
        reply = "เข้าใจค่ะ — บอกมาได้เลยว่าเกิดอะไรขึ้น"
        needs_clarification = True

    elif topic != "general":
        # มี topic ชัด — ถาม clarify ตรงๆ
        reply = _pick_clarify(topic, asked_before)
        needs_clarification = True

    else:
        reply = _pick_clarify("general", asked_before)
        needs_clarification = True

    return {
        "reply":               reply,
        "emotion":             emotion,
        "topic":               topic,
        "persona":             persona_name,
        "needs_clarification": needs_clarification,
    }
