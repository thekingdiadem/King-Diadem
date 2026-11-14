"""
WORLD_MODEL/bio_axiom.py — BIO-AXIOM: พันธุกรรมของสัตว์ใน world model

เจ้าของโปรเจกต์: "ไบโอแอ็คเซี่ยม ก็คือพันธุกรรมของทุกสัตว์ในเวิลโมดูลนะ ควรอัพเดท"

ทะเบียนนี้เก็บข้อเท็จจริงทางพันธุกรรมพื้นฐานของสัตว์ ทั้งสัตว์เล็กใน small_animal_model.py และสัตว์ที่คนไทยเจอบ่อย
  chromosomes = จำนวนโครโมโซมในเซลล์ร่างกาย (2n) · None = ต่างกันตามชนิด/สายพันธุ์ จึงไม่ใส่ตัวเลขเดียว
  genome_gb   = ขนาดจีโนมโดยประมาณ (พันล้านคู่เบส) · None = ไม่ใส่ถ้าไม่มั่นใจ
  sex         = ระบบกำหนดเพศ: XY (ตัวผู้ XY) · ZW (ตัวเมีย ZW เช่นนก) · haplodiploid (ผึ้ง) · TSD (อุณหภูมิไข่กำหนด)
  facts       = ข้อเท็จจริงที่อธิบายได้และมีประโยชน์ (สีขน ลูกผสม โรคทางพันธุกรรม)

หลัก (เหมือน core/hotlines.py และ core/knowledge_pack_facts.py):
- ใส่เฉพาะตัวเลขที่เป็นที่ยอมรับกว้างขวาง · ไม่มั่นใจ = None แล้วบอกตรงๆ
- verified = False ทั้งหมดจนกว่าเจ้าของโปรเจกต์หรือผู้เชี่ยวชาญตรวจกับแหล่งอ้างอิง
- ANIMAL PERMANENT CORE ยังอยู่: ความรู้พันธุกรรมใช้เพื่อเข้าใจและดูแลชีวิต ไม่ใช่เพื่อทำร้าย
"""
from __future__ import annotations

import re

_I = re.I

# key → ข้อมูล · names = คำที่คนพิมพ์ (ไทย/อังกฤษ)
ANIMALS = {
    "human": {"th": "มนุษย์", "en": "human", "names": r"มนุษย์|คน(?:เรา)?(?=มีโครโมโซม|มี\s?dna)|\bhumans?\b", "chromosomes": 46, "genome_gb": 3.1, "sex": "XY",
              "facts": ["มนุษย์กับชิมแปนซีมีลำดับดีเอ็นเอเหมือนกันราว 98–99% ในส่วนที่เทียบกันได้",
                        "ความผิดปกติของจำนวนโครโมโซม เช่น ดาวน์ซินโดรม เกิดจากโครโมโซมคู่ที่ 21 เกินมาหนึ่งแท่ง (47 แท่ง)"]},
    "chimpanzee": {"th": "ชิมแปนซี", "en": "chimpanzee", "names": r"ชิมแปนซี|\bchimp(?:anzee)?s?\b", "chromosomes": 48, "genome_gb": 3.0, "sex": "XY",
                   "facts": ["ลิงใหญ่มีโครโมโซม 48 แท่ง มนุษย์มี 46 เพราะโครโมโซมบรรพบุรุษสองแท่งเชื่อมกันเป็นโครโมโซมคู่ที่ 2 ของมนุษย์"]},
    "dog": {"th": "หมา/สุนัข", "en": "dog", "names": r"หมา|สุนัข|น้องหมา|\bdogs?\b|\bpupp(?:y|ies)\b", "chromosomes": 78, "genome_gb": 2.4, "sex": "XY",
            "facts": ["หมาทุกพันธุ์ ตั้งแต่ชิวาวาถึงเกรทเดน เป็นสปีชีส์เดียวกัน ความต่างของขนาดส่วนใหญ่มาจากยีนไม่กี่ตัว เช่น IGF1",
                      "การผสมเลือดชิดเพื่อคงลักษณะพันธุ์ ทำให้บางพันธุ์เสี่ยงโรคทางพันธุกรรม เช่น สะโพกเสื่อม หรือหายใจลำบากในหมาหน้าสั้น"]},
    "cat": {"th": "แมว", "en": "cat", "names": r"แมว|น้องแมว|\bcats?\b|\bkittens?\b", "chromosomes": 38, "genome_gb": 2.5, "sex": "XY",
            "facts": ["แมวสามสีเกือบทั้งหมดเป็นตัวเมีย เพราะยีนสีส้ม/ดำอยู่บนโครโมโซม X ต้องมี X สองแท่งจึงแสดงได้ทั้งสองสี — แมวสามสีตัวผู้ (XXY) พบน้อยมากและมักเป็นหมัน",
                      "แมววิเชียรมาศ (สยาม) มีสีเข้มที่หน้า หู ขา หาง เพราะเอนไซม์สร้างสีทำงานเฉพาะบริเวณที่อุณหภูมิร่างกายต่ำกว่า",
                      "แมวขาวตาฟ้าจำนวนมากหูหนวกแต่กำเนิด จากยีนสีขาวเด่น (W) ที่มีผลต่อหูชั้นใน"]},
    "cow": {"th": "วัว", "en": "cattle", "names": r"วัว|โค(?!ร|ม|ล|วิด)|\bcows?\b|\bcattle\b", "chromosomes": 60, "genome_gb": 2.7, "sex": "XY",
            "facts": ["ลูกวัวแฝดต่างเพศ ตัวเมียมักเป็นหมัน (freemartin) เพราะได้ฮอร์โมนและเซลล์จากแฝดตัวผู้ผ่านรก"]},
    "buffalo": {"th": "ควาย/กระบือ", "en": "water buffalo", "names": r"ควาย|กระบือ|\bwater buffalo(?:es)?\b", "chromosomes": None, "genome_gb": None, "sex": "XY",
                "facts": ["ควายแม่น้ำมีโครโมโซม 50 แท่ง ส่วนควายปลักแบบที่เลี้ยงในไทยมี 48 แท่ง — ผสมกันได้ ลูกมี 49 แท่ง"]},
    "pig": {"th": "หมู/สุกร", "en": "pig", "names": r"หมู(?!ป่า)|สุกร|\bpigs?\b|\bswine\b", "chromosomes": 38, "genome_gb": 2.5, "sex": "XY",
            "facts": ["อวัยวะหมูมีขนาดใกล้มนุษย์ จึงเป็นสัตว์หลักในงานวิจัยปลูกถ่ายอวัยวะข้ามสายพันธุ์ด้วยการแก้ไขยีน"]},
    "horse": {"th": "ม้า", "en": "horse", "names": r"ม้า(?!ลาย)|\bhorses?\b", "chromosomes": 64, "genome_gb": 2.5, "sex": "XY",
              "facts": ["ม้า (64) ผสมกับลา (62) ได้ล่อ (63) — จำนวนโครโมโซมเป็นเลขคี่ จับคู่กันไม่ลงตัวตอนสร้างเซลล์สืบพันธุ์ ล่อจึงเกือบทั้งหมดเป็นหมัน"]},
    "donkey": {"th": "ลา", "en": "donkey", "names": r"(?<![ก-๙])ลา(?=\s|$|ตัว|มี|กับ|ผสม)|\bdonkeys?\b", "chromosomes": 62, "genome_gb": 2.4, "sex": "XY",
               "facts": ["ลาตัวผู้ผสมม้าตัวเมียได้ล่อ ส่วนม้าตัวผู้ผสมลาตัวเมียได้ hinny — ทั้งสองแบบมีโครโมโซม 63 แท่งและมักเป็นหมัน"]},
    "mule": {"th": "ล่อ", "en": "mule", "names": r"ล่อ(?=\s|$|เป็น|มี|ทำไม)|\bmules?\b", "chromosomes": 63, "genome_gb": None, "sex": "XY",
             "facts": ["ล่อเป็นลูกผสมม้ากับลา มีโครโมโซม 63 แท่ง (เลขคี่) จึงเกือบทั้งหมดเป็นหมัน"]},
    "goat": {"th": "แพะ", "en": "goat", "names": r"แพะ|\bgoats?\b", "chromosomes": 60, "genome_gb": 2.9, "sex": "XY", "facts": []},
    "sheep": {"th": "แกะ", "en": "sheep", "names": r"แกะ(?!สลัก)|\bsheep\b", "chromosomes": 54, "genome_gb": 2.6, "sex": "XY",
              "facts": ["แกะดอลลี่ (ค.ศ. 1996) เป็นสัตว์เลี้ยงลูกด้วยนมตัวแรกที่โคลนจากเซลล์ร่างกายของตัวเต็มวัย"]},
    "chicken": {"th": "ไก่", "en": "chicken", "names": r"ไก่|\bchickens?\b|\bhens?\b|\broosters?\b", "chromosomes": 78, "genome_gb": 1.1, "sex": "ZW",
                "facts": ["นกรวมทั้งไก่ใช้ระบบ ZW — ตัวเมียเป็น ZW ตัวผู้เป็น ZZ แม่จึงเป็นฝ่ายกำหนดเพศลูก (ตรงข้ามกับคน)",
                          "โครโมโซมไก่ส่วนใหญ่เป็นโครโมโซมขนาดเล็กมาก (microchromosome) ซึ่งพบบ่อยในนก"]},
    "duck": {"th": "เป็ด", "en": "duck", "names": r"เป็ด|\bducks?\b", "chromosomes": 80, "genome_gb": 1.2, "sex": "ZW", "facts": []},
    "pigeon": {"th": "นกพิราบ", "en": "pigeon", "names": r"นกพิราบ|\bpigeons?\b", "chromosomes": 80, "genome_gb": 1.1, "sex": "ZW", "facts": []},
    "elephant": {"th": "ช้างเอเชีย", "en": "Asian elephant", "names": r"ช้าง|\belephants?\b", "chromosomes": 56, "genome_gb": None, "sex": "XY",
                 "facts": ["ช้างมียีนต้านมะเร็ง TP53 หลายสิบชุด (คนมีชุดเดียว) อาจเป็นเหตุที่ตัวใหญ่และอายุยืนแต่เป็นมะเร็งน้อย",
                           "ช้างงาเล็กหรือไม่มีงาพบมากขึ้นในบางพื้นที่ที่ถูกล่าเอางาหนัก — แรงคัดเลือกจากมนุษย์เปลี่ยนพันธุกรรมของประชากรได้"]},
    "tiger": {"th": "เสือโคร่ง", "en": "tiger", "names": r"เสือโคร่ง|เสือขาว|\btigers?\b", "chromosomes": 38, "genome_gb": 2.4, "sex": "XY",
              "facts": ["เสือโคร่งขาวเกิดจากยีนด้อย SLC45A2 สองชุด — การผสมเลือดชิดเพื่อให้ได้เสือขาวทำให้เกิดตาเหล่ เพดานโหว่ และโรคอื่นๆ บ่อย"]},
    "lion": {"th": "สิงโต", "en": "lion", "names": r"สิงโต|\blions?\b", "chromosomes": 38, "genome_gb": 2.4, "sex": "XY",
             "facts": ["สิงโตผสมเสือโคร่งได้ (ไลเกอร์/ไทกอน) เพราะโครโมโซม 38 แท่งเท่ากัน แต่เกิดเฉพาะในที่เลี้ยง และมักมีปัญหาสุขภาพ"]},
    "honeybee": {"th": "ผึ้ง", "en": "honeybee", "names": r"ผึ้ง|\bbees?\b|\bhoneybees?\b", "chromosomes": 32, "genome_gb": 0.25, "sex": "haplodiploid",
                 "facts": ["ผึ้งตัวเมีย (นางพญาและผึ้งงาน) มีโครโมโซม 32 แท่ง ตัวผู้เกิดจากไข่ที่ไม่ได้ผสมจึงมีแค่ 16 แท่ง (haplodiploidy)",
                           "ผึ้งงานกับนางพญามียีนเหมือนกัน ที่ต่างกันคืออาหารตอนเป็นตัวอ่อน (นมผึ้ง) ซึ่งเปิดปิดการทำงานของยีน"]},
    "fruit_fly": {"th": "แมลงหวี่", "en": "fruit fly", "names": r"แมลงหวี่|\bfruit fl(?:y|ies)\b|\bdrosophila\b", "chromosomes": 8, "genome_gb": 0.14, "sex": "XY",
                  "facts": ["แมลงหวี่เป็นสัตว์ทดลองหลักของพันธุศาสตร์มากว่าร้อยปี — ยีนก่อโรคในคนจำนวนมากมีคู่เทียบในแมลงหวี่"]},
    "zebrafish": {"th": "ปลาม้าลาย", "en": "zebrafish", "names": r"ปลาม้าลาย|\bzebrafish\b", "chromosomes": 50, "genome_gb": 1.4, "sex": None,
                  "facts": ["ตัวอ่อนปลาม้าลายใส มองเห็นอวัยวะพัฒนาได้ จึงใช้ศึกษาพันธุกรรมการเจริญของหัวใจและสมอง"]},
    "crocodile": {"th": "จระเข้", "en": "crocodile", "names": r"จระเข้|\bcrocodiles?\b", "chromosomes": None, "genome_gb": None, "sex": "TSD",
                  "facts": ["จระเข้ไม่มีโครโมโซมเพศ — อุณหภูมิที่ไข่ได้รับระหว่างฟักเป็นตัวกำหนดเพศลูก"]},
    "sea_turtle": {"th": "เต่าทะเล", "en": "sea turtle", "names": r"เต่าทะเล|\bsea turtles?\b", "chromosomes": None, "genome_gb": None, "sex": "TSD",
                   "facts": ["ทรายที่อุ่นกว่าให้ลูกเต่าตัวเมียมากกว่า — โลกร้อนทำให้บางรังแทบไม่มีลูกตัวผู้ ซึ่งคุกคามประชากรในระยะยาว"]},
    # ── สัตว์เล็กใน small_animal_model.py ──
    "mouse": {"th": "หนูเมาส์", "en": "house mouse", "names": r"หนูเมาส์|หนูทดลอง|\bmice\b|\bmouse\b", "chromosomes": 40, "genome_gb": 2.7, "sex": "XY",
              "facts": ["หนูเมาส์มียีนส่วนใหญ่ตรงกับคน จึงเป็นสัตว์ทดลองหลักสำหรับศึกษาโรคทางพันธุกรรม"]},
    "rat": {"th": "หนูบ้าน/หนูแรท", "en": "brown rat", "names": r"หนูบ้าน|หนูแรท|หนูท่อ|\brats?\b", "chromosomes": 42, "genome_gb": 2.7, "sex": "XY",
            "facts": ["หนูบ้านบางกลุ่มดื้อยาเบื่อกลุ่มวาร์ฟารินจากการกลายพันธุ์ของยีน VKORC1 — ยาเบื่อยิ่งทำให้ประชากรที่ดื้อเพิ่มขึ้น"]},
    "rabbit": {"th": "กระต่าย", "en": "rabbit", "names": r"กระต่าย|\brabbits?\b|\bbunn(?:y|ies)\b", "chromosomes": 44, "genome_gb": 2.7, "sex": "XY", "facts": []},
    "guinea_pig": {"th": "หนูตะเภา", "en": "guinea pig", "names": r"หนูตะเภา|แกสบี้|\bguinea pigs?\b", "chromosomes": 64, "genome_gb": 2.7, "sex": "XY",
                   "facts": ["หนูตะเภาสร้างวิตามินซีเองไม่ได้ (เหมือนคน) เพราะยีน GULO เสีย ต้องได้วิตามินซีจากอาหารทุกวัน"]},
    "hamster": {"th": "แฮมสเตอร์ (ซีเรียน)", "en": "Syrian hamster", "names": r"แฮมสเตอร์|\bhamsters?\b", "chromosomes": 44, "genome_gb": None, "sex": "XY",
                "facts": ["แฮมสเตอร์แต่ละชนิดมีโครโมโซมไม่เท่ากัน — ซีเรียน 44 แท่ง ส่วนแฮมสเตอร์แคระบางชนิดมีน้อยกว่า"]},
    "gerbil": {"th": "เจอร์บิล (มองโกเลีย)", "en": "Mongolian gerbil", "names": r"เจอร์บิล|\bgerbils?\b", "chromosomes": 44, "genome_gb": None, "sex": "XY", "facts": []},
    "hedgehog": {"th": "เม่นแคระ", "en": "hedgehog", "names": r"เม่นแคระ|เม่น|\bhedgehogs?\b", "chromosomes": None, "genome_gb": None, "sex": "XY",
                 "facts": ["เม่นยุโรปมีโครโมโซม 88 แท่ง ส่วนเม่นแคระแอฟริกาที่เลี้ยงกันในไทยยังไม่ได้ใส่ตัวเลข เพราะยังไม่ได้ตรวจกับแหล่งอ้างอิง"]},
    "squirrel": {"th": "กระรอก", "en": "squirrel", "names": r"กระรอก|\bsquirrels?\b", "chromosomes": None, "genome_gb": None, "sex": "XY", "facts": []},
    "shrew": {"th": "ตุ่น/หนูผี", "en": "shrew", "names": r"หนูผี|\bshrews?\b", "chromosomes": None, "genome_gb": None, "sex": "XY", "facts": []},
    "chipmunk": {"th": "ชิปมังก์", "en": "chipmunk", "names": r"ชิปมังก์|\bchipmunks?\b", "chromosomes": None, "genome_gb": None, "sex": "XY", "facts": []},
    "vole": {"th": "หนูนา", "en": "vole", "names": r"หนูนา|\bvoles?\b", "chromosomes": None, "genome_gb": None, "sex": "XY", "facts": []},
    "mole": {"th": "ตุ่นดิน", "en": "mole", "names": r"ตุ่นดิน|\bmoles?\b(?! on)", "chromosomes": None, "genome_gb": None, "sex": "XY", "facts": []},
}
_FACTS_EN = {
    "cat": ["Calico cats are almost always female: the orange/black coat gene sits on the X chromosome, so two X chromosomes are needed to show both colours. Male calicos (XXY) are rare and usually sterile.",
            "Siamese colouring comes from a temperature-sensitive pigment enzyme that works only in cooler body parts — face, ears, paws and tail."],
    "dog": ["Every dog breed, from Chihuahua to Great Dane, is the same species; much of the size difference comes from a few genes such as IGF1."],
    "horse": ["A horse (64) crossed with a donkey (62) gives a mule (63) — an odd number that can't pair evenly in sex cells, so mules are almost always sterile."],
    "mule": ["Mules have 63 chromosomes (odd), so they are almost always sterile."],
    "donkey": ["Donkey × horse offspring have 63 chromosomes and are usually sterile."],
    "chicken": ["Birds use the ZW system: females are ZW, males ZZ — so the mother determines the chick's sex, the reverse of humans."],
    "honeybee": ["Female bees have 32 chromosomes; males hatch from unfertilised eggs and have 16 (haplodiploidy).",
                 "Workers and queens share the same genes — larval diet (royal jelly) switches genes on and off."],
    "tiger": ["White tigers carry two copies of a recessive SLC45A2 variant; inbreeding to produce them causes crossed eyes, cleft palate and other problems."],
    "human": ["Humans and chimpanzees share about 98–99% of comparable DNA sequence.", "Down syndrome results from an extra copy of chromosome 21 (47 in total)."],
    "chimpanzee": ["Great apes have 48 chromosomes; humans have 46 because two ancestral chromosomes fused into human chromosome 2."],
    "crocodile": ["Crocodiles have no sex chromosomes — egg incubation temperature sets the sex."],
    "sea_turtle": ["Warmer sand produces more female hatchlings — rising temperatures leave some nests almost entirely female."],
    "elephant": ["Elephants carry dozens of copies of the tumour-suppressor gene TP53 (humans have one), which may explain their low cancer rates."],
}
_RX = {k: re.compile(v["names"], _I) for k, v in ANIMALS.items()}
VERIFIED = False

_ASK = re.compile(r"โครโมโซม|พันธุกรรม|ยีน|ดีเอ็นเอ|\bdna\b|จีโนม|ลูกผสม|ผสมพันธุ์กับ|ผสมกับ|ผสมกันได้|เป็นหมัน|กำหนดเพศ|สามสี|ทำไม(?:ถึง)?(?:เป็น)?(?:ตัวเมีย|ตัวผู้|ขาว)|"
                  r"\bchromosomes?\b|\bgenetic\w*\b|\bgenes?\b|\bgenome\b|\bhybrid\b|\bsterile\b|\bcalico\b|\bsex determination\b", _I)
_SEX = {"XY": ("ระบบ XY (ตัวผู้ XY · ตัวเมีย XX)", "XY system (male XY, female XX)"),
        "ZW": ("ระบบ ZW (ตัวเมีย ZW · ตัวผู้ ZZ — แม่เป็นฝ่ายกำหนดเพศลูก)", "ZW system (female ZW, male ZZ — the mother determines sex)"),
        "haplodiploid": ("ตัวเมียมาจากไข่ที่ผสม ตัวผู้มาจากไข่ที่ไม่ได้ผสม (haplodiploidy)", "females from fertilised eggs, males from unfertilised eggs (haplodiploidy)"),
        "TSD": ("อุณหภูมิระหว่างฟักไข่เป็นตัวกำหนดเพศ (ไม่มีโครโมโซมเพศ)", "egg incubation temperature determines sex (no sex chromosomes)")}


def animals_in(text: str) -> list[str]:
    t = str(text or "")
    found = []
    for k, rx in _RX.items():
        m = rx.search(t)
        if m:
            found.append((m.start(), k))
    found.sort()
    out = [k for _, k in found]
    # "หนูตะเภา" "หนูบ้าน" ไม่ต้องนับ "หนูเมาส์" ซ้ำ · "ล่อ" มาพร้อม "ม้า"/"ลา" ได้
    return list(dict.fromkeys(out))


def lookup(key: str) -> dict | None:
    return ANIMALS.get(key)


def reply(text: str, lang: str = "th", footer: bool = True):
    """ตอบคำถามพันธุกรรมของสัตว์ — ต้องมีทั้งชื่อสัตว์และคำถามเรื่องพันธุกรรม ไม่ใช่ก็ None"""
    t = str(text or "")
    if not _ASK.search(t):
        return None
    keys = animals_in(t)[:3]
    if not keys:
        return None
    en = lang == "en"
    blocks = []
    for k in keys:
        a = ANIMALS[k]
        name = a["en"] if en else a["th"]
        lines = [name]
        if a["chromosomes"]:
            lines.append((f"· chromosomes: {a['chromosomes']} ({a['chromosomes'] // 2} pairs)" if a["chromosomes"] % 2 == 0
                          else f"· chromosomes: {a['chromosomes']} (odd number)") if en else
                         (f"· โครโมโซม {a['chromosomes']} แท่ง ({a['chromosomes'] // 2} คู่)" if a["chromosomes"] % 2 == 0
                          else f"· โครโมโซม {a['chromosomes']} แท่ง (เลขคี่)"))
        else:
            lines.append("· chromosomes: varies by species or population — no single number given" if en
                         else "· โครโมโซม: ต่างกันตามชนิดหรือประชากร — จึงไม่ให้ตัวเลขเดียว")
        if a["genome_gb"]:
            lines.append(f"· genome: about {a['genome_gb']:g} billion base pairs" if en else f"· จีโนมประมาณ {a['genome_gb']:g} พันล้านคู่เบส")
        if a.get("sex") in _SEX:
            lines.append(("· sex: " if en else "· กำหนดเพศ: ") + _SEX[a["sex"]][1 if en else 0])
        lines += ["· " + f for f in (_FACTS_EN.get(k, []) if en else a["facts"])]
        blocks.append("\n".join(lines))
    head = ("Genetics, from the system's animal register (figures are widely accepted values, still awaiting expert verification):"
            if en else "พันธุกรรมจากทะเบียนสัตว์ของระบบ (ตัวเลขเป็นค่าที่ยอมรับทั่วไป ยังรอผู้เชี่ยวชาญตรวจยืนยัน):")
    ask = "Which animal or trait would you like to go deeper on?" if en else "อยากรู้ลึกเรื่องสัตว์ตัวไหนหรือลักษณะไหนเพิ่มอีกไหม?"
    tag = ("\n· Answered from the system's equations — no AI used" if en else "\n· ตอบจากสมการของระบบ — ไม่ได้ใช้ AI") if footer else ""
    return head + "\n\n" + "\n\n".join(blocks) + f"\n\n{ask}\n\n— LYLA ◈" + tag


def llm_hint(text: str) -> str:
    if not _ASK.search(str(text or "")):
        return ""
    keys = animals_in(text)[:3]
    if not keys:
        return ""
    rows = []
    for k in keys:
        a = ANIMALS[k]
        rows.append(f"· {a['th']}: 2n={a['chromosomes'] or 'ต่างตามชนิด'} · {a['sex'] or '-'}" + (" · " + a["facts"][0] if a["facts"] else ""))
    return "[ทะเบียนพันธุกรรมสัตว์ BIO-AXIOM — ใช้เป็นฐาน ถ้าไม่มีตัวเลขให้บอกว่าต่างตามชนิด อย่าเดา]\n" + "\n".join(rows)
