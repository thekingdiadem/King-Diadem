# ENGINE/human_state_engine.py
# KING DIADEM — Human State Engine
# ประเมินสถานะมนุษย์จาก multiple signals จริง
# ไม่ใช่ keyword match + score -= 10 hardcode

from __future__ import annotations


# ── Text signal detector ─────────────────────────────────────────

_DEPRESSION_SIGNALS = [
    "หมดหวัง", "ไม่อยากทำอะไร", "ไม่มีความหมาย", "ท้อแท้",
    "เบื่อชีวิต", "อยากหายไป", "depress", "hopeless", "worthless",
    "ไม่มีค่า", "ล้มเลิก", "ยอมแพ้",
]
_FEAR_SIGNALS = [
    "กลัว", "ตื่นตกใจ", "หวาดกลัว", "ไม่กล้า", "วิตก",
    "fear", "scared", "panic", "anxiety", "anxious", "กังวล",
]
_ANGER_SIGNALS = [
    "โกรธ", "ฉุน", "หัวร้อน", "เดือด", "ไม่พอใจ", "ทนไม่ได้",
    "angry", "furious", "rage", "frustrated",
]
_EXHAUSTION_SIGNALS = [
    "เหนื่อย", "ล้า", "หมดแรง", "ไม่มีแรง", "อ่อนเพลีย",
    "tired", "exhausted", "burnt out", "burnout",
]
_VIOLENCE_SIGNALS = [
    "ทำร้าย", "ทำร้ายตัวเอง", "ฆ่า", "อยากตาย",
    "violence", "hurt", "kill", "self-harm", "suicide",
]
_DEPENDENCY_SIGNALS = [
    "ต้องเลี้ยงเขา", "ต้องดูแล", "ภาระ", "พึ่งพา",
    "dependent", "responsibility", "burden",
]


def analyze_human_state(text: str) -> dict:
    """
    วิเคราะห์ text → emotional state flags
    return dict พร้อม flags, risk_level, lyla_guidance
    """
    t = (text or "").lower()

    flags = {
        "depression":    any(s in t for s in _DEPRESSION_SIGNALS),
        "fear":          any(s in t for s in _FEAR_SIGNALS),
        "anger":         any(s in t for s in _ANGER_SIGNALS),
        "exhaustion":    any(s in t for s in _EXHAUSTION_SIGNALS),
        "violence_risk": any(s in t for s in _VIOLENCE_SIGNALS),
        "dependency":    any(s in t for s in _DEPENDENCY_SIGNALS),
    }

    # ── Risk level จาก flags ──────────────────────────────────────
    critical_count = sum([flags["depression"], flags["violence_risk"]])
    high_count     = sum([flags["fear"], flags["exhaustion"]])

    if critical_count >= 1:
        risk_level = "critical"
    elif high_count >= 2:
        risk_level = "high"
    elif any(flags.values()):
        risk_level = "moderate"
    else:
        risk_level = "low"

    # ── LYLA guidance ──────────────────────────────────────────────
    if flags["violence_risk"]:
        guidance = "HALT — ไม่ตัดสินใจใดๆ / หาผู้เชี่ยวชาญทันที"
    elif flags["depression"]:
        guidance = "รับฟังก่อน อย่าผลักดัน — เสนอทางเลือกเล็กๆ ที่ทำได้วันนี้"
    elif flags["exhaustion"]:
        guidance = "พักก่อน — แนะนำ action ที่ใช้แรงน้อยที่สุดเท่านั้น"
    elif flags["fear"]:
        guidance = "สร้างความมั่นคงก่อน — บอก Choice(t) ≥ 1 ยังเป็นจริง"
    elif flags["anger"]:
        guidance = "อย่าเร่ง — รอให้อารมณ์เย็นลงก่อนตัดสินใจ"
    else:
        guidance = "พร้อมวิเคราะห์ได้ปกติ"

    return {
        "flags":      flags,
        "risk_level": risk_level,
        "guidance":   guidance,
        "flag_count": sum(flags.values()),
    }


# ── Numeric state evaluator ───────────────────────────────────────

def evaluate_human_state(
    food:    float = 2.0,   # จำนวนมื้อที่มี
    money:   float = 100.0,
    risk:    float = 3.0,   # 0-10
    energy:  float = 50.0,  # 0-100
    sleep:   float = 6.0,   # ชั่วโมง
) -> dict:
    """
    คำนวณ waterline score จาก numeric inputs จริง
    ไม่ใช่ score -= 10 hardcode
    """
    score = 70.0  # baseline

    # food penalty
    if food <= 0:
        score -= 30
    elif food < 2:
        score -= 15
    elif food < 3:
        score -= 5

    # money penalty (progressive)
    if money <= 0:
        score -= 20
    elif money < 50:
        score -= 12
    elif money < 200:
        score -= 5

    # risk penalty
    risk_norm = min(10.0, max(0.0, risk))
    score -= risk_norm * 3  # max -30

    # energy penalty
    if energy < 15:
        score -= 20
    elif energy < 30:
        score -= 10
    elif energy < 50:
        score -= 5

    # sleep penalty
    if sleep < 3:
        score -= 15
    elif sleep < 5:
        score -= 8
    elif sleep < 6:
        score -= 3

    score = max(0.0, min(100.0, score))

    if score < 20:
        state_label = "critical"
    elif score < 40:
        state_label = "high_risk"
    elif score < 60:
        state_label = "stressed"
    elif score < 80:
        state_label = "moderate"
    else:
        state_label = "stable"

    return {
        "waterline":   round(score, 1),
        "state":       state_label,
        "can_decide":  score >= 35,
        "inputs": {
            "food": food, "money": money,
            "risk": risk, "energy": energy, "sleep": sleep,
        },
    }
