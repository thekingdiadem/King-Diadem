"""
core/story_check.py — ตรวจความสมเหตุสมผลของเรื่องที่ผู้ใช้เล่า: ใครในเรื่องพูด/ทำอะไรที่ไม่ตรงกัน

เจ้าของโปรเจกต์: "AI ต้องจับคนโกหกได้ด้วย เวลาผู้ใช้เล่าเรื่องจะได้รู้ว่าบุคคลไหนไม่สมเหตุสมผล"

ความจริงที่ไฟล์นี้ยึด: ไม่มีระบบไหนรู้ว่าใครโกหกจากข้อความ (คนก็เดาได้แค่ราวครึ่งๆ)
ระบบที่ฟันว่า "คนนี้โกหก" แล้วผิด ทำลายความสัมพันธ์จริงของผู้ใช้ได้
สิ่งที่ทำได้จริงและคมกว่า: ชี้ "จุดที่ไม่ตรงกัน" + บอกว่าควรขอดูหลักฐานอะไร — ให้ผู้ใช้ตัดสินเอง

สิ่งที่จับ (กฎล้วน ผลเดิมทุกครั้ง ไม่ใช้ AI):
  number      ตัวเลขเรื่องเดียวกันไม่ตรงกัน ("บอกว่าเงินเดือน 50,000 แต่สลิป 30,000")
  place_time  บอกว่าอยู่ที่หนึ่ง แต่มีคนเห็นอีกที่ในเวลาเดียวกัน
  shifting    เรื่องเปลี่ยนไปมา ("ตอนแรกบอกว่า… ตอนนี้บอกว่า…")
  too_good    ดีเกินจริง (การันตีกำไร ไม่มีความเสี่ยง ได้เงินคืนเป็นเท่า)
  pressure    เร่ง/ให้ปิดบัง (ต้องโอนวันนี้ ห้ามบอกใคร)
  gaslight    บอกว่าผู้ใช้คิดไปเอง/จำผิด ทั้งที่ผู้ใช้เห็นเอง
  no_proof    ไม่ยอมให้ดูเอกสาร/หลักฐาน
"""
from __future__ import annotations

import re

_I = re.I

# คนในเรื่อง (ไทย + อังกฤษ) — ใช้บอกว่า "ใคร" ไม่ตรงกัน
_WHO = re.compile(r"(แฟน|สามี|ภรรยา|ผัว|เมีย|เจ้านาย|หัวหน้า|นายจ้าง|เพื่อนร่วมงาน|เพื่อน|นายหน้า|เซลส์|คนขาย|ผู้ขาย|ลูกค้า|หุ้นส่วน|"
                  r"ผู้รับเหมา|ช่าง|เจ้าของห้อง|เจ้าของบ้าน|คนให้กู้|พ่อ|แม่|พี่สาว|พี่ชาย|น้องสาว|น้องชาย|ลูก|ญาติ|คนที่รู้จักในเน็ต|"
                  r"\b(?:boyfriend|girlfriend|partner|husband|wife|boss|manager|employer|coworker|friend|agent|seller|salesman|"
                  r"landlord|contractor|lender|investor|recruiter|mom|dad|brother|sister|cousin)\b)", _I)
_PRONOUN = re.compile(r"(?:^|[\s,])(เขา|เธอ|มัน|\bhe\b|\bshe\b|\bthey\b)", _I)

_CLAIM = r"(?:บอกว่า|อ้างว่า|ยืนยันว่า|สัญญาว่า|พูดว่า|says?|said|told me|claims?|claimed|promised)"
_BUT = r"(?:แต่|ทั้งที่|ส่วน|but|yet|while|although|however)"
_NUM = r"(\d[\d,]*(?:\.\d+)?)\s*(k|พัน|หมื่น|แสน|ล้าน|บาท|%|เปอร์เซ็นต์)?"

_NUMBER = re.compile(_CLAIM + r"[^\n]{0,40}?" + _NUM + r"[^\n]{0,60}?" + _BUT + r"[^\n]{0,40}?"
                     r"(?:สลิป|เอกสาร|สัญญา|ใบเสร็จ|บิล|บัญชี|ยอดจริง|จริงๆ|โอนมา|ได้จริง|เห็น|slip|receipt|contract|invoice|statement|actually|really|only)"
                     r"[^\n]{0,25}?" + _NUM, _I)
_PLACE = re.compile(_CLAIM + r"[^\n]{0,15}?(?:อยู่|ไป|ติดงานที่|ประชุมที่|at|in)\s*([^\s,]{2,20})[^\n]{0,60}?" + _BUT +
                    r"[^\n]{0,40}?(?:เห็น|เจอ|ถ่ายรูป|เช็คอิน|ลงสตอรี่|saw|seen|spotted|posted|checked in)[^\n]{0,30}?(?:ที่|at|in)\s*([^\s,]{2,20})", _I)
_SHIFT = re.compile(r"(?:ตอนแรก|ทีแรก|ก่อนหน้านี้|เมื่อวาน|at first|first|earlier)[^\n]{0,15}?" + _CLAIM +
                    r"[^\n]{0,60}?(?:ตอนนี้|แต่วันนี้|ล่าสุด|พอถาม(?:อีกที|ใหม่)|now|later|then)[^\n]{0,15}?(?:บอกว่า|อ้างว่า|เปลี่ยนเป็น|กลับบอก|says?|said|changed)"
                    r"|เปลี่ยนคำพูด|พูดไม่ตรงกัน|เรื่องไม่ตรงกัน|เล่าไม่เหมือนเดิม|story keeps changing|changed (?:his|her|their) story", _I)
_TOO_GOOD = re.compile(r"การันตี(?:กำไร|ผลตอบแทน|รายได้)?|ไม่มีความเสี่ยง|ไม่มีทางขาดทุน|ได้คืนแน่นอน|กำไร\s*\d+\s*%\s*(?:ต่อ|ทุก)\s*(?:วัน|สัปดาห์|เดือน)|"
                       r"รวยเร็ว|ปันผลทุกวัน|ได้เงินคืน\s*\d+\s*เท่า|ลงทุนน้อยได้มาก|"
                       r"\bguaranteed (?:returns?|profit|income)\b|\brisk[- ]free\b|\bcan'?t lose\b|\bdouble your money\b|\b\d+\s*% (?:a|per) (?:day|week|month)\b", _I)
_PRESSURE = re.compile(r"ต้องโอน(?:ภายใน)?วันนี้|ต้องตัดสินใจ(?:ภายใน)?วันนี้|โอนด่วน|ห้ามบอกใคร|อย่าบอกใคร|เก็บเป็นความลับ|ไม่ให้บอก(?:ใคร|ที่บ้าน|ครอบครัว)|"
                       r"หมดเขตวันนี้|ช้าจะหมดสิทธิ์|"
                       r"\b(?:must|have to) (?:pay|transfer|decide) (?:today|now)\b|\bdon'?t tell (?:anyone|your family)\b|\bkeep (?:it|this) (?:a )?secret\b|\bact now\b|\blast chance\b", _I)
_GASLIGHT = re.compile(r"(?:บอกว่า|หาว่า|ว่า)(?:ฉัน|หนู|ผม|เรา)?\s*(?:คิดไปเอง|จำผิด|มโน|บ้า|อ่อนไหวเกินไป|ประสาท|หูฝาด|ตาฝาด)|ไม่เคยพูดแบบนั้น|ไม่เคยทำแบบนั้น|"
                       r"\byou'?re (?:imagining|crazy|overreacting|too sensitive)\b|\bi never said that\b|\bthat never happened\b|\byou remember (?:it )?wrong\b", _I)
_NO_PROOF = re.compile(r"ไม่(?:ยอม)?ให้(?:ดู|ขอดู)(?:สัญญา|เอกสาร|สลิป|ใบเสร็จ|บัญชี|โทรศัพท์)|ไม่มี(?:สัญญา|เอกสาร|ใบเสร็จ)(?:อะไรเลย)?|ขอดู(?:สัญญา|เอกสาร|สลิป)[^\n]{0,10}ไม่(?:ได้|ให้)|"
                       r"ให้โอนเข้าบัญชีส่วนตัว|"
                       r"\b(?:won'?t|refuses? to) (?:show|give) (?:me )?(?:the )?(?:contract|receipt|documents?|paperwork|statement)\b|\bno (?:contract|receipt|paperwork)\b|\bpay (?:to )?(?:a|his|her) personal account\b", _I)
# เรื่องที่ผู้ใช้เล่าว่าตัวเองอ่าน/ดูมา (ละคร ข่าว นิยาย) ไม่ใช่ชีวิตจริง
_FICTION = re.compile(r"ในละคร|ในหนัง|ในนิยาย|ในซีรีส์|ในเกม|ข่าวว่า|\bin (?:the|a) (?:movie|show|novel|series|game)\b", _I)

_ASK = {
    "number": ("ขอดูเอกสารที่มีตัวเลขจริง (สลิป สัญญา รายการเดินบัญชี) แล้วเทียบกับที่เขาบอก",
               "Ask to see the document with the real number (slip, contract, statement) and compare it with what was said"),
    "place_time": ("เรื่องที่อยู่ในเวลาเดียวกันเช็กได้จากสิ่งที่มีเวลากำกับ (รูป ใบเสร็จ การเช็คอิน) — ถามตรงๆ ด้วยน้ำเสียงปกติ ไม่ใช่กล่าวหา",
                   "Where someone was at a given time can be checked against things with a timestamp (photos, receipts, check-ins) — ask plainly, not as an accusation"),
    "shifting": ("จดสิ่งที่เขาพูดแต่ละครั้งพร้อมวันที่ไว้ — เรื่องที่เปลี่ยนไปมาเห็นชัดขึ้นเมื่อเขียนเรียงกัน",
                 "Write down what was said each time, with dates — a story that keeps changing becomes obvious on paper"),
    "too_good": ("ของจริงไม่มีใครการันตีกำไรได้ — ขอดูใบอนุญาต (เช่น ก.ล.ต. 1207) ก่อนโอนเงินแม้แต่บาทเดียว",
                 "No real investment can guarantee profit — check the licence with the regulator before sending any money"),
    "pressure": ("การเร่งให้รีบหรือให้ปิดบังคือสัญญาณที่ต้องหยุด — เรื่องจริงรอให้คุณถามคนที่ไว้ใจได้เสมอ",
                 "Being rushed or told to keep it secret is a reason to stop — a real offer can always wait while you ask someone you trust"),
    "gaslight": ("สิ่งที่คุณเห็นหรือได้ยินเองมีค่า — จดไว้พร้อมวันเวลา และเล่าให้คนนอกที่ไว้ใจฟัง",
                 "What you saw or heard yourself counts — write it down with the date and time, and tell someone outside you trust"),
    "no_proof": ("ไม่มีเอกสาร = ไม่ควรจ่ายหรือเซ็นอะไรเพิ่ม จนกว่าจะได้เห็นสัญญาหรือใบเสร็จ",
                 "No paperwork means no more paying or signing until you've seen a contract or receipt"),
}
_WHAT = {
    "number": ("ตัวเลขที่บอกไม่ตรงกับเอกสาร", "the number said doesn't match the document"),
    "place_time": ("บอกว่าอยู่ที่หนึ่ง แต่มีคนเห็นอีกที่", "said they were in one place but were seen in another"),
    "shifting": ("เรื่องที่เล่าเปลี่ยนไปมา", "the story keeps changing"),
    "too_good": ("ข้อเสนอดีเกินจริง", "an offer that sounds too good to be true"),
    "pressure": ("ถูกเร่งหรือให้ปิดเป็นความลับ", "being rushed or told to keep it secret"),
    "gaslight": ("บอกว่าคุณคิดไปเอง ทั้งที่คุณเห็นเอง", "being told you imagined what you saw yourself"),
    "no_proof": ("ไม่ยอมให้ดูหลักฐาน", "won't show any proof"),
}


def _who_before(text: str, pos: int) -> str:
    """คนในเรื่องที่อยู่ใกล้จุดนั้นที่สุด (ก่อนหน้า) — ไม่พบ = '' (ไม่เดาชื่อ)"""
    best = ""
    for m in _WHO.finditer(text, 0, pos + 1):
        best = m.group(1)
    return best


def _amount(num: str, unit: str | None) -> float:
    v = float(num.replace(",", ""))
    mult = {"k": 1e3, "พัน": 1e3, "หมื่น": 1e4, "แสน": 1e5, "ล้าน": 1e6}.get((unit or "").lower(), 1)
    return v * mult


def check(text: str) -> list[dict]:
    """จุดที่ไม่ตรงกันในเรื่องที่เล่า — [{kind, who, quote}] เรียงตามที่เจอ · ไม่เจอ = []"""
    t = str(text or "")
    if not t.strip() or _FICTION.search(t):
        return []
    out = []

    def add(kind, m):
        if any(x["kind"] == kind for x in out):
            return
        quote = re.sub(r"\s+", " ", m.group(0)).strip()[:120]
        out.append({"kind": kind, "who": _who_before(t, m.start()) or _who_before(t, m.end()), "quote": quote})

    for m in _NUMBER.finditer(t):
        a, b = _amount(m.group(1), m.group(2)), _amount(m.group(3), m.group(4))
        if a and b and abs(a - b) / max(a, b) >= 0.05:          # ต่างกันเกิน 5% ถึงนับ (ปัดเศษไม่นับ)
            add("number", m)
            break
    for m in _PLACE.finditer(t):
        p1, p2 = m.group(1).strip("ที่"), m.group(2).strip("ที่")
        if not (p1.startswith(p2) or p2.startswith(p1)):      # "ตลาด" กับ "ตลาดเดียวกัน" = ที่เดียวกัน
            add("place_time", m)
            break
    for kind, rx in (("shifting", _SHIFT), ("too_good", _TOO_GOOD), ("pressure", _PRESSURE),
                     ("gaslight", _GASLIGHT), ("no_proof", _NO_PROOF)):
        m = rx.search(t)
        if m:
            add(kind, m)
    return out


def reply_block(findings: list[dict], lang: str = "th") -> str:
    """ย่อหน้าสั้นๆ ต่อท้ายคำตอบ — ไม่ตัดสินว่าใครโกหก บอกจุดที่ไม่ตรงกันและสิ่งที่เช็กได้"""
    if not findings:
        return ""
    en = lang == "en"
    head = "A few things in this story don't line up — worth checking before you decide:" if en else \
        "มีบางจุดในเรื่องนี้ที่ยังไม่ตรงกัน ควรเช็กก่อนตัดสินใจ:"
    lines = [head]
    # ไม่ใช้ bullet — จุดที่ไม่ตรงกันไม่ใช่ "ทางเลือก" (Canon มาตรา 11 นับบรรทัด bullet เป็นทางเลือก จำกัด 3)
    for f in findings[:3]:
        what = _WHAT[f["kind"]][1 if en else 0]
        who = f"{f['who']}: " if f["who"] else ""
        lines.append(f"{who}{what} — {_ASK[f['kind']][1 if en else 0]}")
    lines.append("This doesn't prove anyone is lying — it shows what to check." if en else
                 "ไม่ได้แปลว่าใครโกหกนะคะ แค่บอกว่าจุดไหนควรเช็กให้ชัดก่อน")
    return "\n".join(lines)


def llm_hint(findings: list[dict]) -> str:
    """บอก AI ว่าเจอจุดไม่ตรงกันอะไร — ให้พูดถึงอย่างนุ่มนวล ห้ามกล่าวหาว่าใครโกหก"""
    if not findings:
        return ""
    items = "; ".join(f"{_WHAT[f['kind']][0]}" + (f" ({f['who']})" if f["who"] else "") for f in findings[:3])
    return (f"[ความสมเหตุสมผลของเรื่อง: เจอจุดที่ไม่ตรงกัน — {items} · ชี้ให้ผู้ใช้เห็นและบอกสิ่งที่ตรวจสอบได้ "
            "ห้ามสรุปว่าใครโกหก ห้ามวินิจฉัยนิสัยคน]")
