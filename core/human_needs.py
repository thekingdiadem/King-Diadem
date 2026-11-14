"""
core/human_needs.py — ความต้องการใต้คำพูด และโทนภาษาของคนตรงหน้า

เจ้าของโปรเจกต์: "เอาให้โครงสร้างข้างในมันสะท้อนความเข้าใจในจิตวิญญาณของมนุษย์แบบทะลุปรุโปร่ง"
และ "โทนตามแพทเทิร์นผู้ใช้จะดีไหม"

person_reading.py อ่านว่าข้อความนี้อยากได้คำตอบ "แบบไหน" (รายละเอียด/ภาพใหญ่ · เหตุผล/ใจ · ข้อสรุป/ทางเลือก)
ไฟล์นี้อ่านอีกชั้นที่ลึกกว่า: คนนี้ "ขาดอะไร" ลึกๆ — เรื่องที่เล่าเป็นแค่ผิว
  "ทำงานหนักแต่ไม่มีใครเห็น" ผิวคือเรื่องงาน ใต้นั้นคืออยากให้มีคนเห็นว่าเขาเป็นใคร

ความต้องการ 6 อย่าง (ย่อจากที่มนุษย์ศึกษากันมานาน — Maslow, Self-Determination Theory, Frankl):
  safety      ปลอดภัย มั่นคง ไม่ต้องกลัวพรุ่งนี้
  belonging   เป็นส่วนหนึ่ง มีคนอยู่ด้วย ไม่ถูกทิ้ง
  autonomy    ได้เลือกเอง ไม่ถูกบังคับหรือควบคุม
  competence  รู้สึกว่าตัวเองทำได้ ยังมีความสามารถ
  meaning     ชีวิตมีความหมาย ทำไปเพื่ออะไร
  seen        มีคนเห็นและยอมรับว่าเขาเป็นใคร ความพยายามมีค่า

โทนภาษา (register): ตามได้แค่ "รูปแบบ" — ความยาว ระดับภาษา จังหวะ
ไม่ตาม: อารมณ์รุนแรง (คนโกรธต้องการคนที่นิ่งกว่า) · คำหยาบ · เรื่องวิกฤต (นิ่ง ชัด ปลอดภัยเสมอ)
· ตัวตนของ persona (LYLA ยังอบอุ่น VEGA ยังเป็นโครงสร้าง) · อีโมจิ (งดตามหลักเดิม)

หลัก: อ่านจากข้อความตรงหน้าเท่านั้น ไม่เก็บเป็นโปรไฟล์ · สัญญาณอ่อนหรือขัดกัน = ไม่ปรับ · วิกฤตไม่ปรับ
"""
from __future__ import annotations

import re

_I = re.I

_NEEDS = {
    "safety": re.compile(
        r"กลัว(?:ว่า)?(?:จะ)?(?:ไม่มี|ตกงาน|โดนไล่|อด|ไม่รอด)|ไม่มั่นคง|ไม่รู้จะรอดไหม|เดือนหน้าจะ(?:เอา|กิน)|ไม่มีเงินสำรอง|"
        r"ไม่ปลอดภัย|นอนไม่หลับเพราะกังวล|กลัวอนาคต|"
        r"\bafraid (?:i'?ll|of) (?:lose|losing|not making)\b|\bno safety net\b|\bscared about (?:money|rent|the future)\b|\bnot secure\b", _I),
    "belonging": re.compile(
        r"ไม่มีใคร(?!เจ็บ|บาดเจ็บ|อยู่บ้าน|รับสาย|เห็น)|ไม่มีเพื่อน|เพื่อนไม่ชวน|ถูกทิ้ง|โดนทิ้ง|ไม่เข้าพวก|เข้ากับใครไม่ได้|เหงา|โดดเดี่ยว|"
        r"เป็นส่วนเกิน|ไม่มีที่ยืน|"
        r"\blonely\b|\bleft out\b|\bno friends\b|\bdon'?t belong\b|\boutsider\b|\babandoned\b", _I),
    "autonomy": re.compile(
        r"(?:ถูก|โดน)บังคับ|ต้องทำตามที่(?:พ่อแม่|เขา|แฟน|หัวหน้า)|ไม่มีสิทธิ์เลือก|ไม่เคยได้เลือก|เลือกเองไม่ได้|ควบคุม(?:ทุกอย่าง|ชีวิต)|"
        r"ไม่ให้(?:ไป|ทำ|เรียน)|ชีวิตไม่ใช่ของตัวเอง|อยากตัดสินใจเอง|"
        r"\bforced to\b|\bno say\b|\bcontrol(?:s|ling)? (?:my|everything)\b|\bnot my choice\b|\bnever (?:got|get) to choose\b|\bmy own decision\b", _I),
    "competence": re.compile(
        r"ทำอะไรก็ไม่ดี|ไม่เก่ง|ทำไม่ได้สักอย่าง|ล้มเหลว|ไม่มีความสามารถ|แย่กว่าคนอื่น|โง่|ตามไม่ทัน|ทำพลาดอีกแล้ว|สู้เขาไม่ได้|"
        r"\bnot good enough\b|\bfailure\b|\bcan'?t do anything right\b|\bincompetent\b|\bbehind everyone\b|\bi'?m stupid\b", _I),
    "meaning": re.compile(
        r"ทำไปเพื่ออะไร|ไม่รู้จะอยู่ไปทำไม(?!.*ตาย)|ชีวิตไม่มีความหมาย|ว่างเปล่า|ไม่มีเป้าหมาย|ไม่รู้ว่าตัวเองต้องการอะไร|"
        r"วนลูปเดิม|ตื่นมาก็เหมือนเดิม|หมดไฟ|"
        r"\bwhat'?s the point\b|\bmeaningless\b|\bempty\b|\bno purpose\b|\bdon'?t know what i want\b|\bburn(?:ed|t)? out\b", _I),
    "seen": re.compile(
        r"ไม่มีใครเห็น|ไม่มีใคร(?:สนใจ|ฟัง|เข้าใจ)|ไม่เคยได้คำชม|ทำดีแค่ไหนก็ไม่มีใครเห็น|มองข้าม|ไม่เห็นค่า|ไม่มีตัวตน|"
        r"ไม่มีใครถาม(?:ว่า)?(?:ฉัน|เรา|ผม)?เป็นยังไง|"
        r"\bnobody (?:notices|sees|listens|cares)\b|\binvisible\b|\btaken for granted\b|\bunappreciated\b|\bno one asks how i am\b", _I),
}

_CRISIS = re.compile(r"อยากตาย|ไม่อยากอยู่|ฆ่าตัว|จบชีวิต|ทำร้ายตัวเอง|กรีด|\bkill myself\b|\bsuicid\w*\b|\bend (?:it all|my life)\b|\bself[- ]harm\b", _I)


def needs(text: str) -> list[str]:
    """ความต้องการที่เห็นในข้อความ เรียงตามลำดับที่ปรากฏ (มากสุด 2) — ว่าง = ไม่เห็นชัด"""
    t = str(text or "")
    if not t.strip() or _CRISIS.search(t):
        return []
    found = []
    for k, rx in _NEEDS.items():
        m = rx.search(t)
        if m:
            found.append((m.start(), k))
    found.sort()
    return [k for _, k in found][:2]


# ── โทนภาษา ───────────────────────────────────────────────────────────────
_CASUAL = re.compile(r"555|ๆๆ|อะ(?:\s|$)|อ่ะ|ป่ะ|มะ(?:\s|$)|จ้า|จัง(?:เลย)?|เว้ย|วะ|แก(?:\s|$)|ดิ(?:\s|$)|เนอะ|\blol\b|\blmao\b|\bgonna\b|\bwanna\b|\bkinda\b|\bya\b", _I)
_POLITE = re.compile(r"ครับ|ค่ะ|คะ|ขอสอบถาม|รบกวน|กรุณา|ขออนุญาต|\bplease\b|\bcould you\b|\bwould you\b|\bkindly\b", _I)
_HEATED = re.compile(r"!{2,}|\?{3,}|โคตร|เหี้ย|สัส|ห่า|แม่ง|\bwtf\b|\bf+u+c+k\w*\b|\bdamn\b", _I)


def register(text: str) -> dict:
    """{"length": "short"|"long"|None, "style": "casual"|"polite"|None, "heated": bool}"""
    t = str(text or "").strip()
    n = len(t)
    c, p = len(_CASUAL.findall(t)), len(_POLITE.findall(t))
    return {
        "length": "short" if n and n <= 25 else ("long" if n >= 220 else None),
        "style": None if c == p else ("casual" if c > p else "polite"),
        "heated": bool(_HEATED.search(t)),
    }


# ── ประโยครับรู้สิ่งที่ขาด (ไม่มี AI) — หนึ่งประโยค ไม่ตีความเกินข้อความ ─────────
_ACK = {
    "safety": ("ความกังวลว่าพรุ่งนี้จะยังมั่นคงไหม กินแรงใจมากกว่าที่คนอื่นเห็น — เริ่มจากสิ่งที่ทำให้ฐานนิ่งก่อนนะ",
               "Not knowing if tomorrow is secure takes more out of you than people see — let's start with what steadies the ground."),
    "belonging": ("การอยากมีที่ที่ตัวเองเป็นส่วนหนึ่ง เป็นความต้องการพื้นฐานของคนทุกคน ไม่ใช่ความอ่อนแอ",
                  "Wanting a place where you belong is a basic human need, not a weakness."),
    "autonomy": ("การที่ชีวิตถูกตัดสินแทนตลอด ทำให้เหนื่อยแบบที่อธิบายยาก — คุณมีสิทธิ์ได้เลือกเองอย่างน้อยในบางเรื่อง",
                 "Having your life decided for you is tiring in a way that's hard to explain — you have the right to choose for yourself, at least in some things."),
    "competence": ("การพลาดในเรื่องหนึ่ง ไม่ได้วัดความสามารถทั้งหมดของคุณ — แม้ตอนนี้จะรู้สึกแบบนั้นก็ตาม",
                   "Failing at one thing doesn't measure everything you're capable of — even if it feels that way right now."),
    "meaning": ("คำถามว่าทำทั้งหมดนี้ไปเพื่ออะไร ไม่ได้แปลว่าคุณหลงทาง — มันมักมาตอนที่ใจอยากได้ทิศใหม่",
                "Asking what it's all for doesn't mean you're lost — it often comes when you need a new direction."),
    "seen": ("ทำเต็มที่แล้วไม่มีใครเห็น เป็นความเหนื่อยอีกแบบที่หนักไม่แพ้ตัวงาน — สิ่งที่คุณทำมามีค่า แม้ยังไม่มีใครพูดออกมา",
             "Giving your all and having no one notice is its own kind of tiredness — what you've done counts, even if no one has said so."),
}


def acknowledge(text: str, lang: str = "th") -> str:
    ns = needs(text)
    if not ns:
        return ""
    return _ACK[ns[0]][1 if lang == "en" else 0]


# เลนส์ที่ประโยคเปิดพูดถึงความต้องการลึกอยู่แล้ว
_COVERED = {"unseen_effort", "solitude_need", "ambition", "ambition_unstable", "philosophy", "philosophy_death"}


def adapt_main(main: dict, text: str, lang: str = "th") -> dict:
    """เติมประโยครับรู้สิ่งที่ขาดไว้หน้าประโยคเปิด และย่อคำตอบเมื่อผู้ใช้พิมพ์สั้นมาก — ข้อเท็จจริงและขั้นตอนเหมือนเดิม"""
    if not isinstance(main, dict) or not main.get("open"):
        return main
    if main.get("key") in _COVERED:          # เลนส์นี้พูดถึงความต้องการนั้นตรงๆ อยู่แล้ว — ไม่รับรู้ซ้ำ
        return main
    ack = acknowledge(text, lang)
    if not ack:
        return main
    m = dict(main)
    open_ = m["open"][0]
    if ack not in open_:
        m["open"] = [ack + "\n\n" + open_]
    return m


# ── คำใบ้ให้ AI ─────────────────────────────────────────────────────────────
_NEED_HINT = {
    "safety": "ใต้เรื่องที่เล่า เขาต้องการความมั่นคง: บอกสิ่งที่ทำให้ฐานนิ่งได้ก่อน (เงิน ที่อยู่ ความปลอดภัย) ก่อนพูดเรื่องเติบโต",
    "belonging": "ใต้เรื่องที่เล่า เขาต้องการเป็นส่วนหนึ่งของใครสักคน: ยอมรับว่านี่เป็นความต้องการปกติ แล้วเสนอการเชื่อมต่อที่เล็กและทำได้จริง",
    "autonomy": "ใต้เรื่องที่เล่า เขาต้องการได้เลือกเอง: อย่าสั่ง อย่าตัดสินแทน คืนอำนาจการเลือกให้เขาอย่างชัดเจน",
    "competence": "ใต้เรื่องที่เล่า เขารู้สึกว่าตัวเองทำไม่ได้: ชี้สิ่งที่เขาทำได้จริงจากที่เล่ามา (ถ้ามี ไม่แต่งเติม) แล้วให้ก้าวเล็กที่สำเร็จได้",
    "meaning": "ใต้เรื่องที่เล่า เขากำลังถามหาความหมาย: อย่ารีบให้คำตอบสำเร็จรูป ช่วยให้เขาเห็นว่าอะไรที่เขาให้ค่าจริงๆ",
    "seen": "ใต้เรื่องที่เล่า เขาต้องการให้มีคนเห็นความพยายาม: สะท้อนสิ่งที่เขาทำมาให้เห็นว่าได้ยินจริง ก่อนให้คำแนะนำ",
}


def llm_hint(text: str) -> str:
    """คำใบ้ภายในสำหรับ prompt — ห้ามพูดกับผู้ใช้ว่าอ่านเขาแบบนี้"""
    lines = [_NEED_HINT[k] for k in needs(text)]
    r = register(text)
    if r["length"] == "short":
        lines.append("เขาพิมพ์สั้น: ตอบกระชับ ไม่ต้องมีอารัมภบท")
    elif r["length"] == "long":
        lines.append("เขาเล่ายาว: ตอบให้ละเอียดพอกัน แสดงว่าอ่านครบ")
    if r["style"] == "casual":
        lines.append("เขาพิมพ์เป็นกันเอง: ใช้ภาษาเป็นกันเองขึ้นได้ แต่คงตัวตนของ persona และไม่ใช้อีโมจิ")
    elif r["style"] == "polite":
        lines.append("เขาพิมพ์สุภาพ: ตอบสุภาพ")
    if r["heated"]:
        lines.append("เขากำลังอารมณ์แรง: อย่าตามอารมณ์หรือคำหยาบ ตอบให้นิ่งกว่าและชัด")
    if not lines:
        return ""
    return "[ความต้องการใต้คำพูดและโทนของผู้ใช้ — ห้ามบอกผู้ใช้ว่าอ่านแบบนี้]\n" + "\n".join("· " + x for x in lines)
