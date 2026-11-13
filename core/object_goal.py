"""
core/object_goal.py — ความสัมพันธ์ของวัตถุกับเป้าหมาย (Object-Goal Relationship)

บทเรียนจากเจ้าของโปรเจกต์ "ปริศนาล้างรถ 100 เมตร": ถามว่า "จะเอารถไปล้างที่ร้านห่างไป 100 เมตร ควรเดินหรือขับ"
AI ที่ดูแค่ตัวเลขจะตอบว่า "เดินไป ประหยัดพลังงาน" — ถูกตามตัวเลข แต่ลืมว่างานคือล้างรถ และรถต้องไปด้วย
ระบบเดิมก็ตกข้อนี้ (ได้ "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน") รวมถึงตู้เย็นไปซ่อม และพาหมาไปฉีดวัคซีน

หลัก: ของที่ต้องไปถึงที่หมาย ต้องไปด้วยวิธีที่พามันไปได้ — ระยะใกล้ไม่ได้เปลี่ยนเรื่องนี้
แยกตามชนิดของ เพราะคำตอบต่างกันจริง: รถต้องขับ · สัตว์เลี้ยงเดินไปด้วยกันได้ · ของหนักเดินไม่ได้ · ของเล็กถือไปได้
และยังคืนทางเลือก (มากกว่าหนึ่งทาง) ไม่ใช่สั่งทางเดียว
"""
from __future__ import annotations

import re

_I = re.I

# ชนิดของ → (คำไทย, คำอังกฤษ)
_KINDS = {
    "vehicle": (r"รถยนต์|รถเก๋ง|รถกระบะ|รถมอเตอร์ไซค์|มอเตอร์ไซค์|มอไซค์|มอไซ|จักรยาน|รถ",
                r"car|truck|motorbike|motorcycle|scooter|bike|bicycle|van"),
    "pet": (r"หมา|สุนัข|แมว|น้องหมา|น้องแมว|กระต่าย|สัตว์เลี้ยง",
            r"dog|puppy|cat|kitten|pet|rabbit"),
    "heavy": (r"ตู้เย็น|เครื่องซักผ้า|ทีวี|โทรทัศน์|โซฟา|ตู้|เตียง|ที่นอน|แอร์|เครื่องปรับอากาศ|เปียโน|โต๊ะ",
              r"fridge|refrigerator|washing machine|washer|tv|television|sofa|couch|mattress|bed|piano|air ?con\w*|wardrobe"),
    "small": (r"มือถือ|โทรศัพท์|โน้ตบุ๊ก|โน๊ตบุ๊ค|คอม|ไอแพด|แท็บเล็ต|รองเท้า|นาฬิกา|กระเป๋า|เสื้อผ้า|แว่น",
              r"phone|laptop|tablet|ipad|shoes|watch|bag|clothes|glasses"),
}
# ไปทำอะไรกับของนั้น (เป้าหมายที่ของต้องไปด้วย)
_TASK_TH = r"ล้าง|ซ่อม|เช็ก|ตรวจ|ฉีด(?:วัคซีน|ยา)?|อาบน้ำ|ตัดขน|เติม(?:ลม|น้ำมัน)|เปลี่ยน(?:ยาง|น้ำมันเครื่อง|จอ|แบต)|ส่ง(?:ซ่อม|ตรวจ)|ขาย|จำนำ|ทำความสะอาด|รักษา|หาหมอ"
_TASK_EN = r"wash|fix|repair|service|check|vaccinat\w*|groom\w*|clean\w*|sell|vet|inflate|refuel"
# คำถามเรื่องวิธีไป
_HOW_TH = r"เดิน(?:ไป)?(?:เอง)?(?:ได้)?(?:ไหม|มั้ย|ดีไหม|ดีมั้ย|หรือ|ดี)|เดินหรือขับ|ขับหรือเดิน|ควรเดิน|เดินไปก็ได้|ไปยังไงดี"
_HOW_EN = r"\bwalk or drive\b|\bdrive or walk\b|\bshould I walk\b|\bcan I (?:just )?walk\b|\bwalk there\b"

_RX_TH = {k: re.compile(rf"(?:เอา|พา|ขน|ยก)?(?:{v[0]})[^\n]{{0,16}}?(?:ไป)?(?:{_TASK_TH})[^\n]{{0,40}}?(?:{_HOW_TH})", _I) for k, v in _KINDS.items()}
_RX_EN = {k: re.compile(rf"\b(?:my |the |a )?(?:{v[1]})\b[^\n]{{0,40}}?\b(?:{_TASK_EN})\w*\b[^\n]{{0,60}}?(?:{_HOW_EN})|"
                        rf"\b(?:{_TASK_EN})\w* (?:my |the |a )?(?:{v[1]})\b[^\n]{{0,60}}?(?:{_HOW_EN})", _I) for k, v in _KINDS.items()}

_REPLY = {
    "vehicle": {
        "th": ("งานนี้คือการเอารถไปทำ — รถต้องไปถึงร้านด้วย ระยะ 100 เมตรหรือ 1 กิโลไม่ได้เปลี่ยนเรื่องนี้ ถ้าเดินไปตัวเปล่า งานก็ไม่เกิด",
               ["ขับหรือขี่ไปเอง — ใกล้แค่ไหนก็ใช้เวลาไม่กี่นาที",
                "ถ้ารถสตาร์ตไม่ติดหรือไม่อยากขับ ถามร้านว่ามีบริการรับรถถึงบ้านไหม หรือเรียกรถยก",
                "ถ้าอยากเดินออกกำลังกายด้วย เอารถไปจอดไว้ที่ร้าน แล้วเดินกลับบ้านระหว่างรอก็ได้"],
               "รถพร้อมขับไปได้ไหม หรือมีปัญหาที่ทำให้ขับไม่ได้?"),
        "en": ("The job is the car — the car has to get to the shop. Whether it's 100 metres or a kilometre doesn't change that; walking there alone gets nothing done.",
               ["Drive it there — even nearby, it takes a couple of minutes.",
                "If it won't start or you'd rather not drive, ask the shop about pick-up, or call a tow.",
                "If you wanted the walk too, drop the car off and walk home while it's being done."],
               "Is the car able to be driven, or is something stopping that?"),
    },
    "pet": {
        "th": ("เป้าหมายคือให้น้องได้ไปถึงที่หมาย — เดินไปได้ ถ้าพาน้องไปด้วย ระยะใกล้แบบนี้เดินเป็นทางที่ดีด้วยซ้ำ",
               ["เดินพาไปพร้อมสายจูง (หมา) หรือใส่กระเป๋า/กรงสัตว์ (แมว กระต่าย) — แมวส่วนใหญ่ตกใจง่ายนอกบ้าน อย่าอุ้มเปล่าๆ",
                "ถ้าน้องป่วย เดินไม่ไหว หรือเครียดง่าย ใช้รถหรือเรียกรถรับส่งสัตว์เลี้ยง",
                "ถ้าเป็นการฉีดวัคซีน พกสมุดวัคซีนไปด้วย"],
               "น้องเดินไหว และคุ้นกับการออกนอกบ้านไหม?"),
        "en": ("The goal is getting your pet there — walking is fine as long as they come with you, and for a short distance it's often the best option.",
               ["Walk them on a leash (dogs) or in a carrier (cats, rabbits) — most cats panic outside, so don't just carry them in your arms.",
                "If they're sick, can't walk far, or stress easily, drive or use a pet taxi.",
                "For vaccinations, bring the vaccination record."],
               "Can your pet walk there, and are they used to being outside?"),
    },
    "heavy": {
        "th": ("ของชิ้นนี้ต้องไปถึงร้าน และเดินถือไปไม่ได้ ไม่ว่าจะใกล้แค่ไหน — คำถามจริงคือจะให้ของไปถึงร้านด้วยวิธีไหน หรือให้ร้านมาหาของแทน",
               ["เรียกช่างมาซ่อมที่บ้าน — ของใหญ่ส่วนมากซ่อมที่บ้านได้ และไม่เสี่ยงเสียหายตอนขน",
                "ถามร้านว่ามีบริการรับของถึงบ้านไหม หรือเรียกรถกระบะหรือแอปขนของ",
                "ถ้าจะขนเอง ใช้รถเข็นและคนช่วยอย่างน้อยสองคน (ตู้เย็นควรตั้งตรง ห้ามนอน)"],
               "ร้านมีบริการซ่อมนอกสถานที่หรือรับของถึงบ้านไหม?"),
        "en": ("This has to reach the shop and can't be carried there on foot, however close — the real question is how it gets there, or whether the shop comes to it instead.",
               ["Have a technician come to you — most large appliances can be repaired at home, without the risk of damage in transit.",
                "Ask the shop about pick-up, or book a van or moving app.",
                "If moving it yourself, use a trolley and at least two people (keep a fridge upright)."],
               "Does the shop offer on-site repair or pick-up?"),
    },
    "small": {
        "th": ("ของชิ้นนี้ถือไปได้ เดินไปได้เลย — แค่อย่าลืมว่างานคือของชิ้นนั้น ต้องเอาติดตัวไปด้วย",
               ["เดินไปพร้อมของ — ใส่ถุงหรือกระเป๋าให้ปลอดภัย",
                "ถ้าเป็นมือถือหรือคอม สำรองข้อมูลก่อนส่งซ่อม และจดรหัสหรืออุปกรณ์เสริมที่ร้านอาจต้องใช้",
                "ขอใบรับของหรือใบเสร็จจากร้านทุกครั้ง"],
               "สำรองข้อมูลในเครื่องไว้แล้วหรือยัง?"),
        "en": ("You can carry this, so walking is fine — just remember the job is the item itself, so it has to come with you.",
               ["Walk there with it, packed safely.",
                "For a phone or laptop, back up your data before repair and note any passcode or accessories the shop may need.",
                "Always get a receipt or ticket for the item."],
               "Have you backed up what's on the device?"),
    },
}


def check(text: str):
    """คืน (ชนิดของ, ภาษา) ถ้าเป็นคำถามแบบ "เอา X ไปทำ Y ควรเดินไหม" — ไม่ใช่ก็ None"""
    t = str(text or "")
    for k in ("vehicle", "heavy", "pet", "small"):          # รถก่อน: "เอารถไปล้าง" · ของหนักก่อนของเล็ก
        if _RX_TH[k].search(t):
            return k, "th"
        if _RX_EN[k].search(t):
            return k, "en"
    return None


def reply(text: str, footer: bool = True):
    hit = check(text)
    if not hit:
        return None
    kind, lang = hit
    opn, paths, ask = _REPLY[kind][lang]
    sign = "— LYLA ◈"
    tag = ("\n· Answered from the system's equations — no AI used" if lang == "en" else "\n· ตอบจากสมการของระบบ — ไม่ได้ใช้ AI") if footer else ""
    return opn + "\n\n" + "\n".join(f"{i + 1}) {p}" for i, p in enumerate(paths)) + f"\n\n{ask}\n\n{sign}" + tag
