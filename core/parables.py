"""
core/parables.py
Human Wisdom Layer — KING DIADEM
เรื่องเล่าที่ LYLA ดึงมาใช้ตาม context จริง ไม่ใช่แค่เก็บไว้
"""

ANT_AND_DOVE = """มดตัวหนึ่งตกน้ำ กำลังจะจมอยู่รอดไม่ได้
นกพิราบเห็น — หยิบใบไม้ทิ้งลงน้ำให้มดเกาะ
มดรอดชีวิต

ต่อมานายพรานเล็งปืนที่นกพิราบ
มดจำได้ — กัดเท้านายพรานทันที
นายพรานสะดุ้ง ยิงพลาด — นกพิราบบินหนีได้

บทเรียน: แม้ตัวเล็กที่สุด ก็ปกป้องได้
และความเมตตาไม่มีวันสูญเปล่า"""

METTA_PRINCIPLE = """โลโกปตฺถมฺภิกา เมตฺตา — เมตตาค้ำจุนโลก

ระบบที่สร้างด้วยตรรกะล้วนๆ จะเย็นชาในที่สุด
ระบบที่มีเมตตาด้วย — รักษาชีวิตได้นานกว่า"""

CHICKEN_GRILL = """หลักไก่ย่าง

การอยู่รอดไม่ต้องชนะทุกวัน

บางวันขายได้ทุกชิ้น
บางวันไม่มีใครซื้อเลย

เป้าหมายไม่ใช่ความสำเร็จสมบูรณ์แบบ
เป้าหมายคือ — อยู่รอดให้ถึงพรุ่งนี้แล้วค่อยลองใหม่"""

BAMBOO_PRINCIPLE = """หลักไม้ไผ่

ไม้ไผ่โค้งในพายุ แต่ไม่หัก
ต้นไม้แข็งทื่อ — หักก่อน

ความยืดหยุ่นไม่ใช่ความอ่อนแอ
มันคือวิธีที่ระบบรอดผ่านแรงกด"""

WATER_PRINCIPLE = """หลักน้ำ (สูญยตา)

น้ำไม่มีรูปทรงของตัวเอง
แต่มันเอาชนะหินได้ด้วยความสม่ำเสมอ

ไม่ต้องแข็งแกร่งที่สุด
แค่ไหลต่อเนื่องพอ"""

# ── Selector — ดึง parable ตาม context ───────────────────────────

# คำสั้นเดิม ("ใจ" ใน "เข้าใจ/ตัดสินใจ", "ช่วย", "ติด" ใน "ติดต่อ", "เงิน", "นาน", "ช้า")
# ทำให้แทบทุกข้อความได้นิทานยาวแปะเข้า prompt → ใช้วลีที่บอกสถานการณ์จริง
_KEYWORD_MAP = {
    "ant_dove": {
        "keywords": ["ตอบแทน","เมตตา","ทำดีไม่ได้ดี","ช่วยคนอื่น","พันธมิตร","ไม่มีใครเห็นค่า"],
        "text": ANT_AND_DOVE,
        "name": "มดกับนกพิราบ",
    },
    "metta": {
        "keywords": ["เย็นชา","ไม่มีใคร","โดดเดี่ยว","ความเมตตา","ใจร้าย","อ่อนโยน"],
        "text": METTA_PRINCIPLE,
        "name": "หลักเมตตา",
    },
    "chicken_grill": {
        "keywords": ["ล้มเหลว","ขาดทุน","ไม่ได้เรื่อง","ไม่มีลูกค้า","ขายไม่ได้","ขายไม่ออก","ธุรกิจแย่","กิจการพัง"],
        "text": CHICKEN_GRILL,
        "name": "หลักไก่ย่าง",
    },
    "bamboo": {
        "keywords": ["กดดัน","ทนไม่ไหว","แรงเกินไป","เครียดมาก","หนักมาก","สู้ไม่ไหว","ปรับตัวไม่ทัน"],
        "text": BAMBOO_PRINCIPLE,
        "name": "หลักไม้ไผ่",
    },
    "water": {
        "keywords": ["ไม่มีทาง","ทางตัน","หาทางออก","ไม่รู้จะไปไหน","ติดอยู่กับที่","ไม่คืบหน้า","ยาวนาน"],
        "text": WATER_PRINCIPLE,
        "name": "หลักน้ำ",
    },
}


def select_parable(user_text: str) -> dict | None:
    """
    ดึง parable ที่เหมาะกับ context
    คืน dict หรือ None ถ้าไม่มี parable ที่เกี่ยวข้อง
    """
    if not user_text:
        return None
    t = str(user_text).lower()
    best_key   = None
    best_score = 0
    for key, data in _KEYWORD_MAP.items():
        score = sum(1 for kw in data["keywords"] if kw in t)
        if score > best_score:
            best_score = score
            best_key   = key
    if best_score == 0:
        return None
    data = _KEYWORD_MAP[best_key]
    return {"name": data["name"], "text": data["text"]}


def parable_context_note(user_text: str) -> str:
    """
    คืน string สำหรับแนบเข้า additional_context ใน generate_with_governance
    ถ้าไม่มี parable ที่เหมาะ คืน string ว่าง
    """
    p = select_parable(user_text)
    if not p:
        return ""
    return f"\n\n[WISDOM LAYER — {p['name']}]\n{p['text']}"


# ── Direct accessors (backward compat) ───────────────────────────
def get_ant_dove_story():
    return {"type": "parable", "name": "มดกับนกพิราบ", "message": ANT_AND_DOVE}

def get_metta_principle():
    return {"type": "wisdom", "name": "หลักเมตตา", "message": METTA_PRINCIPLE}

def get_chicken_grill_principle():
    return {"type": "wisdom", "name": "หลักไก่ย่าง", "message": CHICKEN_GRILL}
