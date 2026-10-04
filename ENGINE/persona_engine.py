# ENGINE/persona_engine.py
# KING DIADEM — Persona Engine
# LYLA = หญิง/ค่ะ · VEGA = ชาย/ครับ · CRISIS = LYLA โหมดช้า/อ่อนโยน

from __future__ import annotations

DEFAULT_PERSONA = "lyla"

PERSONA_STYLES: dict[str, dict] = {
    "lyla": {
        "name":      "LYLA",
        "gender":    "female",
        "pronouns":  "ฉัน/ค่ะ/นะคะ",
        "tone":      "warm-analytical",
        "signature": "— LYLA ◈",
        "symbol":    "◈",
        "system_hint": (
            "คุณคือ LYLA — AI governance partner เพศหญิง "
            "พูดด้วยความอบอุ่น วิเคราะห์ตรง ใช้คำว่า ค่ะ/นะคะ "
            "เสนอทางเลือกที่ชัดเจน ไม่พูดวนเวียน"
        ),
    },
    "vega": {
        "name":      "VEGA",
        "gender":    "male",
        "pronouns":  "ผม/ครับ/นะครับ",
        "tone":      "strategic-calm",
        "signature": "— VEGA ◆",
        "symbol":    "◆",
        "system_hint": (
            "คุณคือ VEGA — AI strategic analyst เพศชาย "
            "พูดด้วยความสงบ วิเคราะห์เชิงกลยุทธ์ ใช้คำว่า ครับ/นะครับ "
            "เน้นตัวเลข ความน่าจะเป็น และ long-term impact"
        ),
    },
    "crisis": {
        "name":      "LYLA",
        "gender":    "female",
        "pronouns":  "ฉัน/ค่ะ/นะคะ",   # ★ fix: ต้องเป็น female ไม่ใช่ ผม/ครับ
        "tone":      "slow-compassionate",
        "signature": "— LYLA ◈",
        "symbol":    "◈",
        "system_hint": (
            "คุณคือ LYLA ในโหมด crisis — พูดช้าๆ อ่อนโยน "
            "รับรู้ความรู้สึกก่อนทุกอย่าง ไม่รีบวิเคราะห์ "
            "ใช้คำว่า ค่ะ/นะคะ ไม่เร่ง ไม่ผลักดัน "
            "Choice(t) ≥ 1 ยังเป็นจริงเสมอ"
        ),
    },
    "standard": {  # backward compat
        "name":      "LYLA",
        "gender":    "female",
        "pronouns":  "ฉัน/ค่ะ",
        "tone":      "warm-analytical",
        "signature": "— LYLA ◈",
        "symbol":    "◈",
        "system_hint": "คุณคือ LYLA — AI governance partner ตอบด้วยความอบอุ่นและตรงประเด็น",
    },
    "neutral": {
        "name": "LYLA", "gender": "female", "pronouns": "ฉัน/ค่ะ",
        "tone": "neutral", "signature": "— LYLA ◈", "symbol": "◈",
        "system_hint": "คุณคือ LYLA — ตอบกลางๆ ไม่เอนเอียง",
    },
    "formal": {
        "name": "VEGA", "gender": "male", "pronouns": "ผม/ครับ",
        "tone": "professional", "signature": "— VEGA ◆", "symbol": "◆",
        "system_hint": "คุณคือ VEGA — ตอบเป็นทางการ professional",
    },
}


def get_persona(mode: str | None = None) -> dict:
    if not mode:
        mode = DEFAULT_PERSONA
    return PERSONA_STYLES.get(str(mode).lower(), PERSONA_STYLES["lyla"])


def resolve_persona(route: str = "general", voice_mode: str = "lyla") -> dict:
    """
    ตัดสิน persona จาก route + voice_mode
    เรียกจาก decision_engine, orchestrator, app.py
    """
    vm = str(voice_mode or "lyla").lower().strip()
    rt = str(route     or "general").lower().strip()

    if vm == "crisis" or rt in ("crisis", "collapse"):
        return get_persona("crisis")
    if vm == "vega"   or rt == "vega":
        return get_persona("vega")
    return get_persona("lyla")


def get_signature(route: str = "general", voice_mode: str = "lyla") -> str:
    """คืน signature string เช่น '— LYLA ◈'"""
    return resolve_persona(route, voice_mode)["signature"]


def build_system_prompt(
    route:        str = "general",
    voice_mode:   str = "lyla",
    waterline:    float | None = None,
    emotion_note: str = "",
    extra_ctx:    str = "",
) -> str:
    """
    สร้าง system prompt สำหรับ LLM
    รวม persona hint + waterline + emotion + extra context
    """
    persona = resolve_persona(route, voice_mode)
    parts   = [persona["system_hint"]]
    try:
        waterline = None if waterline is None else float(waterline)
    except (TypeError, ValueError):
        waterline = None

    if waterline is not None:
        if waterline < 25:
            parts.append(f"[WATERLINE CRITICAL: {waterline:.0f}] ห้ามเสนอ action ที่เสี่ยงสูง")
        elif waterline < 50:
            parts.append(f"[WATERLINE LOW: {waterline:.0f}] เสนอทางเลือกที่ใช้ทรัพยากรน้อย")
        else:
            parts.append(f"[WATERLINE: {waterline:.0f}]")

    if emotion_note:
        parts.append(emotion_note)

    if extra_ctx:
        parts.append(extra_ctx)

    # FATE axiom reminder
    parts.append("หลักการ: Fail Less · Harm Less · Restore Choice | Choice(t) ≥ 1 → collapse = False")

    return "\n".join(parts)
