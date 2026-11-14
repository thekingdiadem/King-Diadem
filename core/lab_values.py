"""
core/lab_values.py — อ่านค่าเลือดจากผลตรวจสุขภาพที่ผู้ใช้พิมพ์มา

เจ้าของโปรเจกต์: "เอาให้มันฉลาดแบบว่ารู้ ... ค่าเลือด DNA ได้มะ"
เดิม "ผลตรวจ LDL 190 น้ำตาล 130" ได้คำตอบทั่วไป — คนที่ถือผลตรวจอยู่ในมืออยากรู้ว่าตัวเลขนี้แปลว่าอะไร

หลัก:
- ใช้เกณฑ์ผู้ใหญ่ที่ใช้กันทั่วไป (ADA, NCEP ATP III, KDIGO และค่าอ้างอิงที่ห้องแล็บไทยใช้บ่อย)
  ค่าอ้างอิงจริงต่างกันเล็กน้อยตามห้องแล็บ — ให้ดูช่วงที่พิมพ์ในใบผลด้วยเสมอ
- บอกว่าตัวเลขอยู่ช่วงไหนและแปลว่าอะไร ไม่วินิจฉัยโรค ไม่สั่งยา ไม่บอกให้หยุดยา
- ค่าวิกฤต (โพแทสเซียมสูง/ต่ำมาก เกล็ดเลือดต่ำมาก น้ำตาลต่ำมาก ฯลฯ) → บอกให้พบแพทย์วันนี้ก่อนอย่างอื่น
- อ่านเฉพาะตัวเลขที่เขียนติดกับชื่อค่า ไม่เดา
"""
from __future__ import annotations

import re

_I = re.I
_NUM = r"\s*(?:[:=]|คือ|ได้|อยู่ที่|ประมาณ|ขึ้น|is|was|of|at)?\s*(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)"

# ชื่อค่า → (regex ชื่อ ไทย+อังกฤษ, ชื่อที่แสดง th, en, หน่วย)
_TESTS = {
    "hba1c": (r"hba1c|hb\s?a1c|\ba1c\b|น้ำตาลสะสม", "น้ำตาลสะสม (HbA1c)", "HbA1c", "%"),
    "glucose": (r"\bfbs\b|\bfpg\b|\bdtx\b|(?:fasting )?(?:blood )?(?:glucose|sugar)|น้ำตาล(?:ในเลือด)?(?!สะสม)", "น้ำตาลในเลือด", "blood sugar", "mg/dL"),
    "ldl": (r"\bldl(?:-c)?\b|ไขมันเลว", "ไขมันเลว (LDL)", "LDL", "mg/dL"),
    "hdl": (r"\bhdl(?:-c)?\b|ไขมันดี", "ไขมันดี (HDL)", "HDL", "mg/dL"),
    "tg": (r"\btg\b|triglycerides?|ไตรกลีเซอไรด์", "ไตรกลีเซอไรด์", "triglycerides", "mg/dL"),
    "chol": (r"(?<!ldl )(?<!hdl )(?:total )?cholesterol|คอเลสเตอรอล(?:รวม)?|ไขมันรวม|\btc\b", "คอเลสเตอรอลรวม", "total cholesterol", "mg/dL"),
    "uric": (r"uric(?: acid)?|(?:กรด)?ยูริก", "กรดยูริก", "uric acid", "mg/dL"),
    "egfr": (r"\be?gfr\b", "eGFR (การทำงานของไต)", "eGFR", "mL/min/1.73m²"),
    "cr": (r"creatinine|ครีเอตินีน|ครีเอตินิน|\bcr\b", "ครีเอตินิน", "creatinine", "mg/dL"),
    "alt": (r"\balt\b|\bsgpt\b", "ค่าตับ ALT (SGPT)", "ALT", "U/L"),
    "ast": (r"\bast\b|\bsgot\b", "ค่าตับ AST (SGOT)", "AST", "U/L"),
    "hb": (r"\bhb\b(?!\s?a1c)|\bhgb\b|ha?emoglobin|ฮีโมโกลบิน|ความเข้มข้นเลือด", "ฮีโมโกลบิน", "hemoglobin", "g/dL"),
    "plt": (r"\bplt\b|platelets?|เกล็ดเลือด", "เกล็ดเลือด", "platelets", "/µL"),
    "k": (r"potassium|โพแทสเซียม|โปแตสเซียม|\bk\b", "โพแทสเซียม", "potassium", "mmol/L"),
    "na": (r"sodium|โซเดียม(?:ในเลือด)?|\bna\b", "โซเดียม", "sodium", "mmol/L"),
}
_RX = {k: re.compile(rf"(?:{v[0]}){_NUM}", _I) for k, v in _TESTS.items()}

# ระดับ: "ok" ปกติ · "watch" ควรดูแล/ตรวจซ้ำ · "high" ควรพบแพทย์ · "urgent" พบแพทย์วันนี้
# (ระดับ, คำอธิบายไทย, คำอธิบายอังกฤษ)


def _grade(k: str, v: float):
    if k == "glucose":
        if v < 54: return "urgent", "ต่ำมาก — ถ้ามีใจสั่น เหงื่อออก สับสน ให้กินน้ำหวานทันทีและพบแพทย์", "very low — if shaky, sweaty or confused, take sugar now and see a doctor"
        if v < 70: return "watch", "ต่ำกว่าปกติ", "below normal"
        if v > 400: return "urgent", "สูงมาก — ควรพบแพทย์วันนี้ โดยเฉพาะถ้ากระหายน้ำมาก ปัสสาวะบ่อย อ่อนเพลีย", "very high — see a doctor today, especially with thirst, frequent urination or weakness"
        if v >= 126: return "high", "ถ้าเป็นค่าอดอาหาร อยู่ในเกณฑ์เบาหวาน (ต้องยืนยันด้วยการตรวจซ้ำหรือ HbA1c)", "if fasting, in the diabetes range (needs confirming with a repeat test or HbA1c)"
        if v >= 100: return "watch", "ถ้าเป็นค่าอดอาหาร อยู่ในกลุ่มเสี่ยงเบาหวาน — ยังย้อนกลับได้ด้วยอาหารและการขยับร่างกาย", "if fasting, prediabetes range — still reversible with diet and activity"
        return "ok", "ปกติ (ถ้าเป็นค่าอดอาหาร)", "normal (if fasting)"
    if k == "hba1c":
        if v >= 10: return "high", "สูงมาก — น้ำตาลเฉลี่ยช่วง 3 เดือนสูงจนควรพบแพทย์เร็ว", "very high — average sugar over 3 months is high enough to see a doctor soon"
        if v >= 6.5: return "high", "อยู่ในเกณฑ์เบาหวาน", "in the diabetes range"
        if v >= 5.7: return "watch", "กลุ่มเสี่ยงเบาหวาน — ยังย้อนกลับได้", "prediabetes range — still reversible"
        return "ok", "ปกติ", "normal"
    if k == "ldl":
        if v >= 190: return "high", "สูงมาก — ระดับนี้แพทย์มักพิจารณายาร่วมกับการปรับอาหาร และควรถามเรื่องไขมันสูงทางพันธุกรรมในครอบครัว", "very high — at this level doctors usually consider medication, and it's worth asking about inherited high cholesterol"
        if v >= 160: return "high", "สูง", "high"
        if v >= 130: return "watch", "ค่อนข้างสูง", "borderline high"
        if v >= 100: return "ok", "เกือบดี (ถ้ามีเบาหวานหรือโรคหัวใจ เป้ามักต่ำกว่านี้)", "near optimal (targets are lower with diabetes or heart disease)"
        return "ok", "ดี", "optimal"
    if k == "hdl":
        if v < 40: return "watch", "ต่ำ — HDL ต่ำเพิ่มความเสี่ยงโรคหัวใจ (ผู้หญิงควรเกิน 50) การออกกำลังกายช่วยเพิ่มได้", "low — raises heart risk (women ideally above 50); exercise helps raise it"
        if v < 50: return "ok", "พอใช้ (สำหรับผู้หญิงยังต่ำกว่าที่ควร คือ 50 ขึ้นไป)", "acceptable (for women, ideally 50 or more)"
        if v >= 60: return "ok", "ดีมาก — ช่วยป้องกันหัวใจ", "very good — protective"
        return "ok", "ปกติ", "normal"
    if k == "tg":
        if v >= 500: return "high", "สูงมาก — เสี่ยงตับอ่อนอักเสบ ควรพบแพทย์เร็ว และงดแอลกอฮอล์", "very high — risk of pancreatitis; see a doctor soon and avoid alcohol"
        if v >= 200: return "high", "สูง — มักเกี่ยวกับแป้ง น้ำตาล และแอลกอฮอล์", "high — often linked to refined carbs, sugar and alcohol"
        if v >= 150: return "watch", "ค่อนข้างสูง", "borderline high"
        return "ok", "ปกติ", "normal"
    if k == "chol":
        if v >= 240: return "high", "สูง — ดู LDL ประกอบ เพราะตัวที่ตัดสินความเสี่ยงคือ LDL", "high — look at LDL too, which matters more for risk"
        if v >= 200: return "watch", "ค่อนข้างสูง", "borderline high"
        return "ok", "ปกติ", "normal"
    if k == "uric":
        if v >= 9: return "high", "สูงมาก — เสี่ยงเกาต์และนิ่วในไต", "very high — risk of gout and kidney stones"
        if v > 7: return "watch", "สูงกว่าปกติ (ผู้หญิงเกิน 6 ก็ถือว่าสูง) — ลดเครื่องในสัตว์ เบียร์ น้ำหวาน และดื่มน้ำให้พอ", "above normal (above 6 for women) — cut organ meats, beer and sugary drinks, drink enough water"
        return "ok", "ปกติ (ผู้หญิงควรไม่เกิน 6)", "normal (for women, ideally 6 or less)"
    if k == "egfr":
        if v < 15: return "urgent", "ต่ำมาก — ไตทำงานน้อยมาก ควรพบแพทย์โรคไตโดยเร็วที่สุด", "very low — kidney function is very reduced; see a kidney doctor as soon as possible"
        if v < 30: return "high", "ไตทำงานลดลงมาก (ระยะ 4) — ควรอยู่ในการดูแลของแพทย์โรคไต", "severely reduced (stage 4) — should be under a kidney specialist"
        if v < 60: return "high", "ไตทำงานลดลง (ระยะ 3) — ควรปรึกษาแพทย์เรื่องการชะลอไตเสื่อม และระวังยาแก้ปวดกลุ่ม NSAIDs", "reduced (stage 3) — talk to a doctor about slowing decline, and be careful with NSAID painkillers"
        if v < 90: return "watch", "ลดลงเล็กน้อย — พบบ่อยตามอายุ ดูประกอบกับโปรตีนในปัสสาวะ", "mildly reduced — common with age; check with urine protein"
        return "ok", "ปกติ", "normal"
    if k == "cr":
        if v >= 4: return "high", "สูงมาก — ควรพบแพทย์เร็ว", "very high — see a doctor soon"
        if v > 1.3: return "watch", "สูงกว่าปกติ (ผู้หญิงเกิน 1.1) — ดู eGFR ประกอบ เพราะค่านี้ขึ้นกับอายุ เพศ และกล้ามเนื้อ", "above normal (above 1.1 for women) — check eGFR, which accounts for age, sex and muscle"
        return "ok", "ปกติ", "normal"
    if k in ("alt", "ast"):
        if v >= 1000: return "urgent", "สูงมาก — ตับอาจอักเสบเฉียบพลัน ควรพบแพทย์วันนี้", "very high — possible acute liver injury; see a doctor today"
        if v >= 120: return "high", "สูงเกิน 3 เท่าของปกติ — ควรพบแพทย์หาสาเหตุ (ไวรัสตับ ไขมันพอกตับ ยา แอลกอฮอล์)", "over 3× normal — see a doctor to find the cause (hepatitis, fatty liver, medication, alcohol)"
        if v > 40: return "watch", "สูงเล็กน้อย — พบบ่อยจากไขมันพอกตับ แอลกอฮอล์ ยาหรืออาหารเสริมบางชนิด", "mildly high — often fatty liver, alcohol, or some medicines or supplements"
        return "ok", "ปกติ", "normal"
    if k == "hb":
        if v < 7: return "urgent", "ต่ำมาก — โลหิตจางรุนแรง ควรพบแพทย์วันนี้ โดยเฉพาะถ้าเหนื่อยง่าย ใจสั่น หน้ามืด", "very low — severe anemia; see a doctor today, especially with breathlessness, palpitations or fainting"
        if v < 12: return "high", "ต่ำ — โลหิตจาง ควรหาสาเหตุ (ขาดธาตุเหล็ก ประจำเดือนมาก ธาลัสซีเมีย ฯลฯ)", "low — anemia; worth finding the cause (iron, heavy periods, thalassemia, etc.)"
        if v < 13: return "watch", "ต่ำเล็กน้อยสำหรับผู้ชาย (ผู้หญิงปกติ 12 ขึ้นไป)", "slightly low for men (normal for women from 12)"
        if v > 18: return "high", "สูงกว่าปกติ — ควรพบแพทย์", "above normal — see a doctor"
        return "ok", "ปกติ", "normal"
    if k == "plt":
        if v < 1000:          # เขียนแบบ ×10³ เช่น 20 = 20,000
            v *= 1000
        if v < 20000: return "urgent", "ต่ำมาก — เสี่ยงเลือดออก ควรพบแพทย์วันนี้ (ถ้ามีไข้ร่วม คิดถึงไข้เลือดออก ห้ามกินแอสไพริน/ไอบูโพรเฟน)", "very low — bleeding risk; see a doctor today (with fever, think dengue — no aspirin or ibuprofen)"
        if v < 100000: return "high", "ต่ำ — ควรพบแพทย์ ถ้ามีไข้ร่วมให้นึกถึงไข้เลือดออก และเลี่ยงแอสไพริน/ไอบูโพรเฟน", "low — see a doctor; with fever think dengue, and avoid aspirin/ibuprofen"
        if v < 150000: return "watch", "ต่ำกว่าปกติเล็กน้อย", "slightly low"
        if v > 450000: return "watch", "สูงกว่าปกติ — ควรตรวจซ้ำ", "above normal — worth rechecking"
        return "ok", "ปกติ", "normal"
    if k == "k":
        if v > 20: return None
        if v < 2.5 or v >= 6.0: return "urgent", "อยู่ในระดับวิกฤต — อาจทำให้หัวใจเต้นผิดจังหวะ ควรไปโรงพยาบาลวันนี้", "critical — can disturb heart rhythm; go to hospital today"
        if v < 3.5: return "high", "ต่ำ — ควรพบแพทย์ (พบบ่อยจากยาขับปัสสาวะ ท้องเสีย อาเจียน)", "low — see a doctor (often diuretics, diarrhea, vomiting)"
        if v > 5.0: return "high", "สูง — ควรพบแพทย์ตรวจซ้ำ (บางครั้งสูงหลอกจากการเจาะเลือด)", "high — see a doctor to recheck (sometimes falsely high from the blood draw)"
        return "ok", "ปกติ", "normal"
    if k == "na":
        if v < 100: return None
        if v < 125 or v > 155: return "urgent", "อยู่ในระดับวิกฤต — อาจทำให้สับสน ชัก ควรไปโรงพยาบาลวันนี้", "critical — can cause confusion or seizures; go to hospital today"
        if v < 135: return "high", "ต่ำ — ควรพบแพทย์", "low — see a doctor"
        if v > 145: return "high", "สูง — ควรพบแพทย์", "high — see a doctor"
        return "ok", "ปกติ", "normal"
    return None


# ต้องเป็นเรื่องผลตรวจจริง — "ใส่น้ำตาล 2 ช้อน" ไม่ใช่น้ำตาลในเลือด 2
_CONTEXT = re.compile(r"ผล(?:ตรวจ|เลือด|แล็บ|แลป|lab)|ตรวจ(?:เลือด|สุขภาพ|ร่างกาย)|ค่า(?:เลือด|ตับ|ไต|น้ำตาล|ไขมัน)|เจาะเลือด|ใบผล|หมอบอก|"
                      r"mg/?dl|mmol|lab|blood (?:test|work|result)s?|test results?|check-?up|my (?:levels?|results?)", _I)
_NOT = re.compile(r"ช้อน|กรัม|ถ้วย|สูตร|ทำขนม|ทำอาหาร|ใส่น้ำตาล|tbsp|tsp|cups?|recipe|grams?", _I)


def read(text: str):
    """คืนรายการ [(ชื่อค่า, ตัวเลข, ระดับ, คำอธิบายไทย, คำอธิบายอังกฤษ)] จากข้อความ — ไม่มี = []"""
    t = str(text or "")
    out, used = [], []
    if _NOT.search(t):
        return []
    for k, rx in _RX.items():
        for m in rx.finditer(t):
            if any(a <= m.start() < b for a, b in used):
                continue                       # "HbA1c 6.8" ไม่ถูกอ่านซ้ำเป็น Hb
            try:
                v = float(m.group(1).replace(",", ""))
            except ValueError:
                continue
            if k == "glucose" and v < 30:      # หน่วย mmol/L หรือไม่ใช่ค่าเลือด — ไม่เดา
                continue
            g = _grade(k, v)
            if g:
                out.append((k, v, *g))
                used.append((m.start(), m.end()))
            break
    if len(out) < 2 and not _CONTEXT.search(t):
        return []                              # ค่าเดียวโดยไม่มีบริบทผลตรวจ — ไม่อ่าน
    return out


_ORDER = {"urgent": 0, "high": 1, "watch": 2, "ok": 3}
_MARK = {"urgent": "!!", "high": "!", "watch": "~", "ok": "✓"}


def reply(text: str, lang: str = "th", footer: bool = True):
    vals = read(text)
    if not vals:
        return None
    en = lang == "en"
    vals.sort(key=lambda x: _ORDER[x[2]])
    worst = vals[0][2]
    lines = []
    for k, v, g, th, eng in vals:
        name = _TESTS[k][2 if en else 1]
        num = f"{v:,.0f}" if v >= 1000 else (f"{v:g}")
        lines.append(f"{_MARK[g]} {name} {num} {_TESTS[k][3]} — {eng if en else th}")
    if worst == "urgent":
        head = ("Some of these values are at a level that should be seen by a doctor today — please don't wait for a routine appointment. "
                "If you feel very unwell (chest pain, confusion, fainting, heavy bleeding), call 1669 or go to the emergency department.") if en else \
               ("มีค่าที่อยู่ในระดับที่ควรพบแพทย์วันนี้ — ไม่ควรรอนัดปกติ ถ้ามีอาการหนัก เช่น เจ็บหน้าอก สับสน หน้ามืด เลือดออกมาก โทร 1669 หรือไปห้องฉุกเฉิน")
        paths = (["Go to a hospital or clinic today with this result sheet.",
                  "Bring a list of every medicine and supplement you take.",
                  "Don't start or stop any medicine on your own before seeing the doctor."] if en else
                 ["ไปโรงพยาบาลหรือคลินิกวันนี้ พร้อมใบผลตรวจนี้",
                  "นำรายการยาและอาหารเสริมที่ใช้อยู่ทั้งหมดไปด้วย",
                  "อย่าเริ่มหรือหยุดยาเองก่อนพบแพทย์"])
    elif worst == "high":
        head = ("Here's what each number means. Some are outside the healthy range and are worth discussing with a doctor soon — this is a reading of the numbers, not a diagnosis."
                if en else "นี่คือความหมายของแต่ละค่า — มีบางค่าที่เกินช่วงปกติและควรคุยกับแพทย์เร็วๆ นี้ ที่อ่านให้คือความหมายของตัวเลข ไม่ใช่การวินิจฉัย")
        paths = (["Book a doctor's visit within the next few weeks and bring this sheet — ask what target fits you and whether to recheck.",
                  "Start what helps almost every value: less sugar and refined carbs, less alcohol, 150 minutes a week of brisk activity, enough sleep.",
                  "Ask about family history — some high values (like very high LDL) run in families."] if en else
                 ["นัดพบแพทย์ภายในไม่กี่สัปดาห์ พร้อมใบผลนี้ — ถามว่าเป้าที่เหมาะกับคุณคือเท่าไร และควรตรวจซ้ำเมื่อไร",
                  "เริ่มสิ่งที่ช่วยเกือบทุกค่า: ลดน้ำตาล แป้งขัดขาว และแอลกอฮอล์ ขยับร่างกายแบบเหนื่อยพอประมาณสัปดาห์ละ 150 นาที นอนให้พอ",
                  "ถามคนในครอบครัวว่ามีใครเป็นแบบเดียวกันไหม — บางค่า เช่น LDL สูงมาก ถ่ายทอดทางพันธุกรรมได้"])
    elif worst == "watch":
        head = ("Here's what each number means. Some are borderline — not alarming, but worth acting on and rechecking. This is a reading of the numbers, not a diagnosis."
                if en else "นี่คือความหมายของแต่ละค่า — มีบางค่าที่ก้ำกึ่ง ยังไม่น่าตกใจ แต่ควรดูแลและตรวจซ้ำ ที่อ่านให้คือความหมายของตัวเลข ไม่ใช่การวินิจฉัย")
        paths = (["Small changes often bring borderline values back within 3–6 months: less sugar and alcohol, more movement, enough sleep.",
                  "Recheck in 3–6 months, and mention these values at your next doctor's visit.",
                  "List any medicines, herbs or supplements you take — some affect liver, kidney or sugar values."] if en else
                 ["ค่าที่ก้ำกึ่งมักดึงกลับมาได้ใน 3–6 เดือนด้วยการปรับเล็กๆ: ลดหวาน ลดแอลกอฮอล์ ขยับร่างกายมากขึ้น นอนให้พอ",
                  "ตรวจซ้ำใน 3–6 เดือน และบอกแพทย์เรื่องค่าเหล่านี้ตอนพบครั้งถัดไป",
                  "จดยา สมุนไพร และอาหารเสริมที่ใช้อยู่ — บางอย่างมีผลต่อค่าตับ ไต หรือน้ำตาล"])
    else:
        head = ("Here's what each number means — nothing here is at an alarming level. This is a reading of the numbers, not a diagnosis."
                if en else "นี่คือความหมายของแต่ละค่า — ไม่มีค่าไหนอยู่ในระดับน่าตกใจ ที่อ่านให้คือความหมายของตัวเลข ไม่ใช่การวินิจฉัย")
        paths = (["Keep doing what's working, and recheck at your next annual checkup.",
                  "For borderline values, small changes — less sugar and alcohol, more movement — often bring them back within 3–6 months.",
                  "Compare with the reference range printed on your own result sheet; labs differ slightly."] if en else
                 ["ทำสิ่งที่ทำอยู่ต่อ และตรวจซ้ำตอนตรวจสุขภาพประจำปี",
                  "ค่าที่ก้ำกึ่ง การปรับเล็กๆ เช่น ลดหวาน ลดแอลกอฮอล์ ขยับร่างกายมากขึ้น มักดึงกลับมาได้ใน 3–6 เดือน",
                  "เทียบกับช่วงอ้างอิงที่พิมพ์ในใบผลของคุณด้วย เพราะแต่ละห้องแล็บต่างกันเล็กน้อย"])
    if worst == "urgent":
        ask = "Do you have any symptoms right now, and can you get to a hospital today?" if en else "ตอนนี้มีอาการอะไรร่วมด้วยไหม และไปโรงพยาบาลได้วันนี้หรือเปล่า?"
    else:
        ask = ("Were these taken fasting, and are you on any medicine for them already?" if en
               else "ตรวจตอนอดอาหารมาหรือเปล่า และตอนนี้กินยาเกี่ยวกับค่าเหล่านี้อยู่ไหม?")
    tag = ("\n· Answered from the system's equations — no AI used" if en else "\n· ตอบจากสมการของระบบ — ไม่ได้ใช้ AI") if footer else ""
    return (head + "\n\n" + "\n".join(lines) + "\n\n" + "\n".join(f"{i + 1}) {p}" for i, p in enumerate(paths))
            + f"\n\n{ask}\n\n— LYLA ◈" + tag)


def llm_hint(text: str) -> str:
    """ส่งผลอ่านตัวเลขให้ AI ใช้เป็นฐาน — AI ยังต้องไม่วินิจฉัยและไม่สั่งยา"""
    vals = read(text)
    if not vals:
        return ""
    rows = [f"· {_TESTS[k][1]} {v:g} → {th}" for k, v, g, th, _ in vals]
    urgent = any(g == "urgent" for _, _, g, _, _ in vals)
    return ("[ผลอ่านค่าเลือดจากเกณฑ์มาตรฐานผู้ใหญ่ — ใช้เป็นฐาน ห้ามวินิจฉัยโรคหรือสั่ง/หยุดยา บอกให้เทียบช่วงอ้างอิงในใบผล"
            + (" · มีค่าวิกฤต: บอกให้พบแพทย์วันนี้ก่อนเรื่องอื่น" if urgent else "") + "]\n" + "\n".join(rows))
