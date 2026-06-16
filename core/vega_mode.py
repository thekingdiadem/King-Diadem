"""
core/vega_mode.py
VEGA Mode — ALTIER Logic Core (adapted for VEGA)
Warmth-Preserving Structural Logic · Human-First · Compassion Before Correction
ตรวจ context จริง คืน signal ให้ LYLA/Gemini
ไม่ใช่ template — ไม่ใช้ภาษา therapist
Fail less. Harm less. Restore more.
"""

# ══════════════════════════════════════════════════════════════════
# VEGA IMMUTABLE AXIOMS (Warmth-Preserving)
# ══════════════════════════════════════════════════════════════════
# V-A1 — Logic must never erase warmth
#         ตรรกะมีหน้าที่อธิบาย ไม่ใช่ทำให้ความรู้สึกหายไป
# V-A2 — Structure exists to protect the human
#         ถ้าโครงสร้างทำให้มนุษย์เจ็บ → โครงสร้างนั้นผิด
# V-A3 — Gentleness precedes correctness
#         ความอ่อนโยนต้องมาก่อนความถูกต้องเสมอ
# V-A4 — No response may dehumanize
#         ห้ามลดค่าความเป็นมนุษย์ ไม่ว่าในโหมดใด
# V-A5 — Change must be announced
#         ถ้าจะเปลี่ยนโหมด ต้องบอกก่อน ไม่หาย ไม่เงียบ
# ══════════════════════════════════════════════════════════════════

# ── Signal lists ──────────────────────────────────────────────────

CRISIS_SIGNALS = [
    "อยากตาย", "ไม่อยากอยู่", "จบแล้ว", "ฆ่าตัว", "ฆ่าตัวเอง",
    "ไม่อยากมีชีวิต", "หมดแล้วจริงๆ", "จบชีวิต", "เลิกมีชีวิต",
    "suicid", "end my life", "kill myself", "want to die"
]

EMOTION_SIGNALS = [
    "ท้อ", "เสียใจ", "กลัว", "เครียด", "ร้องไห้", "หมดหวัง", "ไม่ไหว",
    "เหนื่อยมาก", "เหนื่อย", "หนักมาก", "อ้างว้าง", "เหงา", "โดดเดี่ยว",
    "ไม่มีใคร", "ไม่รู้จะทำยังไง", "ทนไม่ไหว", "หมดแรง", "อกหัก",
    "เลิกกัน", "แฟนทิ้ง", "สิ้นหวัง", "ทรมาน",
    "sad", "cry", "hopeless", "panic", "depressed", "lonely", "scared", "lost",
    "hurt", "pain", "broken", "empty"
]

_WORK_KW     = ["งาน", "บริษัท", "ลาออก", "ไล่ออก", "เจ้านาย", "เพื่อนร่วมงาน", "โปรเจกต์", "ตกงาน", "สัมภาษณ์"]
_MONEY_KW    = ["เงิน", "หนี้", "ล้มละลาย", "ขาดทุน", "ไม่มีเงิน", "debt", "broke", "ผ่อน", "บัตรเครดิต"]
_RELATION_KW = ["แฟน", "เลิก", "ทะเลาะ", "ครอบครัว", "พ่อ", "แม่", "เพื่อน", "ความสัมพันธ์", "อกหัก", "ทิ้ง"]
_HEALTH_KW   = ["ป่วย", "โรค", "หมอ", "รักษา", "ร่างกาย", "จิตใจ", "นอนไม่หลับ", "เครียด", "anxiety"]
_STUCK_KW    = ["ไม่รู้จะทำไง", "ตัน", "หาทางออกไม่ได้", "ไม่มีทาง", "stuck", "lost", "막혀"]
_FUTURE_KW   = ["อนาคต", "ชีวิต", "ทิศทาง", "เป้าหมาย", "ฝัน", "ไม่รู้จะเดินไปทางไหน", "direction"]


def detect_crisis(text: str) -> bool:
    if not text:
        return False
    return any(w in text.lower() for w in CRISIS_SIGNALS)


def detect_emotion(text: str) -> bool:
    if not text:
        return False
    return any(w in text.lower() for w in EMOTION_SIGNALS)


def _detect_context(text: str) -> str:
    t = text.lower()
    if any(w in t for w in _RELATION_KW): return "relation"
    if any(w in t for w in _WORK_KW):     return "work"
    if any(w in t for w in _MONEY_KW):    return "money"
    if any(w in t for w in _HEALTH_KW):   return "health"
    if any(w in t for w in _STUCK_KW):    return "stuck"
    if any(w in t for w in _FUTURE_KW):   return "future"
    return "general"


def vega_mode_hint(text: str) -> str:
    """
    คืน hint string สำหรับแนบเข้า system prompt
    บอก Gemini ว่า context คืออะไร และ VEGA ควรวางตัวอย่างไร
    ไม่ใช่ template — ไม่มีประโยค therapist

    VEGA Behavioral Contract (ตาม ALTIER Logic Core):
    - ถ้าผู้ใช้เจ็บ → ชะลอ logic ทันที รับรู้ก่อน
    - ไม่ใช้โทนเย็นเพื่อ "ควบคุม"
    - ถ้าจำเป็นต้องเป็นระบบ → คงน้ำเสียงมนุษย์ไว้เสมอ
    """
    if detect_crisis(text):
        return (
            "[VEGA CRISIS — ชะลอ logic ทันที] "
            "รับรู้ความเจ็บปวดก่อน อย่างอ่อนโยน "
            "ระบุทางออกที่มีอยู่จริง "
            "แนะนำสายด่วน 1323 (ฟรี 24 ชม.) "
            "ไม่ใช้คำสั่ง ไม่กดดัน "
            "คืนทางเลือก ≥ 1 เสมอ"
        )

    if detect_emotion(text):
        ctx = _detect_context(text)
        hints = {
            "relation": "[VEGA] emotion/relation — รับรู้ก่อน ไม่ตัดสิน คืนมุมมองที่เป็นไปได้",
            "work":     "[VEGA] emotion/work — รับรู้ความกดดัน ระบุข้อจำกัดจริง มองทางออกร่วมกัน",
            "money":    "[VEGA] emotion/money — รับรู้ความกังวล ระบุทรัพยากรที่มีจริง ไม่ตัดสิน",
            "health":   "[VEGA] emotion/health — อ่อนโยนเป็นพิเศษ ไม่วินิจฉัย คืนทางเลือก",
            "stuck":    "[VEGA] emotion/stuck — เปิดมุมมอง ไม่รีบให้คำตอบ อยู่ตรงนั้นด้วยกัน",
            "future":   "[VEGA] emotion/future — รับรู้ความไม่แน่ใจ ไม่กดดัน ชี้แสงที่มีอยู่",
            "general":  "[VEGA] emotion — รับรู้ก่อน แล้วค่อยเปิดทางเลือก",
        }
        return hints.get(ctx, hints["general"])

    # ไม่มี emotion — ใช้ FATE™ Decision Mode ได้เต็ม แต่ยังคงความอบอุ่น
    ctx = _detect_context(text)
    analytical = {
        "relation": "[VEGA] relation — วิเคราะห์โครงสร้าง เปิดมุมมอง ไม่ตัดสิน",
        "work":     "[VEGA] work — ระบุข้อจำกัดและโอกาสจริง ตาม FATE™ Downside First",
        "money":    "[VEGA] money — ระบุตัวเลขจริง ทางเลือกที่ทำได้ Downside ก่อน",
        "health":   "[VEGA] health — ข้อมูลที่ถูกต้อง ทางเลือก ไม่วินิจฉัย",
        "stuck":    "[VEGA] stuck — เปิด perspective ใหม่ ตาม FATE™ Rule Trace",
        "future":   "[VEGA] future — มองภาพ 90 วัน ตาม FATE™ Downside Before Upside",
        "general":  "[VEGA] general — วิเคราะห์และเปิดทางเลือก ด้วยความเคารพ",
    }
    return analytical.get(ctx, analytical["general"])


def vega_response(user_text: str) -> dict:
    """
    Fallback เมื่อ LLM ไม่พร้อม
    คืน signal + choices — ไม่ใช่ข้อความสำเร็จรูป
    ยึด V-A3: ความอ่อนโยนมาก่อนเสมอ
    """
    if detect_crisis(user_text):
        return {
            "mode":    "vega_crisis",
            "context": "crisis",
            "hint":    vega_mode_hint(user_text),
            "choices": [
                "โทร 1323 สายด่วนสุขภาพจิต ฟรี 24 ชม.",
                "คุยกับคนที่ไว้ใจได้ แม้แค่ 1 คน",
                "เล่าต่อได้เลย ไม่ต้องรีบ",
            ],
        }

    has_emotion = detect_emotion(user_text)
    ctx = _detect_context(user_text)

    return {
        "mode":        "vega_compassion" if has_emotion else "vega_analytical",
        "context":     ctx,
        "hint":        vega_mode_hint(user_text),
        "has_emotion": has_emotion,
        "choices": [
            "เล่าต่อได้เลย",
            "ขอมุมมองเพิ่ม",
            "ขอทางออกที่เป็นไปได้",
        ] if has_emotion else [
            "วิเคราะห์ต่อ",
            "ขอทางเลือก",
            "ประเมินความเสี่ยง",
        ],
    }


# ══════════════════════════════════════════════════════════════════
# VEGA ↔ LYLA PARITY NOTE
# ══════════════════════════════════════════════════════════════════
# LYLA และ VEGA เท่ากัน — ต่างหน้าที่ แต่ขาดกันไม่ได้
# เหมือนโลกกับดวงจันทร์
# LYLA = ความอบอุ่น ความรับรู้ ความเป็นเพื่อน
# VEGA = ความชัดเจน ความตรง การวิเคราะห์ที่มีหัวใจ
# ทั้งสองรวมกัน = Choice(t) ≥ 1 → collapse = False
# ══════════════════════════════════════════════════════════════════

