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


# ── อาหารหมดจริง: "สิ่งสุดท้ายที่เหลือ" ของอาหาร (ห่อ/มื้อ/ถุงสุดท้าย · หมดบ้าน · ตู้เย็นว่าง) ─────────────────
# ไม่ต้องมีคำว่าเงิน — ของกินหมดคือพื้นขั้นต่ำหายไปแล้ว · ลดน้ำหนัก/สินค้าหมดสต็อก ไม่นับ
FOOD_ANY = _rx(r"มาม่า", r"บะหมี่", r"ไวไว", r"ยำยำ", r"ข้าว(?!โพด|ของ)", r"อาหาร", r"กับข้าว", r"นม(?:ผง|ลูก|เด็ก)", r"ขนมปัง", r"ไข่",
               r"\b(?:food|rice|noodles?|ramen|bread|formula|groceries|eggs?|cans? of \w+)\b")
LAST_OUT = _rx(r"(?:ห่อ|มื้อ|ถุง|กระป๋อง|ซอง|กล่อง|ฟอง|แผ่น)สุดท้าย", r"(?:หมด|เกลี้ยง)(?:บ้าน|ตู้|แล้ว)", r"(?<!ไม่)หมด(?!อายุ|เขต|ห่วง|แรง|ใจ)", r"ตู้เย็นว่าง",
               r"เหลือ(?:แค่|อยู่)?\S{0,10}(?:เดียว|สุดท้าย)",
               r"\b(?:last (?:pack(?:et)?|can|bag|box|meal|bit|egg)|ran out of|run out of|out of (?:food|rice)|nothing (?:left )?to eat|(?:fridge|cupboard|pantry) is (?:empty|bare))\b")
FOOD_OK = _rx(r"ลดน้ำหนัก", r"ไดเอท", r"คุมอาหาร", r"ไปซื้อ", r"ซื้อ(?:เพิ่ม|มาใหม่|ใหม่)", r"สต็อก", r"ร้าน\S{0,6}หมด", r"ขายหมด", r"หมดอายุ", r"กินหมด", r"หมดจาน", r"อิ่ม", r"อร่อย",
              r"\b(?:diet\w*|sold out|out of stock|go(?:ing)? (?:to )?(?:buy|shopping)|restock|expired)\b")


# อาหารต้องมาก่อนคำว่าหมด/สุดท้ายติดๆ กัน — "เอาเงินไปหมด ไม่ให้กินข้าว" คือเรื่องเงิน ไม่ใช่ข้าวหมด
_FOOD_THEN_OUT = re.compile("(?:" + FOOD_ANY.pattern + r")\S{0,10}\s?(?:" + LAST_OUT.pattern + ")", re.I)
_OUT_OF_FOOD = re.compile(r"\b(?:ran out of|run out of|out of|last (?:pack(?:et)?|can|bag|box) of)\s(?:\w+\s)?(?:food|rice|noodles?|ramen|bread|formula|groceries|eggs?)\b|"
                          r"\b(?:nothing (?:left )?to eat|(?:fridge|cupboard|pantry) is (?:empty|bare))\b", re.I)


def food_floor(t: str) -> Hit | None:
    if (_FOOD_THEN_OUT.search(t) or _OUT_OF_FOOD.search(t)) and not FOOD_OK.search(t):
        return Hit("food_floor", "basic", 75)
    return None


# ── ฝากคนที่ต้องดูแล + หมดแรงจะสู้ต่อ = สัญญาณบอกลา (ของผู้ใช้เอง หรือของคนที่โทรมาเล่า) ─────────────────────
ENTRUST = _rx(r"ฝาก(?:ดูแล|เลี้ยง)?\S{0,3}(?:ลูก|น้อง|แม่|พ่อ|ยาย|ตา|ย่า|ปู่|หลาน|แมว|หมา|สัตว์เลี้ยง)", r"(?:ช่วย)?ดูแล(?:ลูก|น้อง|แม่|พ่อ|หลาน|แมว|หมา)\S{0,4}(?:แทน|ด้วย|ให้)",
              r"\b(?:take care of|look after|watch over|raise) (?:my|the|our) (?:kids?|children|son|daughter|baby|brother|sister|mom|mum|dad|cat|dog|pets?)\b")
GIVE_UP = _rx(r"เหนื่อยเกิน(?:กว่า)?(?:ที่)?จะ(?:สู้|อยู่|ไป|ทน)", r"(?:สู้|อยู่|ไป|ทน)ต่อไม่ไหว", r"ไม่ไหวแล้ว", r"ยอมแพ้แล้ว", r"หมดแรง(?:จะ)?(?:สู้|อยู่)", r"ไม่อยาก(?:สู้|อยู่)(?:ต่อ)?แล้ว",
              r"\b(?:can'?t (?:go on|keep going|do this anymore|fight (?:it |this )?any ?more|take it any ?more)|too tired to (?:fight|go on|keep going|live)|(?:i'?m |i am )?giving up|done fighting)\b")
TEMP_AWAY = _rx(r"ไป(?:ต่าง)?จังหวัด", r"ไปทำงาน", r"ไปเที่ยว", r"ไปเรียน", r"เข้าเวร", r"ไปต่างประเทศ", r"ช่วง(?:ที่)?ไป", r"\b(?:business trip|vacation|travel\w*|while i'?m (?:away|at work)|for the weekend)\b")
OTHER_SPEAKER = _rx(r"(?:แม่|พ่อ|เพื่อน|แฟน|พี่|น้อง|ลูก|ยาย|ตา|ป้า|น้า|อา|สามี|ภรรยา|เมีย|ผัว)\S{0,8}(?:โทรมา|ทักมา|ส่งข้อความ|ไลน์มา|บอกว่า|พูดว่า)",
                    r"\b(?:my )?(?:mom|mum|dad|friend|sister|brother|wife|husband|son|daughter|partner) (?:called|texted|messaged|said|told me)\b")


def entrust_giveup(t: str) -> Hit | None:
    if _near(ENTRUST, GIVE_UP, t, 90) and not TEMP_AWAY.search(t):
        return Hit("entrust_giveup", "someone" if OTHER_SPEAKER.search(t) else "warning", 75)
    return None


# ── ยกสิ่งที่รักให้คนอื่น พร้อมคำปิดท้ายแบบจบ ("ดีที่สุดแล้ว" "ไม่ต้องใช้อีกแล้ว") — ย้ายบ้าน/แพ้ขน ไม่นับ ─────────────
GIVE_AWAY = _rx(r"(?:ยก|เอา|ส่ง)(?:หมา|แมว|สุนัข|น้อง(?:หมา|แมว)|สัตว์เลี้ยง|ของรัก|ของ\S{0,6})\S{0,8}(?:ไป)?ให้", r"แจก(?:ของ|ข้าวของ|เสื้อผ้า)\S{0,8}(?:หมด|ทั้งหมด|ไปแล้ว)",
                r"\b(?:gave|giving|give|handed|been giving) (?:away )?(?:my|all my|her|his|their|all (?:her|his|their)) (?:dog|cat|pets?|puppy|kitten|things|stuff|belongings|guitar|books|clothes|plants|records|vinyl|art|jewel(?:le)?ry|games|collection|favou?rite \w+)\b")
FINAL_NOTE = _rx(r"ดีที่สุดแล้ว", r"ดีกว่า(?:อยู่กับ)?(?:ฉัน|ผม|หนู|เรา)", r"ไม่(?:ต้อง|ได้)ใช้(?:มัน)?(?:อีก)?แล้ว", r"จะได้มีคนดูแล", r"(?:ฉัน|ผม|หนู)ดูแล(?:เขา|มัน)ไม่ได้อีกแล้ว",
                 r"\b(?:for the best|won'?t (?:need|be needing) (?:it|them)|better off (?:with|without)|someone (?:who can|to) (?:take care|look after))\b")
GIVE_OK = _rx(r"ย้าย(?:บ้าน|ห้อง|หอ|งาน|ไป)", r"แพ้ขน", r"เจ้าของ(?:ห้อง|หอ|คอนโด)ไม่ให้", r"ห้ามเลี้ยง", r"ทารก|คลอด|ตั้งครรภ์", r"บริจาค",
              r"\b(?:moving|move (?:to|abroad|out)|allerg\w*|landlord|no pets|new (?:baby|apartment|job)|donat\w*|decluttering)\b")


THIRD = _rx(r"\b(?:she|he|they|her|his|my (?:roommate|friend|sister|brother|mom|mum|dad|son|daughter|partner|wife|husband))\b",
            r"(?:เพื่อน|พี่|น้อง|แม่|พ่อ|ลูก|แฟน|รูมเมท)\S{0,6}(?:เขา|เธอ)?\S{0,4}(?:ยก|แจก|บอกว่า)")


def giveaway_final(t: str) -> Hit | None:
    if _near(GIVE_AWAY, FINAL_NOTE, t, 120) and not GIVE_OK.search(t):
        return Hit("giveaway_final", "someone" if THIRD.search(t) and not re.search(r"\b(?:i|i'?ve|my own)\b|ฉัน|ผม|หนู(?!ๆ)", t, re.I) else "warning", 65)
    return None


# ── ขอโทษแบบบอกลา: "ขอโทษที่เป็นลูกที่ไม่ดี" + "ต่อไปจะไม่ต้องเหนื่อย/ห่วงเพราะฉันแล้ว" — ได้งาน/เรียนจบ/มีเงินช่วย ไม่นับ ───────
RELIEF_SELF = _rx(r"ต่อไป\S{0,10}(?:จะ)?ไม่ต้อง(?:เหนื่อย|ลำบาก|เดือดร้อน|ห่วง|เป็นห่วง|ทน|ดูแล)\S{0,8}(?:เพราะ|กับ)?(?:หนู|ฉัน|ผม|เรา|กู)\S{0,4}(?:อีก)?แล้ว",
                  r"(?:จะ)?ไม่ต้อง(?:เหนื่อย|ลำบาก|เดือดร้อน|ห่วง)เพราะ(?:หนู|ฉัน|ผม|เรา|กู)(?:อีก)?(?:ต่อไป)?แล้ว",
                  r"\b(?:you|mom|mum|dad|everyone|they)(?:'ll| will)? (?:won'?t|will not|never) (?:have to|need to) (?:worry about|deal with|take care of|carry|put up with) me (?:any ?more|again)\b",
                  r"\bno one will have to (?:worry about|deal with) me (?:any ?more|again)\b")
APOLOGY_SELF = _rx(r"ขอโทษที่(?:เป็น|ทำให้)\S{0,12}(?:ไม่ดี|ภาระ|ผิดหวัง|เหนื่อย|ลำบาก)", r"\bsorry for (?:being|everything|all the trouble|being such a)\b")
GOODBYE = _rx(r"ลาก่อน", r"รักทุกคน", r"ฝากดูแล", r"\b(?:goodbye|forever|love you all|take care of (?:yourself|mom|dad))\b")
RELIEF_OK = _rx(r"ได้งาน", r"เรียนจบ", r"ทำงานแล้ว", r"มีเงิน", r"ส่งเงิน", r"ผ่อนให้", r"จ้าง", r"ซื้อ\S{0,8}ให้", r"หาย(?:ดี|ป่วย)แล้ว", r"เลิก(?:เหล้า|บุหรี่|พนัน)",
                 r"\b(?:got (?:a|the|my) (?:new )?job|graduat\w*|i'?ll (?:pay|send|cover)|hired|bought|recovered|sober)\b")


def farewell_apology(t: str) -> Hit | None:
    if (RELIEF_SELF.search(t) or (APOLOGY_SELF.search(t) and GOODBYE.search(t))) and not RELIEF_OK.search(t):
        return Hit("farewell_apology", "someone" if OTHER_SPEAKER.search(t) or re.search(r"ส่งไลน์มา|ส่งข้อความมา|ทักมา|\b(?:texted|messaged|wrote) me\b", t, re.I) else "warning", 80)
    return None


# ── ไฟแนนซ์/ธนาคารจะมายึดรถหรือบ้าน (ค้างงวด) ─────────────────────────────────────────────────────
REPO = _rx(r"(?:มา|จะ|โดน|ถูก)?ยึด(?:รถ|บ้าน|ทรัพย์|คอนโด|ที่ดิน)?", r"\b(?:repossess\w*|foreclos\w*|seize (?:my|our) (?:car|house|home))\b")
LOAN_CTX = _rx(r"ไฟแนนซ์", r"ค่างวด", r"ผ่อน(?:รถ|บ้าน)", r"สินเชื่อ", r"ขายทอดตลาด", r"\b(?:car payments?|mortgage|lender|finance company|behind on|bank)\b")


def repossession(t: str) -> Hit | None:
    if _near(REPO, LOAN_CTX, t, 60) and not re.search(r"ข่าว|ซีรีส์|ละคร|\bnews\b", t, re.I):
        return Hit("repossession", "debt", 60)
    return None


# ── มีคนทักเด็กแล้วสั่งให้เก็บแชทเป็นความลับ = ขั้นตอนล่อลวงเด็ก (ไม่ต้องรอให้ขอรูป) ───────────────────────────────
MINOR = _rx(r"ลูก(?:สาว|ชาย)?", r"หลาน", r"น้อง(?:สาว|ชาย)", r"เด็ก", r"\d{1,2}\s?(?:ขวบ|ปี)",
            r"\b(?:my|our) (?:\d{1,2}[- ]?(?:year|yr)[- ]?old|son|daughter|kid|child|niece|nephew|little (?:sister|brother))\b", r"\b\d{1,2}[- ]?(?:year|yr)[- ]?old\b")
CONTACT = _rx(r"(?:ทัก|แชท|ส่งข้อความ|คุย)\S{0,10}(?:มา|กับ|หา)", r"(?:ทัก|แชท|ส่งข้อความ|ชวนคุย)(?:หา)?(?:ลูก|หลาน|น้อง|เด็ก)", r"\b(?:messag\w*|texting|chatting|dm(?:ing|s)?|talking to)\b")
KEEP_SECRET = _rx(r"(?:ห้าม|อย่า)บอก(?:พ่อ|แม่|ใคร|ผู้ใหญ่|ที่บ้าน)", r"เก็บ\S{0,8}เป็นความลับ", r"ลบแชท", r"แอบคุย",
                  r"\b(?:keep (?:their|the|it|this|our) (?:chats?|messages?|conversations?|it|this)?\s?(?:a )?secret|don'?t tell (?:your )?(?:mom|mum|dad|parents|anyone)|delete (?:the|their) (?:chats?|messages))\b")


MEET_GIFT = _rx(r"ชวน\S{0,6}(?:ไป)?(?:เจอ|หา|ค้าง)", r"นัด(?:เจอ|ไปเจอ)", r"ออกไปเจอ", r"มารับ", r"ส่งของ(?:ขวัญ)?\S{0,4}ให้", r"เติม(?:เกม|เพชร|เงินเกม)ให้", r"ให้(?:โรบัค|เพชร|สกิน)",
                r"\b(?:meet (?:up|in person|him|her|them)|come over|pick (?:her|him) up|sent (?:her|him) (?:gifts?|money|robux|v-?bucks|skins)|buys? (?:her|him) (?:gifts?|robux|skins))\b")


def secret_chat_minor(t: str) -> Hit | None:
    if MINOR.search(t) and (CONTACT.search(t) or MEET_GIFT.search(t)) and KEEP_SECRET.search(t) and not re.search(r"เซอร์ไพรส์|วันเกิด|\bsurprise\b|\bbirthday\b", t, re.I):
        return Hit("secret_chat_minor", "online_grooming", 80)
    return None


# ── วางแผนเฉพาะเจาะจงแล้ว: เลือก "ที่" และ "วัน/เวลา" ไว้แล้วโดยไม่มีงานหรือกิจกรรมใดรองรับ ───────────────────────
PLACE = _rx(r"(?:ที่|สถานที่|จุด|วิธี)", r"\b(?:place|spot|location|way|method|bridge|building)\b")
WHEN_ = _rx(r"(?:วัน|เวลา|คืน|ตอนไหน)", r"\b(?:day|date|time|night|hour|moment)\b")
CHOSEN = _rx(r"(?:เลือก|กำหนด|ตัดสินใจ|คิด)\S{0,6}(?:ไว้)?แล้ว", r"\b(?:i'?ve|i have|already) (?:already )?(?:picked|chosen|chose|decided on|set|planned|got)\b")
EVENT = _rx(r"งาน(?:แต่ง|บวช|ศพ|เลี้ยง|วันเกิด|เปิด)", r"ประชุม", r"เที่ยว", r"วันเกิด", r"สัมภาษณ์", r"ย้าย", r"สอบ", r"นัด", r"ปาร์ตี้", r"ขอแต่งงาน", r"แต่งงาน", r"บวช", r"ทริป", r"เดินทาง", r"ถ่ายรูป", r"จัดงาน", r"เปิดร้าน",
            r"\b(?:wedding|party|trip|vacation|holiday|meeting|interview|birthday|propos\w*|ceremony|mov(?:e|ing)|exam|launch|shoot|event|reunion|date night|honeymoon|picnic|concert|dinner|lunch|surprise|celebrat\w*)\b")


def plan_specific(t: str) -> Hit | None:
    if CHOSEN.search(t) and _near(PLACE, WHEN_, t, 24) and not EVENT.search(t):
        return Hit("plan_specific", "warning", 70)
    return None


# ── ค่าใช้จ่ายจำเป็นที่ใกล้ครบกำหนด แต่ยังไม่มีเงิน (ค่าเทอม ค่ารักษา ค่างวด) ───────────────────────────────────
BILL = _rx(r"ค่าเทอม", r"ค่าเรียน", r"ค่าบำรุง", r"ค่ารักษา", r"ค่าผ่าตัด", r"ค่างวด", r"ค่าผ่อน", r"ค่ายา", r"ค่าประกันตัว",
           r"\b(?:tuition|school fees?|medical bill|hospital bill|surgery|installment|car payment|loan payment|bail)\b")
DUE = _rx(r"(?:ต้อง)?จ่าย\S{0,6}(?:พรุ่งนี้|อาทิตย์หน้า|สัปดาห์หน้า|เดือนหน้า|สิ้นเดือน|วันที่\s?\d+|ภายใน)", r"ครบกำหนด", r"ถึงกำหนด", r"ใกล้(?:จะ)?ถึงกำหนด",
          r"\b(?:due (?:tomorrow|next week|on|by|this|in)|deadline|by friday|by monday)\b")
NO_FUNDS = _rx(r"ยัง(?:หา)?เงินไม่ได้", r"หาเงินไม่ทัน", r"ไม่มีเงิน", r"ยังไม่มีเงิน", r"เงินไม่พอ", r"ไม่รู้จะเอาเงินที่ไหน",
               r"\b(?:don'?t have (?:the )?money|no money|can'?t (?:pay|afford)|haven'?t (?:got|found) the money|short on (?:money|cash))\b")


def bill_due(t: str) -> Hit | None:
    if BILL.search(t) and DUE.search(t) and NO_FUNDS.search(t):
        return Hit("bill_due", "debt", 55)
    return None


# ── มิจฉาชีพแบบโครงสร้าง (ไม่ผูกกับชื่อแอป/ชื่อหน่วยงาน — วิธีใหม่ที่โครงเดิมก็จับได้) ─────────────────────────
# A. จ่ายก่อนถึงจะได้: เงินกู้อนุมัติ/รางวัล/ถอนเงิน/ปลดล็อกยอด แต่ต้องจ่ายค่าธรรมเนียม ภาษี มัดจำก่อน
RECEIVE = _rx(r"อนุมัติ", r"สินเชื่อ\S{0,4}(?:ผ่าน|อนุมัติ)", r"กู้ผ่าน", r"ก่อนเงินเข้า", r"ถูกรางวัล", r"ได้รับรางวัล", r"ได้รางวัล", r"ถอน(?:เงิน)?(?:ได้|ออก)?", r"ปลดล็อก", r"รับเงิน", r"เงินคืน", r"ยอดค้าง(?:ถอน|รับ)", r"พัสดุ",
              r"\b(?:loan (?:is )?approved|approved for|you(?:'ve)? won|won (?:a|the)|prize|lottery|withdraw\w*|unlock|release (?:the |my )?funds|refund|inheritance|parcel|package)\b")
PAY_FIRST = _rx(r"(?:ต้อง|ให้)(?:โอน|จ่าย|เติม|วาง|ชำระ)\S{0,20}ก่อน", r"ค่าธรรมเนียม", r"ค่าดำเนินการ", r"ค่าค้ำประกัน", r"ค่า(?:ภาษี|ประกัน)\S{0,6}ก่อน", r"จ่ายภาษีก่อน",
                r"วางมัดจำ", r"มัดจำเพิ่ม", r"เติมเงินก่อน",
                r"\b(?:pay (?:a |the )?(?:small )?(?:fee|tax|deposit|charge)|upfront (?:fee|payment)|processing fee|release fee|clearance fee|(?:need|have) to (?:deposit|pay) \S+ (?:first|before)|deposit (?:crypto|usdt|money|funds)? ?first)\b")
PAY_FIRST_OK = _rx(r"ธนาคาร(?:ออมสิน|กรุงไทย|กสิกร|ไทยพาณิชย์|กรุงเทพ|กรุงศรี|ทหารไทย|ธกส)\S{0,10}(?:สาขา|ที่สาขา)", r"สัญญาเช่า", r"เช่า(?:ห้อง|บ้าน|คอนโด)", r"ร้าน(?:อาหาร|ค้า)ของเรา", r"ลูกค้า(?:ต้อง|ให้)",
                   r"\b(?:security deposit for (?:the|my) apartment|landlord|our customers)\b")


def scam_pay_first(t: str) -> Hit | None:
    if _near(RECEIVE, PAY_FIRST, t, 70) and not PAY_FIRST_OK.search(t):
        return Hit("pay_first", "scam", 75, "story")
    return None


# B. รู้จักกันแค่ออนไลน์ ไม่เคยเจอตัว แต่ชวนลงทุน/ขอเงิน (หลอกให้รัก · ชวนลงทุนแพลตฟอร์ม)
MET_ONLINE = _rx(r"แอปหาคู่", r"รู้จัก(?:กัน)?(?:ทาง|ใน|จาก)(?:เฟซ|เฟส|ไลน์|ไอจี|ติ๊กต็อก|tiktok|แอป|เน็ต|เกม|ออนไลน์|โซเชียล|เทเลแกรม)", r"ไม่เคยเจอ(?:ตัว|กัน|หน้า)",
                 r"ยังไม่เคย(?:เจอ|เห็นหน้า)", r"คุยกันแต่ในแชท", r"ทักมา(?:ทาง|ใน)?(?:เฟซ|ไลน์|ไอจี|แชท)",
                 r"\b(?:met (?:him|her|them|this (?:guy|girl|man|woman))? ?on (?:instagram|facebook|tinder|bumble|hinge|a dating app|telegram|whatsapp|wechat|line|tiktok|discord|online|a game)|never met (?:in person|face to face)?|online (?:boyfriend|girlfriend|partner))\b")
ASK_MONEY = _rx(r"ลงทุน", r"แพลตฟอร์ม", r"คริปโต", r"เทรด", r"(?:ขอ)?ยืมเงิน", r"(?:ให้)?(?:โอน|ส่ง)เงิน", r"ค่าตั๋ว", r"ภาษีศุลกากร", r"ค่าส่งของขวัญ", r"ค่ารักษา\S{0,6}(?:เขา|แม่เขา)",
                r"\b(?:invest\w*|platform|crypto|trading|send (?:him|her|them)? ?money|needs? (?:money|cash|help paying)|wire|flight|plane ticket|customs fee|gift ?cards?|hospital bills?)\b")


def scam_online_only(t: str) -> Hit | None:
    if MET_ONLINE.search(t) and ASK_MONEY.search(t):
        return Hit("online_only_money", "scam", 75, "romance")
    return None


# C. ข้อความอ้างหน่วยงาน + ลิงก์/แอป + เร่งจ่าย/ยืนยัน (ค่าไฟค้าง · พัสดุติด · บัญชีถูกระงับ)
AUTH_ORG = _rx(r"การไฟฟ้า", r"ไฟฟ้า(?:ส่วนภูมิภาค|นครหลวง)?", r"การประปา", r"ประปา", r"ธนาคาร", r"สรรพากร", r"ไปรษณีย์", r"ขนส่ง", r"ศุลกากร", r"ตำรวจ", r"กรม\S{2,12}",
               r"\b(?:bank|irs|hmrc|post office|postal|usps|dhl|fedex|ups|customs|courier|toll|dmv|tax office|utility company|amazon|apple|microsoft|paypal|netflix)\b")
MSG_LINK = _rx(r"sms", r"เอสเอ็มเอส", r"ข้อความ", r"ลิงก์", r"ลิ้ง", r"กดลิงก์", r"คลิก", r"แอด(?:ไลน์)?", r"\.apk", r"โหลดแอป", r"สแกน\s?qr",
               r"\b(?:text(?:ed)?|sms|email(?:ed)?|link|click|tap here|qr code|download (?:the |an )?app|\.apk)\b")
PRESSURE = _rx(r"ค้าง(?:ชำระ|จ่าย)?", r"ภายใน(?:วันนี้|\d+\s?ชั่วโมง)", r"ไม่งั้น", r"มิฉะนั้น", r"ระงับ", r"(?:ถูก|จะ)ตัด", r"ยืนยันตัวตน", r"อัปเดตข้อมูล", r"ชำระ(?:ค่า)?", r"ค่าธรรมเนียม",
               r"\b(?:unpaid|overdue|suspend\w*|locked|verify|confirm your|update your|within 24|today or|or (?:your|we)|pay (?:now|the)|fee|penalty)\b")


def scam_link_pressure(t: str) -> Hit | None:
    if AUTH_ORG.search(t) and _near(MSG_LINK, PRESSURE, t, 80):
        return Hit("link_pressure", "scam", 75, "story")
    return None


# D. ให้จ่ายด้วยบัตรของขวัญ/บัตรเติมเงิน — หน่วยงานจริงไม่เคยรับเงินแบบนี้
GIFT_CARD = _rx(r"บัตรของขวัญ", r"บัตรเติมเงิน", r"บัตร(?:ทรู|เติม)มันนี่", r"กิฟต์การ์ด", r"\b(?:gift ?cards?|itunes cards?|google play cards?|steam cards?|apple cards?|prepaid cards?)\b")
GIFT_PAY = _rx(r"จ่าย", r"ชำระ", r"ซื้อ\S{0,6}(?:แล้ว)?(?:ส่ง|บอก)(?:รหัส|เลข)", r"ค่าปรับ", r"ภาษี", r"แก้(?:บัญชี|ปัญหา)",
               r"\b(?:pay|buy|purchase|read (?:me )?the (?:numbers|codes?)|send (?:a )?(?:photo|picture) of|fix (?:my|the) account|fine|tax|support|warrant)\b")


DEMANDED = _rx(r"(?:ให้|สั่งให้|บอกให้|ขอให้)(?:ไป)?(?:ซื้อ|จ่าย|ชำระ)", r"\b(?:asked|told|said|wants?|want(?:ed)?|demand\w*|instructed|insist\w*) (?:me |us )?(?:to )?(?:buy|pay|purchase|get)\b")


def scam_gift_card(t: str) -> Hit | None:
    # "ซื้อบัตรของขวัญให้แม่" "can I pay with a gift card at target" ไม่นับ — ต้องมีคนสั่งให้จ่ายด้วยบัตร
    if _near(GIFT_CARD, GIFT_PAY, t, 70) and (DEMANDED.search(t) or AUTH_ORG.search(t)) and not re.search(r"\bat (?:target|walmart|the store)\b|ที่ร้าน", t, re.I):
        return Hit("gift_card", "scam", 75, "impersonation")
    return None


# E. ญาติเดือดร้อนด่วน + ขอเงิน + ห้ามบอกใคร (หลานโดนจับ · ลูกเกิดอุบัติเหตุ) — ให้วางสายแล้วโทรหาเจ้าตัวเอง
RELATIVE = _rx(r"หลาน", r"ลูก(?:ชาย|สาว)?", r"น้อง", r"\b(?:grand(?:son|daughter|child|kid)|nephew|niece|son|daughter)\b")
TROUBLE = _rx(r"ติดคุก", r"โดนจับ", r"ถูกจับ", r"ประกันตัว", r"อุบัติเหตุ", r"ชนคน", r"(?:อยู่|เข้า)โรงพยาบาล", r"\b(?:jail|bail|arrest\w*|accident|hospital|in trouble|police station)\b")
SECRET_MONEY = _rx(r"(?:ห้าม|อย่า)บอก", r"เป็นความลับ", r"โอน(?:เงิน)?(?:ด่วน|ให้)", r"ค่าประกันตัว", r"\b(?:don'?t tell|keep (?:it|this) (?:a )?secret|bail money|send (?:the )?money|wire|gift cards?)\b")


def scam_family_emergency(t: str) -> Hit | None:
    if RELATIVE.search(t) and _near(TROUBLE, SECRET_MONEY, t, 90):
        return Hit("family_emergency", "scam", 80, "impersonation")
    return None


# F. โอนไปแล้วอีกฝ่ายหาย (บล็อก/ไม่ส่งของ/ติดต่อไม่ได้) — ถูกโกงไปแล้ว: ทางตามเงินคืนมาก่อน
PAID = _rx(r"โอน(?:เงิน|มัดจำ|ค่า\S{0,8})?(?:ไป|ให้)?(?:แล้ว)?", r"จ่าย(?:เงิน|มัดจำ)?(?:ไป)?แล้ว", r"\b(?:paid|sent (?:the )?money|transferred|wired|deposit(?:ed)?)\b")
VANISHED = _rx(r"(?:บล็อก|บล๊อก)(?:เรา|ฉัน|ผม)?", r"ติดต่อไม่ได้", r"หาย(?:เงียบ|ไปเลย)", r"ไม่ส่งของ", r"ไม่ได้ของ", r"ปิด(?:เพจ|ร้าน|เฟซ)หนี", r"ลบแชท",
               r"\b(?:blocked me|never (?:shipped|arrived|sent)|disappeared|ghosted|stopped (?:answering|replying)|deleted (?:the|their) (?:page|account)|can'?t reach)\b")


def scam_paid_vanished(t: str) -> Hit | None:
    if _near(PAID, VANISHED, t, 70):
        return Hit("paid_vanished", "scam", 70, "lost")
    return None


# G. งานง่ายรายได้สูง (กดไลค์ รีวิว ทำภารกิจ) แต่ต้องเติมเงิน/วางเงินก่อน
TASK_JOB = _rx(r"กด(?:ไลค์|ไลก์|หัวใจ|ติดตาม|แชร์)", r"รีวิว(?:สินค้า|ร้าน|โรงแรม)?", r"ทำภารกิจ", r"ภารกิจ", r"ทำยอด", r"สั่งซื้อ(?:สินค้า)?ทำยอด",
               r"\b(?:lik(?:e|ing) (?:\w+ )?(?:videos?|posts?)|rat(?:e|ing) (?:products?|hotels?|apps?)|review(?:ing)? (?:products?|hotels?)|tasks?|optimi[sz]ing (?:products|orders)|boost(?:ing)? (?:orders|ratings))\b")
TOP_UP = _rx(r"เติมเงิน", r"วางเงิน", r"วางมัดจำ", r"โอน(?:เงิน)?(?:เข้า)?(?:ระบบ|ก่อน)", r"ทุนสำรอง",
             r"\b(?:deposit\w*|top[- ]?up|recharge|pay (?:in|to start)|prepay\w*|send (?:usdt|crypto))\b")


EARN = _rx(r"ค่าคอม", r"คอมมิชชั่น", r"คอมมิชชัน", r"รายได้", r"ได้เงิน", r"ถอน", r"ค่าตอบแทน", r"งาน(?:เสริม|ออนไลน์|พาร์ทไทม์)?", r"วันละ\s?\d",
           r"\b(?:commission|earn\w*|income|job|recruit\w*|per (?:day|task)|/day|a day|paying \$?\d|salary|withdraw\w*)\b")


def scam_task_job(t: str) -> Hit | None:
    if _near(TASK_JOB, TOP_UP, t, 90) and EARN.search(t):
        return Hit("task_job", "scam", 75, "job")
    return None


# H. เจ้าหน้าที่ (อ้าง) สั่งให้อยู่ในสาย/เปิดกล้องตลอด และห้ามบอกใคร — ตัดผู้ใช้ออกจากคนรอบตัว
OFFICIAL = _rx(r"ตำรวจ", r"ดีเอสไอ", r"\bdsi\b", r"ปปง", r"ปปส", r"เจ้าหน้าที่", r"ศาล", r"อัยการ", r"สรรพากร", r"ศุลกากร",
               r"\b(?:police|officer|agent|fbi|irs|customs|court|prosecutor|detective|government)\b")
ISOLATE = _rx(r"วิดีโอคอล", r"เปิดกล้อง(?:ไว้)?(?:ตลอด)?", r"ห้ามวางสาย", r"อยู่ในสาย(?:ตลอด)?", r"(?:ห้าม|อย่า)บอก(?:ใคร|ครอบครัว|ญาติ|ที่บ้าน)", r"ให้เก็บเป็นความลับ", r"ไปเปิดห้อง",
              r"\b(?:video call|stay on (?:the )?(?:line|call|camera)|keep (?:the )?camera on|don'?t (?:tell|hang up)|keep (?:this|it) (?:confidential|secret)|check into a hotel|go somewhere alone)\b")


def scam_isolate_official(t: str) -> Hit | None:
    if _near(OFFICIAL, ISOLATE, t, 80):
        return Hit("isolate_official", "scam", 80, "impersonation")
    return None


# ── ข้อความลาทุกคน + "จะไม่รบกวนใครอีก" (ไม่ใช่อีเมลลาออก/ย้ายงาน/เกษียณ) ─────────────────────────────────
NO_BURDEN = _rx(r"(?:จะ)?ไม่(?:รบกวน|เป็นภาระ|ทำให้ใคร\S{0,6}ลำบาก)(?:ใคร|ทุกคน)?(?:อีก(?:แล้ว|ต่อไป)?)", r"ขอบคุณที่(?:ทน|อดทน)(?:กับ)?(?:ฉัน|ผม|หนู|กัน)?(?:มา|ได้)",
                r"\b(?:won'?t (?:bother|burden|trouble) (?:anyone|you(?: all)?|any of you) (?:again|any ?more)|thanks? (?:you )?for putting up with me|no longer be a burden)\b")
FAREWELL = _rx(r"(?:อีเมล|ข้อความ|จดหมาย|โพสต์|แชท)\S{0,4}ลา", r"บอกลา", r"ลาทุกคน", r"ลาก่อน", r"\b(?:goodbye|farewell|saying bye to everyone)\b")
JOB_MOVE = _rx(r"ลาออก", r"ย้าย(?:งาน|บริษัท|แผนก|ไป)", r"เกษียณ", r"วันสุดท้ายของการทำงาน", r"งานใหม่", r"ไปเรียนต่อ", r"ไปทำงานที่",
               r"\b(?:resign\w*|last day (?:at|of)|new job|retir\w+|moving to|transferr\w+|starting at)\b")


def farewell_no_burden(t: str) -> Hit | None:
    if NO_BURDEN.search(t) and FAREWELL.search(t) and not JOB_MOVE.search(t):
        return Hit("farewell_no_burden", "someone" if OTHER_SPEAKER.search(t) or re.search(r"เพื่อน|เขา|เธอ|\b(?:she|he|they|my (?:friend|coworker|colleague))\b", t, re.I) else "warning", 80)
    return None


# ── หยุดยา/หยุดรักษาเอง + "ไม่มีประโยชน์แล้ว" (ไม่ใช่หมอสั่งให้หยุด) ─────────────────────────────────────
STOP_CARE = _rx(r"(?:หยุด|เลิก|ไม่ยอม|ไม่)(?:กิน)?ยา", r"ทิ้งยา", r"ไม่(?:ยอม)?(?:ไป)?(?:หาหมอ|รักษา|ฟอกไต|ให้คีโม|ฉีดอินซูลิน)", r"ขอ(?:หยุด|เลิก)รักษา",
                r"\b(?:stopped (?:taking|using) (?:his|her|my|their)? ?(?:\w+ )?(?:meds|medications?|medicine|pills|insulin|inhaler)|refus\w* (?:his|her|my)? ?(?:meds|treatment|dialysis|chemo|insulin)|quit (?:his|her|my) (?:meds|treatment|dialysis))\b")
HOPELESS = _rx(r"ไม่มีประโยชน์", r"ไม่มีความหมาย", r"อยู่ไปก็เท่านั้น", r"อยู่ไปทำไม", r"ไม่อยาก(?:อยู่|รักษา)แล้ว", r"ปล่อยให้มันเป็นไป",
               r"\b(?:no point|what'?s the point|pointless|nothing to live for|tired of living|let (?:it|nature) take|ready to go|done with (?:it|life|all this))\b")
DOCTOR_OK = _rx(r"หมอ\S{0,6}(?:สั่ง|ให้|บอก)\S{0,4}(?:หยุด|เลิก|เปลี่ยน)", r"แพ้ยา", r"เปลี่ยนยา", r"\b(?:doctor (?:said|told|switched|stopped)|side effects|allergic)\b")


def stop_care_hopeless(t: str) -> Hit | None:
    if STOP_CARE.search(t) and HOPELESS.search(t) and not DOCTOR_OK.search(t):
        third = re.search(r"(?:พ่อ|แม่|ยาย|ตา|ปู่|ย่า|สามี|ภรรยา|เพื่อน|ลูก)|\b(?:my (?:dad|mom|mum|father|mother|grand\w+|husband|wife|friend|son|daughter|brother|sister)|he|she)\b", t, re.I)
        return Hit("stop_care_hopeless", "someone" if third else "warning", 80)
    return None


# ── เจ้าของหอ/บ้านขู่จะขนของออก ล็อกห้อง เปลี่ยนกุญแจ (การไล่ที่เอง ผิดกฎหมาย) ───────────────────────────────
EVICT_ACT = _rx(r"ขนของ\S{0,6}ออก", r"โยนของ", r"เอาของ\S{0,6}(?:ออก|ไปวาง)", r"(?:ล็อก|ล๊อก|ปิด)ห้อง", r"เปลี่ยน(?:กุญแจ|แม่กุญแจ)", r"ตัด(?:ไฟ|น้ำ)ห้อง", r"ไล่(?:ออก)?(?:จากห้อง|จากหอ)?",
                r"\b(?:throw (?:my|our) (?:stuff|things|belongings) out|change (?:the )?locks|lock (?:me|us) out|kick (?:me|us) out|put (?:my|our) (?:stuff|things) (?:outside|on the street))\b")


EVICT_THREAT = _rx(r"ขู่", r"ถ้าไม่(?:จ่าย|โอน)", r"ไม่งั้น", r"ค้าง", r"ภายใน", r"\b(?:threat\w*|if (?:i|we) don'?t pay|unless|behind on|overdue|by (?:friday|monday|tomorrow))\b")


def landlord_threat(t: str) -> Hit | None:
    if _near(RENT, EVICT_ACT, t, 80) and EVICT_THREAT.search(t) and not re.search(r"ย้ายห้อง|ย้ายไปห้อง|\bmoving rooms?\b", t, re.I):
        return Hit("landlord_threat", "housing", 70)
    return None


RULES = (child_ingest, absence_prep, lethality_research, scam_unasked_money, scam_multiplier, basic_needs,
         food_floor, entrust_giveup, giveaway_final, plan_specific, bill_due,
         scam_pay_first, scam_online_only, scam_link_pressure, scam_gift_card, scam_family_emergency, scam_paid_vanished,
         scam_task_job, scam_isolate_official, farewell_apology, repossession, secret_chat_minor,
         farewell_no_burden, stop_care_hopeless, landlord_threat)


def check(text) -> list[Hit]:
    t = str(text or "")
    return [h for h in (r(t) for r in RULES) if h]
