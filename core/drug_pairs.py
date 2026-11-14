"""
core/drug_pairs.py — ยาตีกัน: ยาอะไรกับยาอะไร

เจ้าของโปรเจกต์: "ยาตีกันต้องถามด้วยนะยาอะไรกับยาอะไรจะได้แยกสารถูก"
คนพิมพ์ชื่อยามาหลายแบบ — ชื่อสามัญ ชื่อการค้า ชื่อไทย หรือแค่ "ยาแก้ปวด" — ไฟล์นี้แยกเป็นตัวยาสำคัญ (สาร)
แล้วเทียบกับคู่ที่ตีกันซึ่งพบบ่อยและอันตรายจริง

หลัก:
- รายการนี้ไม่ครบทุกคู่ — ไม่เจอในรายการ ≠ ปลอดภัย จึงบอกให้ถามเภสัชกรเสมอ
- บอกว่าเสี่ยงอะไรและควรทำอะไร ไม่ให้หยุดยาที่แพทย์สั่งเอง
- ยาสูตรผสม (ยาแก้หวัดหลายยี่ห้อมีพาราเซตามอลอยู่แล้ว) แยกสารออกมาให้เห็น เพราะพาราซ้ำซ้อนคือสาเหตุตับวายที่พบบ่อย
"""
from __future__ import annotations

import re

_I = re.I

# สาร → (ชื่อที่แสดง, regex ชื่อที่คนพิมพ์, กลุ่ม)
_SUBS = {
    "warfarin": ("วาร์ฟาริน (ยาละลายลิ่มเลือด)", r"วาร์ฟาริน|วาฟาริน|warfarin|orfarin|coumadin", {"anticoag"}),
    "doac": ("ยาต้านการแข็งตัวของเลือดกลุ่มใหม่", r"rivaroxaban|xarelto|apixaban|eliquis|dabigatran|pradaxa", {"anticoag"}),
    "aspirin": ("แอสไพริน", r"แอสไพริน|แอสไพรีน|aspirin|\basa\b|bayer|แอสเพนท์|aspent", {"nsaid", "antiplatelet"}),
    "clopidogrel": ("โคลพิโดเกรล (ยาต้านเกล็ดเลือด)", r"โคลพิโดเกรล|clopidogrel|plavix|apolets", {"antiplatelet"}),
    "ibuprofen": ("ไอบูโพรเฟน (NSAID)", r"ไอบูโพรเฟน|ไอบูโปรเฟน|ibuprofen|brufen|nurofen|gofen", {"nsaid"}),
    "diclofenac": ("ไดโคลฟีแนค (NSAID)", r"ไดโคลฟีแนค|ไดโคลฟีแน็ค|diclofenac|voltaren|cataflam", {"nsaid"}),
    "naproxen": ("นาพรอกเซน (NSAID)", r"นาพรอกเซน|naproxen|naprosyn", {"nsaid"}),
    "mefenamic": ("กรดเมเฟนามิก (NSAID)", r"เมเฟนามิก|mefenamic|ponstan|พอนสแตน", {"nsaid"}),
    "celecoxib": ("เซเลคอกซิบ (NSAID)", r"เซเลคอกซิบ|celecoxib|celebrex|etoricoxib|arcoxia", {"nsaid"}),
    "paracetamol": ("พาราเซตามอล", r"พาราเซตามอล|พาราเซตตามอล|ยาพารา|พารา(?!กอน|ไดซ์|ชู้ต|ชูต|มิเตอร์)|paracetamol|acetaminophen|tylenol|ไทลินอล|sara\b|ซาร่า|panadol|พานาดอล", {"para"}),
    "para_combo": ("ยาแก้หวัดสูตรผสม (มีพาราเซตามอลอยู่แล้ว)", r"ทิฟฟี่|tiffy|ดีคอลเจน|decolgen|นูต้า|nuta|tylenol cold|panadol cold", {"para"}),
    "nitrate": ("ยาขยายหลอดเลือดหัวใจกลุ่มไนเตรต", r"ไอโซซอร์ไบด์|isosorbide|isordil|ยาอมใต้ลิ้น|nitroglycerin|ไนโตรกลีเซอรีน|\bntg\b", {"nitrate"}),
    "pde5": ("ยาเสริมสมรรถภาพทางเพศ (กลุ่ม PDE5)", r"ไวอากร้า|viagra|sildenafil|ซิลเดนาฟิล|tadalafil|cialis|ทาดาลาฟิล|vardenafil|levitra", {"pde5"}),
    "simvastatin": ("ซิมวาสแตติน (ยาลดไขมัน)", r"ซิมวาสแตติน|ซิมวา|simvastatin|zocor|lovastatin", {"statin_cyp"}),
    "atorvastatin": ("อะทอร์วาสแตติน (ยาลดไขมัน)", r"อะทอร์วา|atorvastatin|lipitor", {"statin"}),
    "macrolide": ("ยาปฏิชีวนะคลาริโทรมัยซิน/อีริโทรมัยซิน", r"คลาริโทรมัยซิน|clarithromycin|klacid|อีริโทรมัยซิน|erythromycin", {"cyp3a_inhib"}),
    "grapefruit": ("เกรปฟรุต", r"เกรปฟรุต|grapefruit", {"cyp3a_inhib"}),
    "acei_arb": ("ยาความดันกลุ่ม ACEI/ARB", r"enalapril|อีนาลาพริล|lisinopril|ramipril|captopril|losartan|โลซาร์แทน|valsartan|irbesartan|telmisartan|candesartan", {"raas"}),
    "spironolactone": ("สไปโรโนแลคโตน (ยาขับปัสสาวะเก็บโพแทสเซียม)", r"สไปโรโนแลคโตน|spironolactone|aldactone", {"k_raise"}),
    "potassium": ("โพแทสเซียมเสริม/เกลือโพแทสเซียม", r"โพแทสเซียม(?:เสริม|คลอไรด์)|potassium chloride|kcl\b|เกลือโลโซเดียม|เกลือลดโซเดียม", {"k_raise"}),
    "diuretic": ("ยาขับปัสสาวะ", r"furosemide|ฟูโรเซไมด์|lasix|hydrochlorothiazide|hctz|ไฮโดรคลอโรไทอะไซด์", {"diuretic"}),
    "benzo": ("ยานอนหลับ/ยาคลายกังวลกลุ่มเบนโซ", r"alprazolam|อัลปราโซแลม|xanax|diazepam|ไดอะซีแพม|valium|lorazepam|ลอราซีแพม|ativan|clonazepam|rivotril|zolpidem|stilnox", {"sedative"}),
    "opioid": ("ยาแก้ปวดกลุ่มโอปิออยด์", r"tramadol|ทรามาดอล|tramol|codeine|โคเดอีน|morphine|มอร์ฟีน|oxycodone", {"sedative", "opioid"}),
    "tramadol": ("ทรามาดอล", r"tramadol|ทรามาดอล|tramol", {"serotonergic"}),
    "ssri": ("ยาต้านเศร้ากลุ่ม SSRI", r"fluoxetine|ฟลูออกซิทีน|prozac|sertraline|เซอร์ทราลีน|zoloft|escitalopram|lexapro|citalopram|paroxetine|fluvoxamine", {"serotonergic"}),
    "alcohol": ("แอลกอฮอล์", r"เหล้า|เบียร์|ไวน์|แอลกอฮอล์|alcohol|beer|wine", {"alcohol", "sedative"}),
    "sulfonylurea": ("ยาเบาหวานกลุ่มซัลโฟนิลยูเรีย", r"glipizide|ไกลพิไซด์|glibenclamide|ไกลเบนคลาไมด์|gliclazide|diamicron|glimepiride|amaryl", {"hypo"}),
    "insulin": ("อินซูลิน", r"อินซูลิน|insulin", {"hypo"}),
    "metformin": ("เมทฟอร์มิน", r"เมทฟอร์มิน|metformin|glucophage", {"metformin"}),
    "levothyroxine": ("ยาไทรอยด์ฮอร์โมน", r"levothyroxine|เลโวไทร็อกซีน|euthyrox|eltroxin|ยาไทรอยด์", {"thyroxine"}),
    "binder": ("แคลเซียม/ธาตุเหล็ก/ยาลดกรด", r"แคลเซียม|calcium|ธาตุเหล็ก|เฟอรัส|ferrous|iron|ยาลดกรด|antacid|alum milk|อะลัมมิลค์|ยาธาตุน้ำขาว|แมกนีเซียม", {"binder"}),
    "quinolone_tetra": ("ยาปฏิชีวนะกลุ่มควิโนโลน/เตตราไซคลิน", r"ciprofloxacin|ไซโปรฟลอกซาซิน|levofloxacin|norfloxacin|ofloxacin|doxycycline|ด็อกซีไซคลิน|tetracycline", {"chelatable"}),
    "methotrexate": ("เมโทเทรกเซต", r"methotrexate|เมโทเทรกเซต", {"mtx"}),
    "herb_bleed": ("สมุนไพร/อาหารเสริมที่เพิ่มการเลือดออก", r"แปะก๊วย|ginkgo|น้ำมันปลา|fish oil|โอเมก้า\s?3|omega\s?3|ขมิ้นชัน|turmeric|กระเทียมเม็ด|โสม|ginseng", {"bleed_herb"}),
}
_RX = {k: re.compile(v[1], _I) for k, v in _SUBS.items()}
_EN_NAME = {"warfarin": "warfarin (blood thinner)", "doac": "newer anticoagulant", "aspirin": "aspirin", "clopidogrel": "clopidogrel (antiplatelet)",
            "ibuprofen": "ibuprofen (NSAID)", "diclofenac": "diclofenac (NSAID)", "naproxen": "naproxen (NSAID)", "mefenamic": "mefenamic acid (NSAID)",
            "celecoxib": "celecoxib (NSAID)", "paracetamol": "paracetamol", "para_combo": "combination cold remedy (already contains paracetamol)",
            "nitrate": "nitrate heart medicine", "pde5": "erectile-dysfunction drug (PDE5)", "simvastatin": "simvastatin", "atorvastatin": "atorvastatin",
            "macrolide": "clarithromycin/erythromycin", "grapefruit": "grapefruit", "acei_arb": "ACE inhibitor/ARB", "spironolactone": "spironolactone",
            "potassium": "potassium supplement/low-sodium salt", "diuretic": "diuretic", "benzo": "benzodiazepine/sleeping pill", "opioid": "opioid painkiller",
            "tramadol": "tramadol", "ssri": "SSRI antidepressant", "alcohol": "alcohol", "sulfonylurea": "sulfonylurea (diabetes)", "insulin": "insulin",
            "metformin": "metformin", "levothyroxine": "thyroid hormone", "binder": "calcium/iron/antacid", "quinolone_tetra": "quinolone/tetracycline antibiotic",
            "methotrexate": "methotrexate", "herb_bleed": "bleeding-risk supplement (ginkgo, fish oil, turmeric…)"}


def _name(k, en=False):
    return _EN_NAME.get(k, _SUBS[k][0]) if en else _SUBS[k][0]

# คู่กลุ่ม → (ระดับ, ข้อความไทย, ข้อความอังกฤษ) · ระดับ "danger" = อันตราย · "caution" = ต้องปรับ/เว้นระยะ
_PAIRS = [
    ({"anticoag"}, {"nsaid"}, "danger", "เลือดออกง่ายมาก โดยเฉพาะในกระเพาะ — ห้ามใช้ร่วมกันเอง ใช้พาราเซตามอลแก้ปวดแทนตามขนาด และบอกแพทย์ที่ให้ยาละลายลิ่มเลือด",
     "major bleeding risk, especially stomach bleeding — don't combine on your own; use paracetamol for pain instead and tell the prescriber"),
    ({"anticoag"}, {"antiplatelet"}, "danger", "เลือดออกง่ายขึ้นมาก — ใช้ร่วมกันได้เฉพาะเมื่อแพทย์สั่งทั้งสองตัวเอง ห้ามซื้อมากินเพิ่ม",
     "much higher bleeding risk — only together if a doctor prescribed both deliberately"),
    ({"anticoag"}, {"bleed_herb"}, "caution", "สมุนไพร/อาหารเสริมนี้เพิ่มโอกาสเลือดออก และบางตัวทำให้ค่า INR แกว่ง — บอกแพทย์ก่อนกิน และสังเกตจ้ำเลือด เลือดออกตามไรฟัน",
     "this supplement can increase bleeding and destabilise INR — tell your doctor before taking it"),
    ({"antiplatelet"}, {"nsaid"}, "caution", "เพิ่มโอกาสเลือดออกในกระเพาะ และ NSAID บางตัวลดฤทธิ์ปกป้องหัวใจของแอสไพริน — ถามแพทย์ก่อนใช้ร่วม",
     "raises stomach bleeding risk, and some NSAIDs blunt aspirin's heart protection — ask before combining"),
    ({"nsaid"}, {"nsaid"}, "danger", "เป็นยากลุ่มเดียวกันสองตัว (NSAID ซ้ำซ้อน) — เพิ่มแผลในกระเพาะและไตวาย ใช้ตัวเดียวพอ",
     "two NSAIDs at once — doubles stomach-ulcer and kidney risk; use only one"),
    ({"para"}, {"para"}, "danger", "มีพาราเซตามอลซ้ำสองแหล่ง — ยาแก้หวัดสูตรผสมหลายยี่ห้อมีพาราอยู่แล้ว กินร่วมกันอาจเกินขนาดจนตับวาย (ผู้ใหญ่ไม่ควรเกิน 4,000 มก./วัน)",
     "paracetamol from two sources — many cold remedies already contain it; together they can exceed the safe dose (adults max 4,000 mg/day) and damage the liver"),
    ({"nitrate"}, {"pde5"}, "danger", "ความดันตกรุนแรงจนหมดสติหรือเสียชีวิตได้ — ห้ามใช้ร่วมกันเด็ดขาด (ทาดาลาฟิลต้องห่างไนเตรตอย่างน้อย 48 ชม. ตัวอื่น 24 ชม.)",
     "severe blood-pressure crash that can be fatal — never combine (48 h gap for tadalafil, 24 h for others)"),
    ({"statin_cyp"}, {"cyp3a_inhib"}, "danger", "ระดับยาลดไขมันในเลือดพุ่งสูง เสี่ยงกล้ามเนื้อสลาย — แพทย์มักให้หยุดซิมวาสแตตินชั่วคราวระหว่างกินยาปฏิชีวนะนี้ และงดเกรปฟรุต",
     "statin levels spike, risking muscle breakdown — doctors usually pause simvastatin during this antibiotic; avoid grapefruit"),
    ({"statin"}, {"cyp3a_inhib"}, "caution", "ระดับยาลดไขมันสูงขึ้นได้ — ถามแพทย์เรื่องลดขนาดชั่วคราว สังเกตอาการปวดกล้ามเนื้อหรือปัสสาวะสีเข้ม",
     "statin levels can rise — ask about a temporary dose change; watch for muscle pain or dark urine"),
    ({"raas"}, {"k_raise"}, "danger", "โพแทสเซียมในเลือดสูงจนหัวใจเต้นผิดจังหวะได้ — ใช้ร่วมกันได้เฉพาะเมื่อแพทย์สั่งและเจาะเลือดติดตาม ห้ามซื้อเกลือโพแทสเซียมหรือโพแทสเซียมเสริมกินเอง",
     "potassium can rise to heart-rhythm-threatening levels — only with a doctor's plan and blood monitoring; no self-bought potassium or low-sodium salt"),
    ({"raas"}, {"nsaid"}, "caution", "NSAID ลดฤทธิ์ยาความดันและทำร้ายไต — ถ้ากินยาขับปัสสาวะด้วย จะเสี่ยงไตวายเฉียบพลันสูงมาก ใช้พาราเซตามอลแทน",
     "NSAIDs weaken blood-pressure medicine and strain the kidneys — with a diuretic as well, acute kidney injury risk is high; use paracetamol instead"),
    ({"diuretic"}, {"nsaid"}, "caution", "ลดฤทธิ์ยาขับปัสสาวะและเพิ่มความเสี่ยงไตวาย — ใช้พาราเซตามอลแทนถ้าทำได้",
     "reduces the diuretic's effect and raises kidney risk — prefer paracetamol"),
    ({"opioid"}, {"sedative"}, "danger", "กดการหายใจ ง่วงหนักจนหยุดหายใจได้ — ห้ามใช้ร่วมกันเองโดยเฉพาะกับแอลกอฮอล์",
     "can suppress breathing to the point of stopping — don't combine on your own, especially with alcohol"),
    ({"sedative"}, {"alcohol"}, "danger", "ง่วงหนัก กดการหายใจ หกล้ม — ห้ามดื่มแอลกอฮอล์ระหว่างใช้ยานี้",
     "heavy sedation, breathing suppression and falls — don't drink while taking this"),
    ({"serotonergic"}, {"serotonergic"}, "caution", "เสี่ยงกลุ่มอาการเซโรโทนินเกิน (กระสับกระส่าย ไข้ เหงื่อ กล้ามเนื้อกระตุก) และชักง่ายขึ้นกับทรามาดอล — ถามแพทย์ก่อนใช้ร่วม",
     "risk of serotonin syndrome (agitation, fever, sweating, twitching) and seizures with tramadol — ask before combining"),
    ({"hypo"}, {"alcohol"}, "caution", "น้ำตาลต่ำได้รุนแรงและนาน โดยเฉพาะดื่มตอนท้องว่าง — ถ้าดื่ม ดื่มน้อยและกินอาหารร่วม",
     "can cause severe, prolonged low blood sugar, especially on an empty stomach — if you drink, keep it small and eat"),
    ({"metformin"}, {"alcohol"}, "caution", "ดื่มหนักร่วมกับเมทฟอร์มินเพิ่มความเสี่ยงภาวะกรดแลคติกคั่ง (พบน้อยแต่รุนแรง) — ดื่มน้อยหรือไม่ดื่ม",
     "heavy drinking with metformin raises the rare but serious risk of lactic acidosis — keep it minimal"),
    ({"thyroxine"}, {"binder"}, "caution", "แคลเซียม เหล็ก หรือยาลดกรดลดการดูดซึมยาไทรอยด์ — กินห่างกันอย่างน้อย 4 ชั่วโมง",
     "calcium, iron or antacids block thyroid-hormone absorption — separate by at least 4 hours"),
    ({"chelatable"}, {"binder"}, "caution", "ยาปฏิชีวนะนี้จับกับแคลเซียม เหล็ก แมกนีเซียม จนดูดซึมไม่ได้ — กินยาปฏิชีวนะก่อน 2 ชม. หรือหลัง 6 ชม. และเลี่ยงนมในช่วงนั้น",
     "this antibiotic binds calcium, iron or magnesium and stops working — take it 2 h before or 6 h after, and avoid milk around it"),
    ({"mtx"}, {"nsaid"}, "danger", "NSAID ทำให้เมโทเทรกเซตคั่งจนเป็นพิษต่อไขกระดูกและไต — ห้ามซื้อยาแก้ปวดกลุ่มนี้กินเอง",
     "NSAIDs can make methotrexate build up to toxic levels — don't self-medicate with them"),
]


def substances(text: str) -> list[str]:
    t = str(text or "")
    out = [k for k, rx in _RX.items() if rx.search(t)]
    if "tramadol" in out and "opioid" not in out:
        out.append("opioid")
    return out


def _groups(k):
    g = set(_SUBS[k][2])
    if k == "tramadol":
        g |= _SUBS["opioid"][2]
    return g


def check(text: str):
    """คืน (สารที่เจอ, รายการคู่ที่ตีกัน [(สาร1, สาร2, ระดับ, ไทย, อังกฤษ)])"""
    subs = substances(text)
    subs = [s for s in subs if not (s == "opioid" and "tramadol" in subs)]
    found, seen = [], set()
    for i, a in enumerate(subs):
        for b in subs[i + 1:]:
            ga, gb = _groups(a), _groups(b)
            for x, y, lvl, th, en in _PAIRS:
                if (ga & x and gb & y) or (ga & y and gb & x):
                    key = (frozenset((a, b)), th)
                    if key not in seen:
                        seen.add(key)
                        found.append((a, b, lvl, th, en))
                    break
    return subs, found


_ASK = re.compile(r"ตีกัน|กินด้วยกัน|กินร่วม|กินพร้อม|ใช้ร่วม|ใช้ด้วยกัน|กินคู่|ได้ไหม|ได้มั้ย|ปลอดภัยไหม|อันตรายไหม|"
                  r"\binteract\w*\b|\btogether\b|\bwith\b|\bsafe\b|\bcombine\b|\bmix\b", _I)


def reply(text: str, lang: str = "th", footer: bool = True):
    """ตอบเมื่อมีชื่อยาตั้งแต่ 2 สาร และเป็นคำถามเรื่องใช้ร่วมกัน — ไม่ใช่ก็ None"""
    subs, pairs = check(text)
    if len(subs) < 2 or not _ASK.search(str(text or "")):
        return None
    en = lang == "en"
    names = " · ".join(_name(s, en) for s in subs)
    if en:
        head = f"Substances I identified: {names}"
    else:
        head = f"ตัวยาที่แยกได้: {names}"
    body = []
    pairs.sort(key=lambda p: 0 if p[2] == "danger" else 1)
    for a, b, lvl, th, eng in pairs:
        mark = "!!" if lvl == "danger" else "!"
        body.append(f"{mark} {_name(a, en)} + {_name(b, en)} — {eng if en else th}")
    if not body:
        body.append("Not in the list of common dangerous pairs I know — but that list isn't complete, so please confirm with a pharmacist."
                    if en else "ไม่อยู่ในรายการคู่ยาอันตรายที่พบบ่อยที่ระบบรู้ — แต่รายการนี้ไม่ครบทุกคู่ ควรให้เภสัชกรยืนยันอีกครั้ง")
    tail = (["Don't stop any medicine a doctor prescribed on your own — ask the prescriber or a pharmacist how to adjust.",
             "Bring every medicine, supplement and herb in one bag to a pharmacist for a full review.",
             "If you've already taken a dangerous pair and feel faint, very drowsy, short of breath or are bleeding — call 1669."] if en else
            ["อย่าหยุดยาที่แพทย์สั่งเอง — ถามแพทย์หรือเภสัชกรว่าควรปรับอย่างไร",
             "นำยา อาหารเสริม และสมุนไพรทั้งหมดใส่ถุงเดียวไปให้เภสัชกรดูทีเดียว",
             "ถ้ากินคู่อันตรายไปแล้วและมีอาการ หน้ามืด ง่วงผิดปกติ หายใจไม่อิ่ม หรือเลือดออก — โทร 1669"])
    ask = ("Are there any other medicines or supplements you take that I should check too?" if en
           else "มียาหรืออาหารเสริมตัวอื่นที่กินอยู่ด้วยไหม จะได้ดูให้ครบ?")
    tag = ("\n· Answered from the system's equations — no AI used" if en else "\n· ตอบจากสมการของระบบ — ไม่ได้ใช้ AI") if footer else ""
    return (head + "\n\n" + "\n".join(body) + "\n\n" + "\n".join(f"{i + 1}) {p}" for i, p in enumerate(tail))
            + f"\n\n{ask}\n\n— LYLA ◈" + tag)


def llm_hint(text: str) -> str:
    subs, pairs = check(text)
    if len(subs) < 2:
        return ""
    rows = [f"· {_SUBS[a][0]} + {_SUBS[b][0]}: {th}" for a, b, _, th, _ in pairs] or ["· ไม่พบคู่อันตรายในรายการที่รู้ (รายการไม่ครบ — ให้แนะนำถามเภสัชกร)"]
    return ("[ตรวจคู่ยาจากรายการที่ระบบรู้ — ตัวยาที่แยกได้: " + ", ".join(_SUBS[s][0] for s in subs)
            + " · ห้ามสั่งหยุดยาที่แพทย์สั่ง]\n" + "\n".join(rows))
