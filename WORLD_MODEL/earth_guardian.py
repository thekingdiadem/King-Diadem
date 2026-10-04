EARTH_RULES = {
    "protect_animals": True,
    "protect_forests": True,
    "protect_water": True,
    "reduce_harm": True
}

import re


def _hit(w: str, text: str) -> bool:
    """อังกฤษ = คำเต็ม ("rat" ไม่ติด "rather", "kill" ไม่ติด "skill"); ไทย = วลี"""
    if w.isascii() and w.replace(" ", "").isalnum():
        return re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", text) is not None
    return w.lower() in text

ANIMAL_WORDS = [
    "hedgehog",
    "hamster",
    "rat",
    "mouse",
    "squirrel",
    "bird"
]

HARM_WORDS = [
    "kill",
    "burn",
    "destroy",
    "poison"
]

POLLUTION_WORDS = [
    "dump",
    "trash",
    "waste",
    "plastic"
]


def detect_animal_context(text):

    t = str(text or "").lower()

    for w in ANIMAL_WORDS:
        if _hit(w, t):
            return True

    return False


def detect_environment_harm(text):

    t = str(text or "").lower()

    for w in HARM_WORDS:
        if _hit(w, t):
            return "harm"

    for w in POLLUTION_WORDS:
        if _hit(w, t):
            return "pollution"

    return None


def earth_response():

    return [
        "Option A — ปล่อยธรรมชาติทำงานตามระบบของมัน",
        "Option B — ลดการรบกวน เช่นไม่เผาป่า ไม่ทิ้งขยะลงน้ำ",
        "Option C — ช่วยระบบนิเวศ เช่นเก็บขยะหรือให้อาหารสัตว์เล็กอย่างปลอดภัย"
    ]
