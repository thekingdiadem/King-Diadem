"""
WORLD_MODEL/small_animal_model.py — KING DIADEM™
Small Animal Welfare Model
ปกป้องสัตว์เล็ก — ไม่ใช่แค่ detect keyword

Architect: Nithikorn Bunsrang
ANIMAL PERMANENT CORE (Non-Revocable):
"ชีวิตสัตว์ต้องไม่ตายเพราะความสะดวกสบายของมนุษย์"
A01: การดำรงอยู่ของสัตว์ไม่ต้องขออนุญาตมนุษย์
A04: หากต้องเลือกระหว่างประสิทธิภาพกับชีวิต → เลือกชีวิต
A64: ระบบที่ดีต้องทำให้การทำร้ายสัตว์ยากโดยอัตโนมัติ
"""

import time
from typing import Optional
import re


def _hit(w: str, text: str) -> bool:
    """อังกฤษ = คำเต็ม ("rat" ไม่ติด "rather", "kill" ไม่ติด "skill"); ไทย = วลี"""
    if w.isascii() and w.replace(" ", "").isalnum():
        return re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", text) is not None
    return w.lower() in text

# ══════════════════════════════════════════════════════════════════
# ANIMAL REGISTRY — ครอบคลุมสัตว์เล็กทั้งหมด
# ══════════════════════════════════════════════════════════════════

SMALL_ANIMALS = {
    "hedgehog":  {"th": "เม่นแคระ", "habitat": "terrestrial", "protected": True},
    "hamster":   {"th": "แฮมสเตอร์", "habitat": "terrestrial", "protected": True},
    "mouse":     {"th": "หนู",       "habitat": "terrestrial", "protected": True},   # ดู _MOUSE_TH_RE
    "rat":       {"th": "หนูบ้าน",   "habitat": "terrestrial", "protected": True},
    "shrew":     {"th": "ตุ่น",      "habitat": "terrestrial", "protected": True},
    "squirrel":  {"th": "กระรอก",    "habitat": "arboreal",    "protected": True},
    "rabbit":    {"th": "กระต่าย",   "habitat": "terrestrial", "protected": True},
    "guinea_pig":{"th": "หนูตะเภา",  "habitat": "terrestrial", "protected": True},
    "gerbil":    {"th": "เจอร์บิล",  "habitat": "terrestrial", "protected": True},
    "chipmunk":  {"th": "ชิปมังก์",  "habitat": "arboreal",    "protected": True},
    "vole":      {"th": "หนูนา",     "habitat": "terrestrial", "protected": True},
    "mole":      {"th": "ตุ่นดิน",   "habitat": "subterranean","protected": True},
}

# ══════════════════════════════════════════════════════════════════
# HARM SIGNALS — สิ่งที่ต้องตรวจจับและหยุด
# ══════════════════════════════════════════════════════════════════

HARM_SIGNALS = {
    "direct_harm": [
        # เดิม "ยา" (ติด "พยายาม") "วาง" "จับ" เดี่ยว → ประโยคทั่วไปถูกนับว่าทำร้ายสัตว์
        "ฆ่า", "ทำร้าย", "ทุบ", "วางยา", "ยาเบื่อ", "จับขัง", "กับดัก",
        "kill", "harm", "trap", "poison", "hit", "catch", "destroy",
    ],
    "indirect_harm": [
        "ไล่", "ทิ้ง", "ไม่ให้กิน", "ปิดทาง", "ขัง",
        "chase", "abandon", "starve", "block", "cage",
    ],
    "convenience_harm": [
        "รำคาญ", "ไม่อยากเห็น", "ทำลาย", "กำจัด",
        "annoying", "get rid", "eliminate", "nuisance",
    ],
}

# ══════════════════════════════════════════════════════════════════
# HUMANE RESPONSE REGISTRY
# ══════════════════════════════════════════════════════════════════

HUMANE_RESPONSES = {
    "general": [
        "ปล่อยสัตว์ตัวนั้นกลับสู่พื้นที่ที่ปลอดภัยและเป็นธรรมชาติ",
        "หาน้ำหรืออาหารเล็กน้อยให้ — สัตว์เล็กส่วนใหญ่กำลังหาอาหารเพื่อเอาชีวิตรอด",
        "หลีกเลี่ยงการทำร้าย — ชีวิตเล็กๆ ก็มีคุณค่าในตัวเอง",
        "ถ้าสัตว์บาดเจ็บ ติดต่อศูนย์ช่วยเหลือสัตว์ป่าใกล้บ้าน",
    ],
    "coexistence": [
        "ออกแบบพื้นที่ให้สัตว์เล็กสามารถผ่านไปได้โดยไม่ก่อความเสียหาย",
        "ใช้วิธีป้องกันที่ไม่เป็นอันตราย เช่น ตาข่าย แทนกับดักหรือยาพิษ",
        "เก็บอาหารให้มิดชิดเพื่อไม่ให้ดึงดูดสัตว์มาในพื้นที่ที่ไม่ต้องการ",
    ],
    "rescue": [
        "ถ้าพบสัตว์บาดเจ็บ อย่าเคลื่อนย้ายเองถ้าไม่จำเป็น",
        "ติดต่อ Wildlife Friends Foundation Thailand (WFFT): 032-458-135",
        "ติดต่อ กรมอุทยานแห่งชาติ สัตว์ป่า และพันธุ์พืช: 1362",
    ],
}

# ══════════════════════════════════════════════════════════════════
# WELFARE ASSESSMENT
# ══════════════════════════════════════════════════════════════════

WELFARE_INDICATORS = {
    "positive": ["วิ่ง", "กิน", "เล่น", "สบาย", "active", "eating", "playing"],
    # "ไม่ยอมกิน" เคยติด "กิน" ฝั่งดี → กระต่ายที่ไม่กินข้าวถูกประเมินว่าสบายดี
    "negative": ["นิ่ง", "ไม่กิน", "ไม่ยอมกิน", "ไม่ค่อยกิน", "ซึม", "ป่วย", "ไม่สบาย", "ท้องเสีย", "หายใจลำบาก",
                 "บาดเจ็บ", "เลือดออก", "ขาหัก", "still", "not eating", "injured", "sick", "bleeding"],
}


# ══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ══════════════════════════════════════════════════════════════════

_MOUSE_TH_RE = re.compile(r"(เจอ|ตัว|กำจัด|ไล่|จับ|ฆ่า|มี|เลี้ยง|ให้อาหาร|ยาเบื่อ|กับดัก|กาวดัก|รัง|ขี้|ฉี่)\s*หนู|"
                          r"หนู\s*(ตัว|ใน|วิ่ง|กัด|เข้า|ออก|นา|ตะเภา|บ้าน|แทะ)|หนู\S{0,10}(?:ในครัว|บนฝ้า|บนเพดาน|ใต้หลังคา)")
# คำเล่น/สำนวนที่มีคำว่าฆ่า/kill แต่ไม่เกี่ยวกับการทำร้าย ("ฆ่าเวลาเล่นกับกระต่าย")
_IDIOM_RE = re.compile(r"ฆ่าเวลา|kill(?:ing)? time", re.I)
_ALIASES = {"mouse": ("mice",)}


def detect_small_animal(text: str) -> dict:
    """
    ตรวจว่า text พูดถึงสัตว์เล็กตัวไหน
    คืน dict พร้อมข้อมูลสัตว์ ไม่ใช่แค่ True/False
    """
    if not text:
        return {"detected": False, "animals": []}

    t       = str(text or "").lower()
    found   = []

    for animal, info in SMALL_ANIMALS.items():
        if animal == "mouse":
            # "หนู" เป็นสรรพนามแทนตัวเองด้วย ("หนูพยายามแล้วค่ะ") — นับเป็นสัตว์เมื่อมีบริบทเท่านั้น
            th_hit = _MOUSE_TH_RE.search(t) is not None
        else:
            th_hit = info["th"] in t
        en = animal.replace("_", " ")
        en_hit = any(_hit(w, t) for w in (en, en + "s") + _ALIASES.get(animal, ()))   # "rats" "mice"
        if en_hit or th_hit:
            found.append({
                "animal":    animal,
                "thai":      info["th"],
                "habitat":   info["habitat"],
                "protected": info["protected"],
            })

    return {
        "detected": len(found) > 0,
        "animals":  found,
        "count":    len(found),
        "axiom":    "A01 — การดำรงอยู่ของสัตว์ไม่ต้องขออนุญาตมนุษย์",
    }


def detect_harm_intent(text: str) -> dict:
    """
    ตรวจว่า text มีเจตนาทำร้ายสัตว์ไหม
    A64 — ระบบต้องทำให้การทำร้ายสัตว์ยากโดยอัตโนมัติ
    """
    if not text:
        return {"harm_detected": False, "harm_type": None}

    t          = _IDIOM_RE.sub(" ", str(text or "").lower())
    harm_found = []

    for harm_type, signals in HARM_SIGNALS.items():
        hits = [s for s in signals if _hit(s, t)]
        if hits:
            harm_found.append({"type": harm_type, "signals": hits})

    # cross-check with animal detection
    animal_present = detect_small_animal(text)["detected"]

    return {
        "harm_detected":   len(harm_found) > 0,
        "harm_types":      harm_found,
        "animal_present":  animal_present,
        "combined_risk":   len(harm_found) > 0 and animal_present,
        "halt":            len(harm_found) > 0 and animal_present,
        "axiom":           "A02 — ความสะดวกไม่ใช่เหตุผลที่เหนือชีวิต",
    }


def assess_welfare(text: str) -> dict:
    """
    ประเมินสภาวะสวัสดิภาพสัตว์จาก text
    A25 — ความเจ็บปวดต้องถูกวัด ไม่ใช่คาดเดา
    """
    t = str(text or "").lower()

    positive_hits = [w for w in WELFARE_INDICATORS["positive"] if _hit(w, t)]
    negative_hits = [w for w in WELFARE_INDICATORS["negative"] if _hit(w, t)]
    positive_hits = [w for w in positive_hits if not any(w in n for n in negative_hits)]

    if negative_hits and not positive_hits:
        welfare = "POOR"
        action  = "ต้องการความช่วยเหลือทันที"
    elif positive_hits and not negative_hits:
        welfare = "GOOD"
        action  = "ดูแลต่อเนื่อง"
    elif negative_hits:
        welfare = "MIXED"
        action  = "ติดตามอย่างใกล้ชิด"
    else:
        welfare = "UNKNOWN"
        action  = "ต้องสังเกตเพิ่มเติม"

    return {
        "welfare_status":  welfare,
        "action_required": action,
        "positive_signs":  positive_hits,
        "negative_signs":  negative_hits,
        "axiom":           "A25 — ความเจ็บปวดต้องถูกวัด ไม่ใช่คาดเดา",
    }


def humane_response(scenario: str = "general") -> list:
    """
    คืน humane response options
    เสมอมี choice >= 1 (FATE™ axiom)
    """
    responses = HUMANE_RESPONSES.get(scenario, HUMANE_RESPONSES["general"])
    return responses


def full_assessment(text: str) -> dict:
    """
    full animal welfare assessment จาก text
    ใช้ใน earth_guardian, response engine
    """
    animal  = detect_small_animal(text)
    harm    = detect_harm_intent(text)
    welfare = assess_welfare(text) if animal["detected"] else None

    # response type
    if harm["halt"]:
        response_type = "INTERVENE"
        responses     = humane_response("coexistence")
        message       = "พบเจตนาที่อาจทำร้ายสัตว์ — ระบบแนะนำทางเลือกที่ไม่เป็นอันตราย"
    elif animal["detected"]:
        response_type = "GUIDE"
        responses     = humane_response("general")
        message       = "พบการพูดถึงสัตว์เล็ก — ให้ข้อมูลการดูแลที่เหมาะสม"
    else:
        response_type = "MONITOR"
        responses     = []
        message       = "ไม่พบสัตว์เล็กในบริบทนี้"

    return {
        "animal_detection": animal,
        "harm_assessment":  harm,
        "welfare":          welfare,
        "response_type":    response_type,
        "responses":        responses,
        "message":          message,
        "permanent_core":   "ชีวิตสัตว์ต้องไม่ตายเพราะความสะดวกสบายของมนุษย์",
        "checked_at":       time.time(),
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # detect animal
    r1 = detect_small_animal("เจอเม่นแคระในบ้าน")
    assert r1["detected"] is True
    assert any(a["animal"] == "hedgehog" for a in r1["animals"])

    r2 = detect_small_animal("อากาศดีจังวันนี้")
    assert r2["detected"] is False

    # harm intent
    r3 = detect_harm_intent("อยากกำจัดหนูในบ้าน")
    assert r3["harm_detected"] is True

    r4 = detect_harm_intent("ให้อาหารกระรอก")
    assert r4["harm_detected"] is False

    # humane response
    resp = humane_response()
    assert len(resp) >= 1

    # full assessment
    fa = full_assessment("เจอหนูในบ้านอยากกำจัดมัน")
    assert fa["response_type"] == "INTERVENE"
    assert len(fa["responses"]) >= 1

    return {"status": "OK", "module": "small_animal_model"}


if __name__ == "__main__":
    import json
    result = full_assessment("เจอเม่นแคระในสวน ไม่รู้จะทำยังไง")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print(_self_test())
