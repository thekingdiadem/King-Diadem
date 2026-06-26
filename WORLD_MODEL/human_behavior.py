"""
WORLD_MODEL/human_behavior.py — KING DIADEM™
Human Behavior Engine — วิเคราะห์พฤติกรรมมนุษย์จากบริบทจริง

Architect: Nithikorn Bunsrang
SCL-7 A3: When conflict arises, gentleness precedes correctness.
UDOK: หยุดที่เวทนา ก่อนมันสร้างตัณหา

❌ REMOVED: keyword match แบบ flat ไม่มี context
✅ REBUILT: multi-layer behavior analysis + UDOK integration
"""

import re
import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# EMOTION PATTERN REGISTRY — ครอบคลุมกว่าเดิมมาก
# ══════════════════════════════════════════════════════════════════

EMOTION_PATTERNS = {
    "joking":        ["555", "ฮ่า", "ขำ", "ตลก", "ล้อเล่น", "มุก", "haha", "lol", "😂", "🤣"],
    "stress":        ["เหนื่อย", "ไม่ไหว", "พัง", "แย่", "หมดแรง", "ล้า", "กดดัน", "stressed", "overwhelmed"],
    "hope":          ["หวัง", "อยาก", "ลอง", "ตั้งใจ", "พยายาม", "wish", "hope", "try"],
    "love":          ["รัก", "คิดถึง", "ห่วง", "ใส่ใจ", "love", "miss", "care"],
    "money_problem": ["เงิน", "จน", "หาเงิน", "หนี้", "ขาดเงิน", "broke", "debt", "ค่าใช้จ่าย"],
    "anger":         ["โกรธ", "หัวร้อน", "ไม่พอใจ", "เซ็ง", "짜증", "angry", "frustrated", "ทนไม่ได้"],
    "fear":          ["กลัว", "กังวล", "วิตก", "ไม่แน่ใจ", "ตื่นตระหนก", "afraid", "scared", "anxious"],
    "sadness":       ["เศร้า", "ร้องไห้", "หดหู่", "เสียใจ", "ผิดหวัง", "sad", "cry", "disappointed"],
    "confusion":     ["งง", "สับสน", "ไม่เข้าใจ", "ไม่รู้", "confused", "lost", "unclear"],
    "determined":    ["ตั้งใจ", "มุ่งมั่น", "จะทำ", "ไม่ยอมแพ้", "determined", "resolve", "commit"],
    "grateful":      ["ขอบคุณ", "ซาบซึ้ง", "ดีใจ", "ขอบใจ", "thankful", "grateful", "appreciate"],
    "lonely":        ["โดดเดี่ยว", "เดียวดาย", "ไม่มีใคร", "alone", "lonely", "isolated"],
}

# ══════════════════════════════════════════════════════════════════
# BEHAVIOR PATTERNS — รูปแบบพฤติกรรมที่ detect ได้
# ══════════════════════════════════════════════════════════════════

BEHAVIOR_SIGNALS = {
    "seeking_help":      ["ช่วย", "ขอความช่วยเหลือ", "ทำยังไง", "help", "how to", "แนะนำ"],
    "venting":           ["ระบาย", "บ่น", "เล่าให้ฟัง", "อยากพูด", "vent", "rant"],
    "decision_making":   ["ตัดสินใจ", "เลือก", "ควรทำ", "decide", "choice", "option"],
    "information":       ["อยากรู้", "ข้อมูล", "หาข้อมูล", "research", "find out", "what is"],
    "crisis":            ["ฉุกเฉิน", "เร่งด่วน", "ด่วน", "urgent", "emergency", "ทันที"],
    "reflection":        ["คิดทบทวน", "มองย้อน", "ทำไม", "reflect", "wonder", "think about"],
}

# ══════════════════════════════════════════════════════════════════
# CONTEXT EXTRACTOR
# ══════════════════════════════════════════════════════════════════

TOPIC_SIGNALS = {
    "money":        ["เงิน", "บาท", "บัญชี", "ธนาคาร", "หนี้", "ลงทุน", "รายได้", "salary", "income"],
    "food":         ["อาหาร", "กิน", "ข้าว", "หิว", "ร้านอาหาร", "food", "eat", "hungry"],
    "health":       ["สุขภาพ", "เจ็บ", "ป่วย", "หมอ", "ยา", "โรค", "health", "sick", "doctor"],
    "work":         ["งาน", "บริษัท", "เจ้านาย", "ลูกค้า", "โปรเจกต์", "work", "job", "boss"],
    "relationship": ["แฟน", "ครอบครัว", "เพื่อน", "ความสัมพันธ์", "partner", "family", "friend"],
    "survival":     ["รอด", "อยู่รอด", "ขาดแคลน", "ไม่มีจะกิน", "survive", "scarce"],
    "technology":   ["โค้ด", "ระบบ", "แอป", "AI", "code", "system", "app", "tech"],
}


# ══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def detect_emotion(text: str) -> str:
    """
    ตรวจ primary emotion จาก text
    คืน emotion label หรือ "neutral"

    UDOK — ช่วยระบุเวทนาก่อนที่มันจะกลายเป็นตัณหา
    """
    if not text:
        return "neutral"
    t = text.lower()

    # priority order — crisis signals ก่อน
    priority = ["fear", "sadness", "anger", "stress", "lonely",
                "money_problem", "hope", "love", "grateful",
                "determined", "confusion", "joking"]

    for emotion in priority:
        words = EMOTION_PATTERNS.get(emotion, [])
        if any(w in t for w in words):
            return emotion

    return "neutral"


def detect_all_emotions(text: str) -> list:
    """
    ตรวจ ALL emotions ที่อยู่ใน text
    คืน list ของ emotions ที่พบ — ไม่แค่ตัวแรก
    """
    if not text:
        return []
    t       = text.lower()
    found   = []
    for emotion, words in EMOTION_PATTERNS.items():
        if any(w in t for w in words):
            hits = [w for w in words if w in t]
            found.append({"emotion": emotion, "matched": hits})
    return found


def detect_behavior(text: str) -> Optional[str]:
    """
    ตรวจ behavior signal — seeking_help / venting / decision_making ฯลฯ
    """
    if not text:
        return None
    t = text.lower()
    for behavior, signals in BEHAVIOR_SIGNALS.items():
        if any(s in t for s in signals):
            return behavior
    return None


def extract_context(text: str) -> dict:
    """
    extract context จาก text — topic, numbers, behavior, emotion
    ครอบคลุมกว่าเดิมมาก
    """
    if not text:
        return {}

    context: dict = {}
    t = text.lower()

    # numbers
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    if numbers:
        context["numbers"] = numbers

    # topic detection
    topics_found = []
    for topic, signals in TOPIC_SIGNALS.items():
        if any(s in t for s in signals):
            topics_found.append(topic)
    if topics_found:
        context["topics"]       = topics_found
        context["primary_topic"] = topics_found[0]

    # emotion
    emotion = detect_emotion(text)
    if emotion != "neutral":
        context["emotion"] = emotion

    # behavior
    behavior = detect_behavior(text)
    if behavior:
        context["behavior"] = behavior

    # emotional signal for SCL-7
    context["has_emotional_signal"] = emotion not in ("neutral", "joking", "grateful", "determined")

    # length signal — ข้อความยาว = อาจต้องการ venting
    context["text_length"] = len(text)
    if len(text) > 200:
        context["likely_venting"] = True

    return context


def analyze_behavior(text: str) -> dict:
    """
    full behavior analysis — ใช้ใน gateway / eternal_snapshot
    คืน emotion + behavior + context + response guidance
    """
    emotion  = detect_emotion(text)
    all_emo  = detect_all_emotions(text)
    behavior = detect_behavior(text)
    context  = extract_context(text)

    # emotional intensity
    intensity = len(all_emo)
    if intensity >= 3:
        emotional_load = "HIGH"
    elif intensity >= 1:
        emotional_load = "MEDIUM"
    else:
        emotional_load = "LOW"

    # response mode (SCL-7)
    if emotion in ("fear", "sadness", "stress", "lonely", "anger"):
        scl_mode = "emotional"
        guidance = "หยุดตรรกะ — รับรู้ความรู้สึกก่อน"
    elif emotion in ("joking", "grateful", "determined"):
        scl_mode = "neutral"
        guidance = "ดำเนินการด้วยตรรกะ — ยังคงความอบอุ่น"
    else:
        scl_mode = "neutral"
        guidance = "ดำเนินการตามปกติ"

    return {
        "primary_emotion":    emotion,
        "all_emotions":       all_emo,
        "behavior":           behavior,
        "context":            context,
        "emotional_load":     emotional_load,
        "scl_mode":           scl_mode,
        "response_guidance":  guidance,
        "pause_logic":        scl_mode == "emotional",
        "analyzed_at":        time.time(),
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # basic emotion
    assert detect_emotion("เหนื่อยมากเลย") == "stress"
    assert detect_emotion("555 ตลกมาก") == "joking"
    assert detect_emotion("กลัวมากเลย") == "fear"
    assert detect_emotion("วิเคราะห์ตลาดหน่อย") == "neutral"

    # all emotions
    r1 = detect_all_emotions("เหนื่อยและกลัวมาก")
    assert len(r1) >= 2

    # behavior
    assert detect_behavior("ช่วยแนะนำหน่อยได้ไหม") == "seeking_help"
    assert detect_behavior("อยากระบายนิดนึง") == "venting"

    # context
    ctx = extract_context("มีปัญหาเรื่องเงินมาก เครียดมากเลย ไม่รู้จะทำยังไง")
    assert "money" in ctx.get("topics", [])
    assert ctx.get("emotion") in ("stress", "money_problem", "confusion")
    assert ctx["has_emotional_signal"] is True

    # full analysis
    analysis = analyze_behavior("กลัวมากเลย ไม่รู้จะทำยังไงกับปัญหานี้")
    assert analysis["pause_logic"] is True
    assert analysis["scl_mode"] == "emotional"

    return {"status": "OK", "module": "human_behavior"}


if __name__ == "__main__":
    import json
    result = analyze_behavior("เหนื่อยมากเลย เครียดเรื่องเงิน ไม่รู้จะทำยังไง ช่วยแนะนำหน่อยได้ไหม")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print(_self_test())
