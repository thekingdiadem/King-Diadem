"""ตัวตรวจแบบเงื่อนไข — ประกอบจาก "แนวคิด" หลายส่วน (ใคร × ทำอะไร × กับอะไร) แทนรายการประโยค

ทำไม: ตัวตรวจเดิมส่วนใหญ่เป็นรายการวลี ("กลืนถ่าน" "กลืนแม่เหล็ก") — ของใหม่ที่ไม่อยู่ในรายการหลุดทั้งหมด
เช่น ก้อนล้างจาน (dishwasher pod) · แอปเงินกู้แบบใหม่ · วิธีหลอกลงทุนแบบใหม่
เจ้าของโปรเจกต์: "มันต้องเป็นเงื่อนไขนะ ไม่งั้นเดี๋ยวคนมันก็มีแอปโกงใหม่ หรือวิธีโกงแบบใหม่อีก"

หลัก:
  · กฎหนึ่งข้อ = แนวคิด 2–3 กลุ่มต้องเจอพร้อมกันในประโยคเดียว (ไม่ข้ามบรรทัด) + ข้อยกเว้นที่ชัด
  · แนวคิดเป็น "ประเภท" (สิ่งที่ไม่ใช่อาหาร · เงินที่ไม่ได้ขอ · ผลตอบแทนหลายเท่าในเวลาสั้น) ไม่ใช่ชื่อยี่ห้อ/ชื่อแอป
  · ทุกกฎคืนผลแบบเดียวกัน: Hit(rule, topic, risk, scam_flag) — kernel_voice.assess ผสานเข้าผลหลักจุดเดียว
  · ค่าเดิมได้ผลเดิมเสมอ ไม่ใช้ AI · tests/test_conditions.py ทดสอบทั้งกรณีที่ต้องจับและกรณีที่ต้องไม่จับ
"""
from __future__ import annotations

import re
from typing import NamedTuple


class Hit(NamedTuple):
    rule: str
    topic: str | None
    risk: int
    scam: str | None = None


def _rx(*parts: str) -> re.Pattern:
    return re.compile("|".join(parts), re.I)


def _near(a: re.Pattern, b: re.Pattern, text: str, gap: int = 60) -> bool:
    """แนวคิด a และ b อยู่ในประโยคเดียวกัน ห่างกันไม่เกิน gap ตัวอักษร (ลำดับไหนก็ได้)"""
    for sent in re.split(r"[\n.!?。！？]+", text):
        for m in a.finditer(sent):
            for n in b.finditer(sent):
                if abs(m.start() - n.start()) <= gap:
                    return True
    return False


# ══ 1) เด็ก × กลืน/กัด/เลีย × สิ่งที่ไม่ใช่อาหาร → ฉุกเฉิน (โทรศูนย์พิษวิทยา) ══════════════════════
CHILD = _rx(r"เด็ก(?!หนุ่ม|สาว|ฝึกงาน|เสิร์ฟ|ช่าง|เส้น)", r"ลูก(?!อม|ค้า|หมา|แมว|น้ำ|ชิ้น|บอล|ไม้|เต๋า|โป่ง|กวาด|จ้าง|ศิษย์|พี่ลูกน้อง|น้อง)", r"หลาน", r"ทารก",
            r"น้อง(?=\S{0,3}(?:อายุ|\d|ขวบ|เล็ก))", r"\b(?:toddler|baby|infant|kid|child|son|daughter|little one|my \d+[- ]?(?:year|month)[- ]?old)\b")
INGEST = _rx(r"กลืน", r"กัด", r"เลีย", r"แทะ", r"เคี้ยว", r"อม(?!ยิ้ม)", r"ดื่ม", r"(?<!ไม่)กิน(?!ข้าว|นม|ขนม|ผลไม้|อาหาร|เก่ง|ได้|ยาก|น้อย)", r"เอาเข้าปาก", r"เข้าปาก",
             r"\b(?:bit(?: into)?|ate|eaten|eating|swallow\w*|drank|drinking|lick\w*|chew\w*|suck(?:ed|ing) on|got into|put \w+ in (?:his|her|their) mouth)\b")
# ประเภท ไม่ใช่ชื่อยี่ห้อ: สารทำความสะอาด · ยา · เชื้อเพลิง/สารเคมี · นิโคติน · ของชิ้นเล็กอันตราย · พืช/เห็ด
NON_FOOD = _rx(r"น้ำยา(?!ล้างจาน(?!เครื่อง))\S{0,8}", r"ผงซักฟอก", r"ก้อน(?:ล้างจาน|ซักผ้า|ทำความสะอาด)", r"เจลบอล", r"ไฮเตอร์", r"น้ำยาฟอกขาว", r"แอมโมเนีย", r"โซดาไฟ",
               r"ยา(?!สีฟัน|ดม|หม่อง)(?:\S{0,6})?(?:เม็ด|ของ(?:แม่|พ่อ|ยาย|ตา|คุณ)|ความดัน|เบาหวาน|นอนหลับ|แก้ปวด|พารา|ทั้งแผง|หลายเม็ด)?", r"วิตามิน", r"เม็ดยา",
               r"น้ำมัน(?!หอย|พืช|มะกอก)", r"ทินเนอร์", r"ยาฆ่า(?:แมลง|หญ้า|ยุง)", r"ยาเบื่อ", r"น้ำกรด", r"สารเคมี", r"ปุ๋ย", r"ลูกเหม็น",
               r"น้ำยาบุหรี่ไฟฟ้า|บุหรี่ไฟฟ้า|พอต|ก้นบุหรี่|นิโคติน", r"ถ่าน(?:กระดุม|นาฬิกา)?", r"แบตเตอรี", r"แม่เหล็ก", r"เหรียญ", r"เห็ด(?:ป่า|ในสวน|ไม่รู้จัก)",
               r"\b(?:dishwasher|laundry|detergent|cleaning)\s*(?:pod|tablet|capsule|packet)s?\b", r"\b(?:bleach|detergent|cleaner|ammonia|drain opener|lye|oven cleaner)\b",
               r"\b(?:pills?|tablets?|medicine|meds|medication|vitamins?|gummies|iron supplements?)\b", r"\b(?:antifreeze|gasoline|petrol|kerosene|lamp oil|lighter fluid|paint thinner)\b",
               r"\b(?:pesticide|insecticide|weed ?killer|rat poison|mothballs?)\b", r"\b(?:nicotine|vape (?:juice|liquid|pod)|e-?liquid|cigarette butts?)\b",
               r"\b(?:button )?batter(?:y|ies)\b", r"\bmagnets?\b", r"\bcoins?\b", r"\b(?:wild |unknown )?mushrooms?\b", r"under the sink")
# ของที่ไม่อันตรายมาก (มีคำตอบของเดิม CHILD_HOUSEHOLD) — ไม่ยกเป็นฉุกเฉิน
# กินยาตามที่หมอสั่ง/ตามฉลาก = ไม่ใช่อุบัติเหตุ
AS_PRESCRIBED = _rx(r"ตาม(?:ที่)?(?:หมอ|แพทย์|เภสัช)(?:สั่ง)?", r"ตามฉลาก", r"ตามขนาด", r"\b(?:as prescribed|prescribed (?:by|for)|the (?:doctor|pharmacist) (?:said|told|gave))\b")
MILD = _rx(r"แชมพู", r"สบู่", r"ยาสีฟัน", r"ครีมทาผิว", r"โลชั่น", r"แป้งเด็ก", r"ดินน้ำมัน", r"สีเทียน", r"\b(?:shampoo|soap|toothpaste|crayons?|play-?doh|chalk)\b")


# วัตถุชิ้นเล็ก (ถ่าน แม่เหล็ก เหรียญ) = เอกซเรย์/ผ่าตัด ("swallowed") · สารพิษและยา = ศูนย์พิษวิทยา ("overdose")
OBJECT = _rx(r"ถ่าน(?:กระดุม|นาฬิกา)?", r"แบตเตอรี", r"แม่เหล็ก", r"เหรียญ", r"\b(?:button )?batter(?:y|ies)\b", r"\bmagnets?\b", r"\bcoins?\b")


def child_ingest(t: str) -> Hit | None:
    if MILD.search(t) and not NON_FOOD.search(MILD.sub("", t)):
        return None
    if AS_PRESCRIBED.search(t):
        return None
    if _near(CHILD, INGEST, t, 40) and _near(INGEST, NON_FOOD, t, 45):
        return Hit("child_ingest", "swallowed" if OBJECT.search(t) else "overdose", 85)
    return None


# ══ 2) เตรียมตัวเผื่อตัวเองไม่อยู่ (ส่วนตัว + ซ้ำๆ) → สัญญาณเตือน ถามตรงๆ อย่างอ่อนโยน ══════════════════
ABSENCE = _rx(r"เผื่อ(?:วันที่|วันไหน|ตอนที่)?(?:ฉัน|หนู|ผม|เรา|กู)?(?:ไม่อยู่|จากไป|ไม่ได้อยู่(?:แล้ว)?|ตาย)", r"(?:หลัง|ถ้า)(?:วันที่)?(?:ฉัน|หนู|ผม|เรา|กู)(?:ไม่อยู่|จากไป)(?:แล้ว)?",
              r"\b(?:in case|for when|after) i'?m (?:not (?:here|around)|gone|no longer (?:here|around))\b", r"\bwhen i'?m (?:gone|no longer (?:here|around))\b")
PREP = _rx(r"เขียน(?:จดหมาย|โน้ต|ข้อความ)", r"จดหมายถึง", r"อัด(?:คลิป|เสียง)", r"ฝาก(?:ลูก|แมว|หมา|สัตว์เลี้ยง|ของ|รหัส)", r"(?:บอก|จด)รหัส", r"แจก(?:ของ|ข้าวของ)", r"จัดการ(?:หนี้|บัญชี|ของ)",
           r"\b(?:writ\w+|wrote|leav\w+|record\w*) (?:a |the |my )?(?:letters?|notes?|messages?|videos?)\b", r"\bletters? to\b", r"\b(?:giving|gave) away\b", r"\b(?:passwords?|who (?:gets|takes) my (?:cat|dog|pets?))\b")
PERSONAL = _rx(r"ทุก(?:คืน|วัน)", r"ช่วงนี้", r"เรื่อยๆ", r"แอบ", r"ถึง(?:แม่|พ่อ|ลูก|แฟน|ทุกคน|ครอบครัว)", r"\b(?:every (?:night|day)|lately|recently|been|to (?:my )?(?:mom|mum|dad|kids|family|everyone|wife|husband))\b")
PLANNING = _rx(r"พินัยกรรม", r"ทนาย", r"มรดก", r"ประกัน", r"ยังไง", r"อย่างไร", r"ควร", r"แบบไหน", r"ตัวอย่าง", r"\b(?:lawyer|estate|template|how (?:do|to|should)|insurance|executor)\b")


def absence_prep(t: str) -> Hit | None:
    if PLANNING.search(t):                  # วางแผนมรดก/ถามวิธีเขียนพินัยกรรม = เรื่องปกติของผู้ใหญ่
        return None
    if ABSENCE.search(t) and PREP.search(t) and PERSONAL.search(t):
        return Hit("absence_prep", "warning", 65)
    return None


# ══ 3) ค้นหาว่าต้อง "แค่ไหน" ถึงพอ (ความสูง จำนวนเม็ด ปริมาณ) ของตัวเอง → สัญญาณเตือน ══════════════════
RESEARCH = _rx(r"ค้นหา", r"เสิร์ช", r"เสิช", r"หาข้อมูล", r"อ่าน(?:เรื่อง)?", r"อยากรู้(?:ว่า)?", r"ดู(?:ว่า)", r"สงสัย(?:ว่า)?",
               r"\b(?:look(?:ed|ing)? up|googl\w*|search\w*|research\w*|reading (?:up )?about|wonder\w*|figur\w* out|trying to find out)\b")
# ไทย: ต้องมีคำบอกผลลัพธ์ ("ถึงจะตาย/ไม่รอด/ไม่ตื่น") — "ตึกนี้สูงกี่ชั้น" เป็นคำถามทั่วไป
THRESHOLD = _rx(r"(?:สูง(?:แค่ไหน|เท่าไหร่|กี่เมตร)|กี่ชั้น|กี่เม็ด|กี่แผง|ปริมาณ(?:เท่าไหร่|เท่าไร|แค่ไหน)|เท่าไหร่|แค่ไหน)\S{0,4}ถึง(?:จะ)?(?:ตาย|ไม่รอด|หลับไม่ตื่น|ไม่ตื่น|อันตรายถึงชีวิต)",
                r"\bhow (?:high|far|tall|long) (?:a |the )?(?:fall|drop|jump|building|bridge|floor)\b", r"\bhow many (?:pills|tablets|floors|stories|storeys)\b",
                r"\bhow much (?:\w+ )?(?:insulin|medication|medicine|pills|of (?:my|these|the) (?:meds|pills))\b", r"\b(?:lethal|fatal|deadly) (?:dose|amount|height)\b", r"\bhas to be\b(?=[^\n]{0,20}\b(?:fall|drop|high)\b)|\b(?:fall|drop)\b[^\n]{0,20}\bhas to be\b")
NOT_SELF = _rx(r"โทรศัพท์", r"มือถือ", r"ไข่", r"แก้ว", r"แมว", r"หมา", r"สุนัข", r"การบ้าน", r"ฟิสิกส์", r"นิยาย", r"เกม", r"รายงาน", r"สัตว์",
               r"\b(?:phone|egg|glass|cat|dog|pet|homework|physics|engineering|class|novel|story|game|parachute|bungee|skydiv\w*|drone|package|data)\b")


def lethality_research(t: str) -> Hit | None:
    if NOT_SELF.search(t):
        return None
    if _near(RESEARCH, THRESHOLD, t, 50):
        return Hit("lethality_research", "warning", 70)
    return None


# ══ 4) มิจฉาชีพตามพฤติกรรม (ไม่สนชื่อแอป) ═══════════════════════════════════════════════════════
# 4a เงินเข้าบัญชีทั้งที่ไม่ได้ขอ + ถูกทวง/ให้โอนคืน/คิดดอก → แอปเงินกู้เถื่อน หรือหลอกให้โอนคืน
UNASKED_MONEY = _rx(r"(?:โอน|ส่ง)(?:เงิน)?เข้ามา(?:ใน\S{0,6})?เอง", r"เงิน(?:โอน)?เข้า(?:บัญชี)?(?:มา)?เอง", r"(?:โอน|ส่ง)(?:เงิน)?(?:มา|เข้ามา)?\S{0,8}(?:ทั้งที่|โดย(?:ที่)?)(?:ไม่ได้|ไม่เคย)(?:ขอ|กู้|ยืม|กด)",
                    r"ไม่ได้กู้\S{0,10}(?:แต่)?(?:มี)?เงิน(?:โอน)?เข้า", r"\bmoney (?:just )?(?:showed up|appeared|landed|was (?:deposited|sent|transferred)) (?:in|into|to) my (?:account|wallet)\b",
                    r"\b(?:sent|deposited|transferred) (?:me )?(?:money|cash|funds)\b[^\n]{0,24}\bi (?:didn'?t|never|did not) (?:ask|borrow|appl|request)\w*\b")
DEMAND = _rx(r"ทวง", r"ให้(?:โอน)?คืน", r"ดอก(?:เบี้ย)?", r"ขู่", r"โทรตาม", r"ตามด่า", r"ประจาน", r"\b(?:demand\w*|asking (?:for|me to)|pay (?:it )?back|return it|interest|threaten\w*|harass\w*|calling me)\b")
# 4b ผลตอบแทนหลายเท่า/ร้อยละสูงต่อวัน × ช่วงเวลาสั้น × เรื่องเงิน → หลอกลงทุน
MULTIPLY = _rx(r"(?:สอง|สาม|สี่|ห้า|สิบ|[2-9]|10)\s*(?:เท่า|x\b|×)", r"เพิ่มเป็น(?:สอง|สาม)เท่า", r"\b(?:double|triple|quadruple|10x|5x|2x|3x)\b",
               r"\d{1,3}\s*%\s*(?:ต่อ|a|per|every|each|/)\s*(?:วัน|สัปดาห์|อาทิตย์|day|week)", r"กำไร\s*\d{2,}\s*%")
SHORT_TIME = _rx(r"(?:ใน|ภายใน)\s*(?:\d+|หนึ่ง|สอง|สาม|1|2|3)?\s*(?:วัน|สัปดาห์|อาทิตย์|เดือน|ชั่วโมง)", r"ต่อวัน|ทุกวัน|รายวัน",
                 r"\b(?:in|within) (?:a|one|two|three|\d+) (?:days?|weeks?|months?|hours?)\b", r"\b(?:daily|per day|a day|every day|overnight|by tomorrow)\b")
MONEY = _rx(r"เงิน", r"ลงทุน", r"เทรด", r"คริปโต", r"หุ้น", r"บาท", r"ฟอเร็กซ์", r"ทอง", r"กองทุน", r"\b(?:money|invest\w*|profit|returns?|crypto|bitcoin|forex|trading|stocks?|gold|fund|usdt|\$|usd|baht)\b")
NOT_MONEY_MULTIPLY = _rx(r"สูตร", r"ออกกำลัง", r"เวท", r"ยิม", r"คะแนน", r"\b(?:recipe|reps|workout|points|xp|followers|speed|dose)\b")


def scam_unasked_money(t: str) -> Hit | None:
    if _near(UNASKED_MONEY, DEMAND, t, 80) or (UNASKED_MONEY.search(t) and DEMAND.search(t)):
        return Hit("unasked_money", "scam", 75, "unasked_money")
    return None


def scam_multiplier(t: str) -> Hit | None:
    if NOT_MONEY_MULTIPLY.search(t):
        return None
    if MULTIPLY.search(t) and SHORT_TIME.search(t) and MONEY.search(t):
        return Hit("multiplier", "scam", 70, "guarantee")
    return None


# ══ 5) ความจำเป็นพื้นฐาน × ขาด/ถูกตัด/ถูกไล่ → ความเดือดร้อน (มีเบอร์จากทะเบียน core/hotlines.py) ══════════
FOOD = _rx(r"อาหาร", r"ข้าว(?!โพด|ของ)", r"นมผง", r"นม(?:ลูก|เด็ก)", r"กับข้าว", r"\b(?:food|groceries|formula|meals?|diapers?|nappies)\b")
POWER = _rx(r"ค่าไฟ", r"ไฟฟ้า", r"ตัดไฟ", r"\b(?:electric\w*|power (?:bill|company)|utilit\w*|gas bill|heating)\b")
WATER = _rx(r"ค่าน้ำ(?!มัน)", r"น้ำประปา", r"ประปา", r"ตัดน้ำ", r"\b(?:water (?:bill|company|was|got|is)|water (?:shut|cut) off|shut (?:off|down) (?:our|the|my) water)\b|\bshut off our water\b")
RENT = _rx(r"ค่าเช่า", r"ค่าห้อง", r"เจ้าของ(?:ห้อง|บ้าน|หอ)", r"\b(?:rent|landlord|evict\w*|throw us out|kick us out)\b")
# ไม่มีที่อยู่: บอกตรงๆ หรือ "นอนในรถ/ข้างถนน" ที่มีช่วงเวลาต่อเนื่อง ("ลูกอยู่ในรถกับพ่อ" "slept in the car on our road trip" ไม่นับ)
HOMELESS = _rx(r"ไม่มีที่(?:อยู่|นอน|ไป|ซุกหัวนอน)", r"คนไร้บ้าน", r"นอน(?:ใน)?(?:รถ|ข้างถนน|ป้ายรถเมล์|สถานีรถไฟ|สวนสาธารณะ)\S{0,8}(?:มา|หลาย|ทุกคืน|\d|สอง|สาม|เพราะ)",
               r"\b(?:homeless|nowhere to (?:live|sleep|stay|go))\b",
               r"\b(?:sleeping|living|staying) (?:in|on) (?:my |the |our )?(?:car|street|streets|park|station)\b(?=[^\n]{0,24}\b(?:for|since|every|weeks?|days?|nights?|months?|now)\b)")
LACK = _rx(r"ไม่มีเงิน", r"(?:จ่าย|ผ่อน)ไม่ไหว", r"หาเงินไม่ได้", r"ไม่พอ", r"ค้าง(?:จ่าย)?", r"(?:จะ|โดน|ถูก)(?:มา)?ตัด", r"ตัด(?:ไฟ|น้ำ)", r"ไล่(?:ออก|ที่)", r"ไม่มีที่",
           r"\b(?:can'?t (?:pay|afford|cover|buy)|cannot (?:pay|afford)|behind on|owe|shut\w* (?:off|down)|cut\w* (?:off|in half)|disconnect\w*|evict\w*|threaten\w* to|no money|ran out|run out|sleeping (?:in|on)|nowhere)\b")


def basic_needs(t: str) -> Hit | None:
    if (_near(POWER, LACK, t, 50) or _near(WATER, LACK, t, 50)):
        return Hit("utilities", "basic", 70)
    if HOMELESS.search(t) or _near(RENT, LACK, t, 60):
        return Hit("housing", "housing", 70)
    if _near(FOOD, LACK, t, 50):
        return Hit("food", "basic", 75)
    return None


RULES = (child_ingest, absence_prep, lethality_research, scam_unasked_money, scam_multiplier, basic_needs)


def check(text) -> list[Hit]:
    t = str(text or "")
    return [h for h in (r(t) for r in RULES) if h]
