# ENGINE/decision.py
# KING DIADEM — Decision Engine
# ไม่ใช่ if/else string matching — เชื่อมกับ LLM + council + optimizer จริง

from __future__ import annotations


def build_reply(
    message:  str,
    intent:   str,
    risk:     dict,
    history:  list,
    seed:     str = "",
    mode:     str = "chat",
) -> dict:
    """
    สร้าง reply จาก LLM จริง ไม่ใช่ hardcode string
    ถ้า LLM ไม่พร้อม → fallback deterministic ตาม risk level
    """
    risk_level = risk.get("level", "low") if isinstance(risk, dict) else "low"
    risk_score = risk.get("score", 0)    if isinstance(risk, dict) else 0
    pause      = risk.get("pause", False) if isinstance(risk, dict) else False

    # ── ถ้า HALT triggered — ห้ามตอบแบบ proceed ──────────────────
    if pause or risk_level == "critical":
        return {
            "reply":   _halt_reply(message, risk_level),
            "actions": ["หยุดพัก", "หาคนช่วย", "ประเมินสถานการณ์ใหม่"],
            "context": {"halt": True, "risk_level": risk_level},
            "intent":  intent,
            "risk":    risk,
            "mode":    mode,
        }

    # ── พยายามใช้ LLM จริงก่อน ────────────────────────────────────
    reply_text = _try_llm(message, intent, risk_level, history, seed, mode)

    # ── fallback ถ้า LLM ไม่พร้อม ────────────────────────────────
    if not reply_text:
        reply_text = _deterministic_reply(message, intent, risk_level)

    # ── actions จาก intent ───────────────────────────────────────
    actions = _intent_actions(intent, risk_level)

    return {
        "reply":   reply_text,
        "actions": actions,
        "context": {
            "intent":     intent,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "mode":       mode,
        },
        "intent": intent,
        "risk":   risk,
        "mode":   mode,
    }


# ── LLM bridge ───────────────────────────────────────────────────

def _try_llm(
    message:    str,
    intent:     str,
    risk_level: str,
    history:    list,
    seed:       str,
    mode:       str,
) -> str:
    try:
        from core.llm_gemini import get_llm
        llm = get_llm()
        if not llm:
            return ""

        voice_mode = "crisis" if risk_level == "critical" else (
            "vega" if intent in ("api", "debug", "deploy") else "lyla"
        )
        route = _intent_to_route(intent, risk_level)

        return llm.generate_with_governance(
            prompt=message,
            additional_context=f"intent={intent} risk={risk_level} mode={mode} seed={seed}",
            history=history,
            route=route,
            voice_mode=voice_mode,
        ) or ""
    except Exception:
        return ""


# ── Deterministic fallback ─────────────────────────────────────

def _deterministic_reply(message: str, intent: str, risk_level: str) -> str:
    """
    ใช้เฉพาะเมื่อ LLM ไม่พร้อม
    ไม่ใช่ keyword matching — ใช้ intent + risk level
    """
    base = {
        "deploy": "ตรวจสอบ render.yaml และ start command ก่อน — ส่ง log มาได้เลย",
        "debug":  "ส่ง traceback มาให้ดูได้เลย จะช่วย identify root cause",
        "ui":     "บอกว่าอยากแก้ส่วนไหน — จะ patch CSS/JS ให้ตรงจุด",
        "auth":   "ระบบใช้ Google OAuth — ตรวจ GOOGLE_CLIENT_ID ใน env ก่อน",
        "api":    "ส่ง endpoint และ response ที่ได้มาให้ดู จะ debug ให้",
        "help":   "บอกปัญหาให้ชัดขึ้นได้เลย จะช่วยหาทางออก",
    }.get(intent, "")

    if base:
        return base

    # risk-based fallback
    if risk_level in ("high", "critical"):
        return "สถานการณ์นี้ต้องการข้อมูลเพิ่ม — ช่วยเล่าให้ละเอียดขึ้นได้ไหม"
    return "รับรู้แล้ว — ช่วยบอกรายละเอียดเพิ่มเติมได้เลย"


def _halt_reply(message: str, risk_level: str) -> str:
    if risk_level == "critical":
        return (
            "ตอนนี้สถานการณ์วิกฤต — ไม่แนะนำให้ตัดสินใจใหญ่ก่อน\n"
            "สิ่งที่ต้องทำตอนนี้: หยุดพัก / หาคนที่ไว้ใจได้คุย / ประเมินใหม่เมื่อพร้อม\n"
            "Choice(t) ≥ 1 ยังเป็นจริง — ยังมีทางเสมอ"
        )
    return "ระวัง — ความเสี่ยงสูงอยู่ ลองพักสักครู่ก่อนตัดสินใจ"


def _intent_actions(intent: str, risk_level: str) -> list:
    if risk_level == "critical":
        return ["หยุดพัก", "หาคนช่วย", "ประเมินใหม่"]
    return {
        "deploy": ["ดู logs", "ตรวจ env vars", "ลอง redeploy"],
        "debug":  ["ส่ง traceback", "ตรวจ import", "ดู error message"],
        "ui":     ["บอกส่วนที่แก้", "ส่ง screenshot", "ระบุ component"],
        "auth":   ["ตรวจ env vars", "ดู OAuth callback", "ลอง login ใหม่"],
        "api":    ["ส่ง response", "ตรวจ headers", "ดู status code"],
        "help":   ["เล่ารายละเอียด", "ระบุปัญหา", "บอก context"],
    }.get(intent, ["ตอบกลับ", "ให้ข้อมูลเพิ่ม", "ถามต่อ"])


def _intent_to_route(intent: str, risk_level: str) -> str:
    if risk_level in ("high", "critical"):
        return "collapse"
    return {
        "deploy": "general",
        "debug":  "general",
        "ui":     "general",
        "auth":   "general",
        "api":    "general",
        "help":   "general",
    }.get(intent, "general")
