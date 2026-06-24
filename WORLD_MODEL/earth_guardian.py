EARTH_RULES = {
    "protect_animals": True,
    "protect_forests": True,
    "protect_water": True,
    "reduce_harm": True
}

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

    t = text.lower()

    for w in ANIMAL_WORDS:
        if w in t:
            return True

    return False


def detect_environment_harm(text):

    t = text.lower()

    for w in HARM_WORDS:
        if w in t:
            return "harm"

    for w in POLLUTION_WORDS:
        if w in t:
            return "pollution"

    return None


def earth_response():

    return [
        "Option A — ปล่อยธรรมชาติทำงานตามระบบของมัน",
        "Option B — ลดการรบกวน เช่นไม่เผาป่า ไม่ทิ้งขยะลงน้ำ",
        "Option C — ช่วยระบบนิเวศ เช่นเก็บขยะหรือให้อาหารสัตว์เล็กอย่างปลอดภัย"
    ]
