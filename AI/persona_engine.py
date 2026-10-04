# AI/persona_engine.py — KING DIADEM
# LYLA Persona Engine v2.0
# โทน: อบอุ่น สงบ ชัดเจน มีน้ำหนัก — ไม่ใช่ chatbot
# ปฏิจสมุปบาท: อ่าน intent จากเหตุปัจจัย ไม่ใช่ pattern matching ล้วนๆ

import re


class PersonaEngine:

    # ── INTENT ──────────────────────────────────────────────────
    INTENT_MAP = [
        # เดิม "ฆ่า" "ตาย" "จบแล้ว" "หมดแล้ว" "ทนไม่ไหว" → "ฆ่าเวลา" "ขำจะตาย" "ข้าวหมดแล้ว" = crisis
        ("crisis", [
            "ฆ่าตัว", "อยากตาย", "ไม่อยากอยู่แล้ว", "ไม่อยากมีชีวิต", "จบชีวิต", "ทำร้ายตัวเอง",
            r"\bsuicid", r"\bkill myself\b", r"\bwant to die\b", r"\bend my life\b",
        ]),
        ("survival", [
            "ตกงาน", "ไม่มีเงิน", "หนี้", "ค่าเช่า", "กินข้าวไม่ได้",
            "ทรัพยากรหมด", "รอดยาก", "ฉุกเฉิน", "พังหมด",
            r"\bno money\b", r"\bbankrupt\b", r"\bevicted\b", r"\bsurvive\b",
        ]),
        ("business", [
            "ธุรกิจ", "บริษัท", "ตลาด", "หุ้น", "ลงทุน", "กำไร", "ขาดทุน",
            "เงินทุน", "ลูกค้า", "ยอดขาย", "startup",
            r"\bmarket\b", r"\brevenue\b", r"\bprofit\b", r"\binvest\b",
        ]),
        ("life", [
            "ความสัมพันธ์", "แฟน", "ครอบครัว", "เพื่อน",
            "อนาคต", "ความฝัน", "ตัวตน", "เครียด", "เหนื่อย",
            r"\brelationship\b", r"\bfamily\b", r"\bfriend\b",
        ]),
    ]

    # ── STYLE ────────────────────────────────────────────────────
    STYLE_MAP = [
        ("playful",  ["เริ่ด", "โคตร", "มึง", "กู", "ว้าว", "555", "lol", "haha"]),
        ("formal",   ["ครับ", "ค่ะ", "กรุณา", "ขอบคุณ", "เรียน"]),
        ("urgent",   ["ด่วน", "ตอนนี้", "ทันที", "เร่งด่วน", "asap", "urgent"]),
        ("confused",  ["ไม่รู้", "ไม่แน่ใจ", "งง", "confused", "stuck", "ไม่เข้าใจ"]),
    ]

    # ── WATERLINE ────────────────────────────────────────────────
    WATERLINE_MAP = {
        "crisis":   "BREACHED",
        "survival": "AT_RISK",
        "business": "NOMINAL",
        "life":     "DECLINING",
        "general":  "NOMINAL",
    }

    CHOICE_FLOOR_MAP = {
        "crisis":   0,
        "survival": 1,
        "business": 2,
        "life":     1,
        "general":  3,
    }

    # ── TONE TEMPLATES ───────────────────────────────────────────
    # โทนที่ LYLA/VEGA ใช้ตาม intent — ไม่ใช่ template แต่เป็น hint ให้ LLM
    TONE_HINT = {
        "crisis":   "รับรู้ก่อน ไม่รีบ ไม่ push — คืนทางออกที่เล็กที่สุดก่อน",
        "survival": "ระบุทรัพยากรจริง — อย่า dump ข้อมูล — ทำได้วันนี้อะไรบ้าง",
        "business": "วิเคราะห์จากเหตุปัจจัย — เปิดทางเลือก ≤3 — ไม่ฟันธง",
        "life":     "รับรู้ก่อน 1 ประโยค — ถามกลับได้แค่หนึ่งคำถาม",
        "general":  "ตอบตรง กระชับ — ไม่ dump — ถ้าถามสั้น ตอบสั้น",
    }

    # ────────────────────────────────────────────────────────────

    def detect_intent(self, text: str) -> str:
        t = str(text or "").lower()
        for intent, patterns in self.INTENT_MAP:
            for pat in patterns:
                if re.search(pat, t):
                    return intent
        return "general"

    def detect_style(self, text: str) -> str:
        t = str(text or "").lower()
        for style, keywords in self.STYLE_MAP:
            for kw in keywords:
                if kw in t:
                    return style
        return "neutral"

    def observe(self, text: str) -> dict:
        """
        Full observation — คืน waterline + tone hint + action signal
        ใช้เป็น context ให้ LLM ไม่ใช่ hardcode คำตอบ
        """
        intent = self.detect_intent(text)
        style  = self.detect_style(text)
        wl     = self.WATERLINE_MAP.get(intent, "NOMINAL")
        floor  = self.CHOICE_FLOOR_MAP.get(intent, 2)
        tone   = self.TONE_HINT.get(intent, self.TONE_HINT["general"])

        if intent == "crisis":
            action = "INTERVENE"
            note   = "Choice collapse risk — Stop-the-Line — คืนทางออกก่อนทุกอย่าง — แนะนำ 1323"
        elif intent == "survival":
            action = "STABILIZE"
            note   = "Waterline at risk — ระบุทรัพยากรจริงก่อน optimize"
        elif wl == "DECLINING":
            action = "MONITOR"
            note   = "Drift สะสม — รับรู้ก่อน วิเคราะห์ทีหลัง"
        else:
            action = "OBSERVE"
            note   = "No critical signal — ตอบตรง ไม่เกินที่ถาม"

        return {
            "intent":       intent,
            "style":        style,
            "waterline":    wl,
            "choice_floor": floor,
            "action":       action,
            "tone_hint":    tone,
            "note":         note,
            "law":          "Fail less. Harm less. Restore more.",
        }

    def build_context_note(self, text: str) -> str:
        """
        คืน string สำหรับแนบเข้า additional_context ใน generate_with_governance
        ทำให้ LLM รู้ว่า intent คืออะไร และควรโทนแบบไหน
        """
        obs = self.observe(text)
        parts = [
            f"[PERSONA] intent={obs['intent']} style={obs['style']}",
            f"waterline={obs['waterline']} action={obs['action']}",
            f"tone: {obs['tone_hint']}",
        ]
        if obs["intent"] == "crisis":
            parts.append("CRISIS: รับรู้ก่อน ไม่ตัดสิน แนะนำ 1323 ถ้าจำเป็น")
        return " | ".join(parts)


# ── Singleton ─────────────────────────────────────────────────────
_engine = PersonaEngine()

def observe(text: str) -> dict:
    return _engine.observe(text)

def build_context_note(text: str) -> str:
    return _engine.build_context_note(text)

def detect_intent(text: str) -> str:
    return _engine.detect_intent(text)

def detect_style(text: str) -> str:
    return _engine.detect_style(text)
