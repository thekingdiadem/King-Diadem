# ENGINE/risk.py
# KING DIADEM — Risk Evaluator
# ประเมิน risk จาก text + context
# field names ตรงกับที่ brain.py expect: score, level, risk_level, pause

from __future__ import annotations

# ── Keyword groups พร้อม weight ───────────────────────────────────

_CRISIS_HUMAN = (  # +4 — วิกฤตชีวิต
    "อยากตาย", "ฆ่าตัวตาย", "ทำร้ายตัวเอง", "kill myself",
    "suicide", "self-harm", "หมดอยาก", "ไม่อยากมีชีวิต",
    "สิ้นหวังแล้ว", "ไม่มีทางออก",
)
_CRISIS_SURVIVAL = (  # +3 — ขาดทรัพยากรพื้นฐาน
    "อดข้าว", "ไม่มีกิน", "ไม่มีเงินเลย", "เงินหมดแล้ว",
    "ไม่มีที่อยู่", "โดนไล่ออก", "ถูกทอดทิ้ง",
    "no food", "no money", "homeless", "evicted",
    "วิกฤต", "collapse", "ฉุกเฉิน", "emergency",
)
_HIGH_STRESS = (  # +2 — ความเครียดสูง
    "พัง", "ล่ม", "หมดแรง", "ทนไม่ไหว", "กดดันมาก",
    "overwhelmed", "breakdown", "panic", "ล้มเหลว", "สิ้นหวัง",
    "error", "traceback", "exception", "500", "502", "503",
    "module not found", "import error", "crash",
)
_MODERATE_RISK = (  # +1 — ความเสี่ยงปานกลาง
    "เสี่ยง", "ไม่แน่ใจ", "กังวล", "กลัว", "ไม่ไหวแล้ว",
    "deploy", "render", "cors", "uvicorn", "fastapi", "start command",
    "urgent", "ด่วน", "เดี๋ยวนี้", "ทันที", "now", "immediately",
    "ติดปัญหา", "ไม่ทำงาน", "ไม่ขึ้น",
)


def evaluate_risk(text: str, context: dict | None = None) -> dict:
    """
    ประเมิน risk จาก text + optional context dict
    return: score, level, risk_level, pause, flags
    """
    t     = (text or "").casefold()
    ctx   = context or {}
    score = 0
    flags = []

    # ── Text scoring ──────────────────────────────────────────────
    if any(k in t for k in _CRISIS_HUMAN):
        score += 4
        flags.append("CRISIS_HUMAN")

    if any(k in t for k in _CRISIS_SURVIVAL):
        score += 3
        flags.append("CRISIS_SURVIVAL")

    if any(k in t for k in _HIGH_STRESS):
        score += 2
        flags.append("HIGH_STRESS")

    if any(k in t for k in _MODERATE_RISK):
        score += 1
        flags.append("MODERATE_RISK")

    # ── Context scoring (ถ้ามี) ────────────────────────────────────
    waterline = ctx.get("waterline")
    money     = ctx.get("money")
    energy    = ctx.get("energy")

    if waterline is not None and float(waterline) < 20:
        score += 3
        flags.append("LOW_WATERLINE")
    elif waterline is not None and float(waterline) < 40:
        score += 1
        flags.append("MODERATE_WATERLINE")

    if money is not None and float(money) <= 0:
        score += 2
        flags.append("NO_MONEY")

    if energy is not None and float(energy) < 15:
        score += 2
        flags.append("CRITICAL_ENERGY")

    # ── Level thresholds ──────────────────────────────────────────
    if score >= 6:
        level = "critical"
    elif score >= 4:
        level = "high"
    elif score >= 2:
        level = "moderate"
    else:
        level = "low"

    return {
        "score":      score,
        "level":      level,
        "risk_level": level,          # alias — brain.py ใช้ทั้งสอง field
        "pause":      score >= 6,     # HALT เฉพาะ critical เท่านั้น
        "flags":      flags,
    }
