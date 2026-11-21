"""ดูแลโรคเรื้อรังระยะแรก — ไต · เบาหวาน · ความดัน · ไขมัน (ไม่ใช้ AI ผลเหมือนเดิมทุกครั้ง)

เจ้าของโปรเจกต์ขอ: คนที่เป็นโรคไตระยะแรก อยากรู้วิธีไม่ให้ถึงขั้นฟอกไต ใช้เวลาเท่าไร กินอะไร
และแต่ละคนไม่เหมือนกัน ทั้งการกิน การนอน การนั่ง การยืน

หลักที่โมดูลนี้ยึด (สำคัญกว่าความยาวของคำตอบ):
  1. โรคไตเรื้อรังส่วนใหญ่ "หายขาด" ไม่ได้ แต่ "ชะลอ" ได้จริง — บอกตรงๆ ไม่สัญญาว่าหาย
  2. ไม่เดาระยะเวลาเป็นตัวเลข — บอกว่าดูจากค่าอะไร และควรตรวจซ้ำบ่อยแค่ไหนแทน
  3. ไม่แนะนำสมุนไพรเพื่อรักษา — เตือนว่าหลายชนิดทำร้ายไต (มะเฟือง กรดอริสโตโลคิก ฯลฯ)
  4. คำนวณจากข้อมูลของคนนั้นจริงๆ ข้อไหนไม่มีข้อมูลก็ถาม ไม่เติมค่าเอง

อ้างอิงหลัก (ตัวเลขทั้งหมดในไฟล์นี้มาจากแนวทางเหล่านี้):
  · eGFR: สมการ CKD-EPI 2021 (ไม่ใช้ตัวแปรเชื้อชาติ) — Inker et al., NEJM 2021
  · ระยะโรคไตและความถี่การตรวจ: KDIGO 2012/2024 CKD guideline (ตาราง G × A)
  · โปรตีน 0.8 ก./กก./วัน ในคนที่ไม่ได้ฟอกไต · โซเดียม < 2 ก./วัน: KDIGO 2024
  · เป้าหมาย HbA1c / ความดัน / LDL: ADA Standards of Care 2024 · ACC/AHA 2017 · KDIGO 2021 BP
"""
from __future__ import annotations

import math
import re

LANGS = ("th", "en", "es", "vi", "zh", "ko", "ja")
_UMOL_PER_MGDL = 88.4                      # ครีเอตินีน: µmol/L ÷ 88.4 = mg/dL


# ═══ 1) การคำนวณ (ไม่มีข้อความ ทดสอบได้ตรงๆ) ═══════════════════════════════════════════

def egfr_ckd_epi_2021(creatinine: float, age: float, sex: str, unit: str = "mg/dL") -> float | None:
    """eGFR (mL/min/1.73m²) จากครีเอตินีนในเลือด — CKD-EPI 2021 ไม่ใช้ตัวแปรเชื้อชาติ

    eGFR = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^-1.200 × 0.9938^อายุ × 1.012 (ถ้าเป็นหญิง)
    κ = 0.7 (หญิง) / 0.9 (ชาย) · α = -0.241 (หญิง) / -0.302 (ชาย)
    ใช้กับผู้ใหญ่ (อายุ 18 ขึ้นไป) เท่านั้น — เด็กใช้สมการอื่น จึงคืน None
    """
    try:
        scr, age = float(creatinine), float(age)
    except (TypeError, ValueError):
        return None
    sex = _sex(sex)
    if sex is None or not (18 <= age <= 120) or not math.isfinite(scr) or scr <= 0:
        return None
    if str(unit or "").lower().replace("μ", "µ") in ("umol/l", "µmol/l", "umol", "µmol"):
        scr = scr / _UMOL_PER_MGDL
    if not (0.1 <= scr <= 25):                 # นอกช่วงนี้น่าจะพิมพ์ผิดหน่วย
        return None
    k, a = (0.7, -0.241) if sex == "f" else (0.9, -0.302)
    r = scr / k
    egfr = 142 * min(r, 1) ** a * max(r, 1) ** -1.200 * 0.9938 ** age * (1.012 if sex == "f" else 1.0)
    return round(egfr, 1)


def _sex(sex) -> str | None:
    s = str(sex or "").strip().lower()
    if s in ("f", "female", "woman", "หญิง", "ผู้หญิง", "mujer", "nữ", "女", "여", "여자", "여성", "女性"):
        return "f"
    if s in ("m", "male", "man", "ชาย", "ผู้ชาย", "hombre", "nam", "男", "남", "남자", "남성", "男性"):
        return "m"
    return None


def gfr_category(egfr: float | None) -> str | None:
    """ระยะ G ตาม KDIGO: G1 ≥90 · G2 60–89 · G3a 45–59 · G3b 30–44 · G4 15–29 · G5 <15"""
    if egfr is None:
        return None
    for limit, cat in ((90, "G1"), (60, "G2"), (45, "G3a"), (30, "G3b"), (15, "G4")):
        if egfr >= limit:
            return cat
    return "G5"


def albuminuria_category(acr_mg_g: float | None) -> str | None:
    """ระยะ A ตาม KDIGO จากอัตราส่วนอัลบูมินต่อครีเอตินีนในปัสสาวะ (UACR, mg/g):
    A1 <30 · A2 30–300 · A3 >300"""
    if acr_mg_g is None:
        return None
    try:
        acr = float(acr_mg_g)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(acr) or acr < 0:
        return None
    return "A1" if acr < 30 else "A2" if acr <= 300 else "A3"


def has_ckd(g: str | None, a: str | None) -> bool | None:
    """เป็นโรคไตเรื้อรังตามนิยาม: eGFR < 60 หรือมีอัลบูมินรั่ว (A2 ขึ้นไป) — ต้องคงอยู่ > 3 เดือน
    ไม่รู้ทั้งสองค่า = ยังบอกไม่ได้ (None)"""
    if g in ("G3a", "G3b", "G4", "G5") or a in ("A2", "A3"):
        return True
    if g in ("G1", "G2") and a == "A1":
        return False
    return None


# ความถี่การตรวจเลือด/ปัสสาวะต่อปี ตามตาราง KDIGO (แถว G × คอลัมน์ A) · 4 หมายถึง "4 ครั้งขึ้นไป"
_MONITOR = {
    "G1": {"A1": 1, "A2": 1, "A3": 2}, "G2": {"A1": 1, "A2": 1, "A3": 2},
    "G3a": {"A1": 1, "A2": 2, "A3": 3}, "G3b": {"A1": 2, "A2": 3, "A3": 3},
    "G4": {"A1": 3, "A2": 3, "A3": 4}, "G5": {"A1": 4, "A2": 4, "A3": 4},
}


def checks_per_year(g: str | None, a: str | None) -> int | None:
    """ควรตรวจค่าไตปีละกี่ครั้ง — ไม่รู้ระยะ A ใช้ค่าที่บ่อยที่สุดของแถวนั้น (ปลอดภัยไว้ก่อน)"""
    if g not in _MONITOR:
        return None
    row = _MONITOR[g]
    return row[a] if a in row else max(row.values())


def risk_level(g: str | None, a: str | None) -> str | None:
    """สีในตาราง KDIGO: green (ความเสี่ยงต่ำ) · yellow · orange · red (สูงมาก)"""
    if g is None:
        return None
    a = a or "A1"
    table = {
        "G1": ("green", "yellow", "orange"), "G2": ("green", "yellow", "orange"),
        "G3a": ("yellow", "orange", "red"), "G3b": ("orange", "red", "red"),
        "G4": ("red", "red", "red"), "G5": ("red", "red", "red"),
    }
    return table[g][("A1", "A2", "A3").index(a)]


def needs_nephrologist(g: str | None, a: str | None, egfr_drop_per_year: float | None = None) -> bool:
    """ควรส่งพบอายุรแพทย์โรคไต: eGFR < 30 · ACR > 300 · eGFR ลดเร็ว (≥ 5 ต่อปี) — KDIGO"""
    if g in ("G4", "G5") or a == "A3":
        return True
    try:
        return egfr_drop_per_year is not None and float(egfr_drop_per_year) >= 5
    except (TypeError, ValueError):
        return False


def bp_status(sys_bp, dia_bp) -> str | None:
    """normal · elevated · high · crisis (≥180/120 — ถ้ามีอาการต้องไปโรงพยาบาลทันที)"""
    try:
        s, d = float(sys_bp), float(dia_bp)
    except (TypeError, ValueError):
        return None
    if not (50 <= s <= 300 and 30 <= d <= 200):
        return None
    if s >= 180 or d >= 120:
        return "crisis"
    if s >= 130 or d >= 80:
        return "high"
    if s >= 120:
        return "elevated"
    return "normal"


def a1c_target(age, frail: bool = False, hypo_history: bool = False) -> float:
    """เป้าหมาย HbA1c (%) — ส่วนใหญ่ < 7 · สูงอายุ/เปราะบาง/เคยน้ำตาลต่ำบ่อย < 8 (ADA)"""
    try:
        old = float(age) >= 75
    except (TypeError, ValueError):
        old = False
    return 8.0 if (old or frail or hypo_history) else 7.0


def ldl_target(diabetes: bool, cvd: bool, ckd: bool | None, age=None) -> int:
    """เป้าหมาย LDL (mg/dL): เคยเป็นโรคหัวใจ/สมองขาดเลือด < 55 · เบาหวานหรือโรคไต < 100
    (บางคนที่เสี่ยงสูงหมออาจตั้ง < 70) · ทั่วไป < 130"""
    if cvd:
        return 55
    if diabetes or ckd:
        return 100
    return 130


def statin_discussion(age, diabetes: bool, ckd: bool | None, cvd: bool, dialysis: bool = False) -> bool:
    """ควรคุยกับหมอเรื่องยาลดไขมันกลุ่มสแตติน — KDIGO lipid: โรคไตอายุ ≥ 50 ปีที่ยังไม่ฟอกไต ·
    ADA: เบาหวานอายุ 40–75 ปี · ทุกคนที่เคยเป็นโรคหัวใจหรือสมองขาดเลือด"""
    try:
        age = float(age)
    except (TypeError, ValueError):
        age = None
    if cvd:
        return True
    if ckd and not dialysis and age is not None and age >= 50:
        return True
    return bool(diabetes and age is not None and 40 <= age <= 75)


# ═══ 2) ตรวจยาและอาหารที่อันตรายต่อไต ══════════════════════════════════════════════

_NSAID = re.compile(r"ibuprofen|brufen|naproxen|diclofenac|voltaren|celecoxib|celebrex|etoricoxib|arcoxia|mefenamic|ponstan|"
                    r"piroxicam|meloxicam|indomethacin|ketorolac|aspirin\s*(?:3\d\d|[5-9]\d\d)|nsaid|"
                    r"ไอบูโพรเฟน|นาพรอกเซน|ไดโคลฟีแนค|ยาแก้อักเสบ|ยาชุด|ยาแก้ปวดข้อ|"
                    r"ibuprofeno|naproxeno|diclofenaco|布洛芬|萘普生|双氯芬酸|이부프로펜|나프록센|イブプロフェン|ロキソニン|loxoprofen", re.I)
_METFORMIN = re.compile(r"metformin|เมทฟอร์มิน|metformina|二甲双胍|메트포르민|メトホルミン", re.I)
_STAR_FRUIT = re.compile(r"star\s*fruit|carambola|มะเฟือง|khế|杨桃|楊桃|스타프루트|スターフルーツ", re.I)
_HERBAL = re.compile(r"herb|สมุนไพร|ยาต้ม|ยาหม้อ|ยาลูกกลอน|ยาจีน|hierbas|thuốc nam|thuốc bắc|中药|中藥|草药|草藥|한약|약초|漢方|煎じ薬", re.I)
_HIGH_K = re.compile(r"banana|orange|durian|coconut water|potato|avocado|กล้วย|ส้ม|ทุเรียน|น้ำมะพร้าว|มันฝรั่ง|อะโวคาโด|ลำไย|"
                     r"plátano|naranja|durián|agua de coco|chuối|cam|sầu riêng|nước dừa|香蕉|橙|榴莲|椰子水|바나나|오렌지|두리안|코코넛|バナナ|オレンジ|ドリアン", re.I)
_DIURETIC_OR_RAS = re.compile(r"furosemide|lasix|hydrochlorothiazide|hctz|spironolactone|enalapril|lisinopril|ramipril|losartan|valsartan|"
                              r"telmisartan|irbesartan|candesartan|ยาขับปัสสาวะ|ยาขับน้ำ|empagliflozin|dapagliflozin|canagliflozin|jardiance|forxiga", re.I)


def medication_warnings(meds, foods, g: str | None, ckd: bool | None) -> list[str]:
    """รหัสคำเตือน (แปลเป็นข้อความทีหลัง) — ไม่สั่งหยุดยาเอง ให้ไปคุยกับหมอ ยกเว้นข้อที่ชัดเจนว่าเลี่ยงได้เอง"""
    meds_t = " ".join(str(m) for m in (meds or []))
    foods_t = " ".join(str(f) for f in (foods or []))
    all_t = meds_t + " " + foods_t
    out = []
    kidney_risk = bool(ckd) or g in ("G3a", "G3b", "G4", "G5")
    if _NSAID.search(meds_t):
        out.append("nsaid")
    if _METFORMIN.search(meds_t) and g in ("G4", "G5"):
        out.append("metformin_stop")
    elif _METFORMIN.search(meds_t) and g == "G3b":
        out.append("metformin_reduce")
    if _STAR_FRUIT.search(all_t) or kidney_risk:
        out.append("star_fruit")                 # คนโรคไตทุกระยะเลี่ยงมะเฟือง — เตือนเสมอเมื่อเป็นโรคไต
    if _HERBAL.search(all_t) or kidney_risk:
        out.append("herbs")
    if _HIGH_K.search(foods_t) and g in ("G4", "G5"):
        out.append("potassium")
    if _DIURETIC_OR_RAS.search(meds_t) or _METFORMIN.search(meds_t):
        out.append("sick_day")
    return list(dict.fromkeys(out))


# ═══ 3) การกิน การนอน การนั่ง การยืน ═══════════════════════════════════════════════

def lifestyle_codes(p: dict, g: str | None, ckd: bool | None) -> list[str]:
    out = []
    try:
        sleep = float(p.get("sleep_hours")) if p.get("sleep_hours") is not None else None
    except (TypeError, ValueError):
        sleep = None
    try:
        sitting = float(p.get("sitting_hours")) if p.get("sitting_hours") is not None else None
    except (TypeError, ValueError):
        sitting = None
    try:
        standing = float(p.get("standing_hours")) if p.get("standing_hours") is not None else None
    except (TypeError, ValueError):
        standing = None
    if sleep is not None and sleep < 7:
        out.append("sleep_short")
    elif sleep is not None and sleep > 9:
        out.append("sleep_long")
    if sitting is not None and sitting >= 6:
        out.append("sitting")
    if standing is not None and standing >= 6:
        out.append("standing")
    out.append("salt")
    if ckd and g not in ("G5",) and not p.get("dialysis"):
        out.append("protein")
    out.append("activity")
    if p.get("smoker"):
        out.append("smoking")
    return out


# ═══ 4) ข้อความ 7 ภาษา ════════════════════════════════════════════════════════════
# ภาษาอื่นที่ยังไม่รองรับ → ใช้ภาษาอังกฤษ และบอกตรงๆ ว่ายังไม่มีภาษานั้น
# (คำแนะนำทางการแพทย์ที่แปลผิดแม้คำเดียวอันตราย จึงไม่เพิ่มภาษาโดยไม่มีคนตรวจ)

T: dict[str, dict[str, str]] = {
    "title": {
        "th": "แผนดูแลไต เบาหวาน ความดัน ไขมัน ของคุณ",
        "en": "Your kidney, diabetes, blood pressure and cholesterol plan",
        "es": "Tu plan para riñón, diabetes, presión y colesterol",
        "vi": "Kế hoạch chăm sóc thận, tiểu đường, huyết áp và mỡ máu của bạn",
        "zh": "您的肾脏、糖尿病、血压和血脂管理计划",
        "ko": "콩팥·당뇨·혈압·콜레스테롤 관리 계획",
        "ja": "腎臓・糖尿病・血圧・コレステロールのケア計画",
    },
    "no_cure": {
        "th": "พูดตรงๆ: โรคไตเรื้อรังส่วนใหญ่รักษาให้หายขาดไม่ได้ แต่ชะลอได้จริง หลายคนคุมได้ดีจนไม่ต้องฟอกไตตลอดชีวิต ถ้าค่าไตเพิ่งแย่ลงเร็วๆ นี้ อาจเป็นไตบาดเจ็บเฉียบพลันที่ฟื้นได้ ต้องให้หมอแยกให้",
        "en": "Honestly: most chronic kidney disease can't be cured, but it can truly be slowed — many people never need dialysis. If your numbers dropped suddenly, it may be acute injury that can recover; your doctor needs to tell the two apart.",
        "es": "Con honestidad: la mayoría de la enfermedad renal crónica no se cura, pero sí se puede frenar — mucha gente nunca necesita diálisis. Si tus valores bajaron de golpe, puede ser una lesión aguda que se recupera; tu médico debe distinguirlo.",
        "vi": "Nói thật: phần lớn bệnh thận mạn không chữa khỏi hẳn, nhưng làm chậm được thật — nhiều người không bao giờ phải chạy thận. Nếu chỉ số mới xấu đi đột ngột, có thể là tổn thương cấp hồi phục được; bác sĩ cần phân biệt.",
        "zh": "实话实说：大多数慢性肾病无法根治，但确实可以延缓——很多人一辈子都不需要透析。如果指标是最近突然变差，可能是可恢复的急性损伤，需要医生判断。",
        "ko": "솔직히 말하면 만성 콩팥병은 대부분 완치되지 않지만 진행은 확실히 늦출 수 있어요. 평생 투석 없이 지내는 분도 많아요. 수치가 최근 갑자기 나빠졌다면 회복 가능한 급성 손상일 수 있으니 의사의 판단이 필요해요.",
        "ja": "正直に言うと、慢性腎臓病の多くは完治しませんが、進行は確かに遅らせられます。一生透析をせずに済む人も多いです。最近急に数値が悪化した場合は回復しうる急性の障害かもしれないので、医師の判断が必要です。",
    },
    "no_timeline": {
        "th": "ใช้เวลาเท่าไร: ไม่มีใครบอกเป็นตัวเลขเดียวได้ ระบบจึงไม่เดา สิ่งที่บอกได้คือดูจากค่า eGFR และไข่ขาวในปัสสาวะทุกครั้งที่ตรวจ ถ้าคงที่หรือดีขึ้นแปลว่าแผนได้ผล",
        "en": "How long it takes: no one can give one number, so this system won't guess. What tells you is your eGFR and urine albumin at each check — stable or better means the plan is working.",
        "es": "Cuánto tiempo: nadie puede dar un solo número, así que no lo adivinamos. Lo que te lo dice es tu eGFR y la albúmina en orina en cada control — estable o mejor significa que el plan funciona.",
        "vi": "Mất bao lâu: không ai nói được một con số, nên hệ thống không đoán. Điều cho biết là eGFR và albumin niệu mỗi lần khám — ổn định hoặc tốt hơn nghĩa là kế hoạch có hiệu quả.",
        "zh": "需要多久：没有人能给出一个确切数字，所以系统不会猜。看每次检查的 eGFR 和尿白蛋白——稳定或变好就说明计划有效。",
        "ko": "얼마나 걸리나: 누구도 숫자 하나로 말할 수 없어서 추측하지 않아요. 검사할 때마다 eGFR과 소변 알부민을 보면 돼요. 유지되거나 좋아지면 계획이 효과가 있는 거예요.",
        "ja": "どのくらいかかるか：一つの数字では誰にも言えないので、推測はしません。毎回の検査の eGFR と尿アルブミンを見てください。横ばいか改善なら計画が効いています。",
    },
    "need_creat": {
        "th": "ยังคำนวณค่าไตไม่ได้: ต้องมีค่าครีเอตินีนในเลือด อายุ และเพศ (ดูได้จากใบผลเลือด)",
        "en": "Can't calculate kidney function yet: need blood creatinine, age and sex (on your lab report).",
        "es": "Aún no se puede calcular la función renal: falta creatinina en sangre, edad y sexo (en tu análisis).",
        "vi": "Chưa tính được chức năng thận: cần creatinin máu, tuổi và giới tính (trên phiếu xét nghiệm).",
        "zh": "暂时无法计算肾功能：需要血肌酐、年龄和性别（见化验单）。",
        "ko": "아직 콩팥 기능을 계산할 수 없어요: 혈중 크레아티닌, 나이, 성별이 필요해요(검사 결과지에 있어요).",
        "ja": "まだ腎機能を計算できません：血清クレアチニン、年齢、性別が必要です（検査結果に記載）。",
    },
    "need_acr": {
        "th": "ถ้ามี ขอค่าไข่ขาวในปัสสาวะ (UACR หน่วย mg/g) ด้วย จะบอกความเสี่ยงได้แม่นขึ้นมาก",
        "en": "If you have it, add urine albumin-to-creatinine ratio (UACR, mg/g) — it makes the risk much clearer.",
        "es": "Si lo tienes, agrega el cociente albúmina/creatinina en orina (UACR, mg/g) — aclara mucho el riesgo.",
        "vi": "Nếu có, thêm tỉ số albumin/creatinin niệu (UACR, mg/g) — sẽ đánh giá nguy cơ rõ hơn nhiều.",
        "zh": "如果有，请补充尿白蛋白/肌酐比（UACR，mg/g），能更准确判断风险。",
        "ko": "있다면 소변 알부민/크레아티닌 비율(UACR, mg/g)도 알려 주세요. 위험도를 훨씬 정확히 볼 수 있어요.",
        "ja": "あれば尿アルブミン/クレアチニン比（UACR、mg/g）も教えてください。リスクがずっと正確にわかります。",
    },
    "egfr": {
        "th": "ค่าการทำงานของไต (eGFR) ประมาณ {egfr} — ระยะ {g}{a}",
        "en": "Estimated kidney function (eGFR) about {egfr} — stage {g}{a}",
        "es": "Función renal estimada (eGFR) cerca de {egfr} — estadio {g}{a}",
        "vi": "Chức năng thận ước tính (eGFR) khoảng {egfr} — giai đoạn {g}{a}",
        "zh": "估算肾功能（eGFR）约 {egfr}——分期 {g}{a}",
        "ko": "추정 콩팥 기능(eGFR) 약 {egfr} — 단계 {g}{a}",
        "ja": "推定腎機能（eGFR）約 {egfr}——ステージ {g}{a}",
    },
    "not_ckd": {
        "th": "จากค่าที่ให้มา ยังไม่เข้าเกณฑ์โรคไตเรื้อรัง (ต้องผิดปกตินานเกิน 3 เดือน) แต่ถ้ามีเบาหวานหรือความดัน ควรตรวจไตปีละครั้ง",
        "en": "From these numbers you don't meet the definition of chronic kidney disease (it must last over 3 months), but with diabetes or high blood pressure check your kidneys yearly.",
        "es": "Con estos valores no cumples la definición de enfermedad renal crónica (debe durar más de 3 meses), pero con diabetes o hipertensión revisa tus riñones cada año.",
        "vi": "Theo các chỉ số này bạn chưa đủ tiêu chuẩn bệnh thận mạn (phải kéo dài trên 3 tháng), nhưng nếu có tiểu đường hoặc huyết áp cao nên kiểm tra thận mỗi năm.",
        "zh": "按这些数值尚未达到慢性肾病标准（需持续超过 3 个月），但如有糖尿病或高血压，应每年查一次肾功能。",
        "ko": "이 수치로는 만성 콩팥병 기준(3개월 이상 지속)에 해당하지 않아요. 다만 당뇨나 고혈압이 있다면 매년 콩팥 검사를 받으세요.",
        "ja": "この数値では慢性腎臓病の基準（3か月以上続くこと）には当たりませんが、糖尿病や高血圧があれば年1回は腎臓を検査してください。",
    },
    "monitor": {
        "th": "ควรตรวจเลือดและปัสสาวะดูค่าไตปีละ {n} ครั้ง",
        "en": "Check blood and urine kidney tests {n} times a year",
        "es": "Revisa análisis de sangre y orina renales {n} veces al año",
        "vi": "Nên xét nghiệm máu và nước tiểu kiểm tra thận {n} lần mỗi năm",
        "zh": "建议每年查血和尿肾功能 {n} 次",
        "ko": "1년에 {n}번 혈액·소변 콩팥 검사를 받으세요",
        "ja": "腎臓の血液・尿検査を年に {n} 回受けてください",
    },
    "monitor_4": {
        "th": "ควรตรวจค่าไตอย่างน้อยปีละ 4 ครั้ง (ทุก 3 เดือนหรือถี่กว่านั้นตามที่หมอนัด)",
        "en": "Check kidney tests at least 4 times a year (every 3 months or as often as your doctor says)",
        "es": "Revisa la función renal al menos 4 veces al año (cada 3 meses o según tu médico)",
        "vi": "Kiểm tra thận ít nhất 4 lần mỗi năm (3 tháng một lần hoặc theo lịch bác sĩ)",
        "zh": "每年至少查 4 次肾功能（每 3 个月或按医生安排）",
        "ko": "콩팥 검사를 1년에 최소 4번(3개월마다 또는 의사 지시에 따라) 받으세요",
        "ja": "腎臓の検査を年4回以上（3か月ごと、または医師の指示どおり）受けてください",
    },
    "refer": {
        "th": "ควรได้พบอายุรแพทย์โรคไตโดยตรง — ขอใบส่งตัวจากหมอที่ดูแลอยู่",
        "en": "You should see a kidney specialist (nephrologist) — ask your doctor for a referral.",
        "es": "Deberías ver a un nefrólogo — pide una derivación a tu médico.",
        "vi": "Bạn nên khám bác sĩ chuyên khoa thận — xin giấy chuyển từ bác sĩ đang điều trị.",
        "zh": "建议看肾内科专科医生——请主治医生开转诊。",
        "ko": "신장내과 전문의 진료가 필요해요. 지금 보는 의사에게 의뢰서를 요청하세요.",
        "ja": "腎臓内科の専門医を受診すべきです。今の主治医に紹介状を頼んでください。",
    },
    "bp_target": {
        "th": "เป้าความดัน: ต่ำกว่า 130/80 (หมอบางคนอาจตั้งตัวบนต่ำกว่า 120 ถ้าทนได้) · ตอนนี้ {bp}",
        "en": "Blood pressure goal: below 130/80 (some doctors aim for top number under 120 if tolerated) · now {bp}",
        "es": "Meta de presión: menos de 130/80 (algunos médicos buscan la alta bajo 120 si se tolera) · ahora {bp}",
        "vi": "Mục tiêu huyết áp: dưới 130/80 (có bác sĩ đặt tâm thu dưới 120 nếu chịu được) · hiện tại {bp}",
        "zh": "血压目标：低于 130/80（部分医生在可耐受时把收缩压控制在 120 以下）· 目前 {bp}",
        "ko": "혈압 목표: 130/80 미만(견딜 수 있으면 수축기 120 미만을 목표로 하는 의사도 있어요) · 현재 {bp}",
        "ja": "血圧の目標：130/80 未満（耐えられれば上を 120 未満にする医師もいます）· 現在 {bp}",
    },
    "bp_crisis": {
        "th": "ความดัน {bp} สูงระดับวิกฤต — ถ้ามีปวดหัวมาก เจ็บหน้าอก หายใจไม่อิ่ม ตามัว หรือแขนขาอ่อนแรง โทร 1669 ทันที ถ้าไม่มีอาการ นั่งพัก 5 นาทีแล้ววัดใหม่ และติดต่อหมอวันนี้",
        "en": "Blood pressure {bp} is at crisis level — with severe headache, chest pain, breathlessness, blurred vision or weakness call emergency services now. Without symptoms, rest 5 minutes, recheck, and contact your doctor today.",
        "es": "Presión {bp} en nivel de crisis — con dolor de cabeza fuerte, dolor de pecho, falta de aire, visión borrosa o debilidad llama a emergencias ya. Sin síntomas, descansa 5 minutos, vuelve a medir y contacta a tu médico hoy.",
        "vi": "Huyết áp {bp} ở mức khủng hoảng — nếu đau đầu dữ dội, đau ngực, khó thở, mờ mắt hoặc yếu tay chân hãy gọi cấp cứu ngay. Không có triệu chứng thì nghỉ 5 phút, đo lại và liên hệ bác sĩ trong hôm nay.",
        "zh": "血压 {bp} 已达危象水平——如有剧烈头痛、胸痛、气短、视物模糊或肢体无力，立即呼叫急救。没有症状就休息 5 分钟再测，并今天联系医生。",
        "ko": "혈압 {bp}은 위기 수준이에요. 심한 두통, 가슴 통증, 숨참, 시야 흐림, 팔다리 힘 빠짐이 있으면 바로 119에 전화하세요. 증상이 없으면 5분 쉬고 다시 재고 오늘 의사에게 연락하세요.",
        "ja": "血圧 {bp} は危険な水準です。激しい頭痛、胸痛、息切れ、目のかすみ、手足の脱力があればすぐ救急に連絡してください。症状がなければ5分休んで測り直し、今日中に医師に連絡を。",
    },
    "a1c_target": {
        "th": "เป้าน้ำตาลสะสม (HbA1c): ต่ำกว่า {t}% · ตอนนี้ {v}%",
        "en": "HbA1c goal: below {t}% · now {v}%",
        "es": "Meta de HbA1c: menos de {t}% · ahora {v}%",
        "vi": "Mục tiêu HbA1c: dưới {t}% · hiện tại {v}%",
        "zh": "糖化血红蛋白（HbA1c）目标：低于 {t}% · 目前 {v}%",
        "ko": "당화혈색소(HbA1c) 목표: {t}% 미만 · 현재 {v}%",
        "ja": "HbA1c の目標：{t}% 未満 · 現在 {v}%",
    },
    "ldl_target": {
        "th": "เป้าไขมันเลว (LDL): ต่ำกว่า {t} mg/dL · ตอนนี้ {v}",
        "en": "LDL cholesterol goal: below {t} mg/dL · now {v}",
        "es": "Meta de colesterol LDL: menos de {t} mg/dL · ahora {v}",
        "vi": "Mục tiêu LDL cholesterol: dưới {t} mg/dL · hiện tại {v}",
        "zh": "低密度脂蛋白（LDL）目标：低于 {t} mg/dL · 目前 {v}",
        "ko": "LDL 콜레스테롤 목표: {t} mg/dL 미만 · 현재 {v}",
        "ja": "LDL コレステロールの目標：{t} mg/dL 未満 · 現在 {v}",
    },
    "statin": {
        "th": "จากอายุและโรคที่มี ควรคุยกับหมอเรื่องยาลดไขมันกลุ่มสแตติน (ลดเส้นเลือดหัวใจตีบในคนโรคไตและเบาหวาน)",
        "en": "Given your age and conditions, ask your doctor about a statin (it lowers heart risk in kidney disease and diabetes).",
        "es": "Por tu edad y condiciones, pregunta a tu médico por una estatina (baja el riesgo cardíaco en enfermedad renal y diabetes).",
        "vi": "Với tuổi và bệnh hiện có, hãy hỏi bác sĩ về thuốc statin (giảm nguy cơ tim mạch ở người bệnh thận và tiểu đường).",
        "zh": "根据您的年龄和病情，建议与医生讨论他汀类降脂药（可降低肾病和糖尿病患者的心血管风险）。",
        "ko": "나이와 질환을 고려하면 스타틴(콜레스테롤 약)에 대해 의사와 상의하세요. 콩팥병·당뇨 환자의 심장 위험을 낮춰요.",
        "ja": "年齢と病気を考えると、スタチン（コレステロールの薬）について医師に相談してください。腎臓病や糖尿病の心臓リスクを下げます。",
    },
    "nsaid": {
        "th": "ยาแก้ปวดกลุ่ม NSAIDs (ไอบูโพรเฟน ไดโคลฟีแนค นาพรอกเซน ยาชุด) ทำร้ายไตโดยตรง — เลี่ยงถ้าเป็นโรคไต ปวดให้ใช้พาราเซตามอลตามขนาด และบอกหมอ",
        "en": "NSAID painkillers (ibuprofen, diclofenac, naproxen) directly harm kidneys — avoid them with kidney disease; use paracetamol at the right dose for pain and tell your doctor.",
        "es": "Los analgésicos AINE (ibuprofeno, diclofenaco, naproxeno) dañan directamente el riñón — evítalos con enfermedad renal; usa paracetamol en dosis correcta y avisa a tu médico.",
        "vi": "Thuốc giảm đau NSAID (ibuprofen, diclofenac, naproxen) hại thận trực tiếp — tránh nếu bị bệnh thận; đau thì dùng paracetamol đúng liều và báo bác sĩ.",
        "zh": "非甾体抗炎止痛药（布洛芬、双氯芬酸、萘普生）直接伤肾——有肾病应避免；止痛用对乙酰氨基酚（按剂量），并告诉医生。",
        "ko": "NSAID 진통제(이부프로펜, 디클로페낙, 나프록센)는 콩팥을 직접 손상시켜요. 콩팥병이 있으면 피하고, 통증엔 정량의 아세트아미노펜을 쓰고 의사에게 알리세요.",
        "ja": "NSAIDs の痛み止め（イブプロフェン、ジクロフェナク、ロキソプロフェン）は腎臓を直接傷めます。腎臓病なら避け、痛みにはアセトアミノフェンを用量通りに使い、医師に伝えてください。",
    },
    "metformin_stop": {
        "th": "eGFR ต่ำกว่า 30 ไม่ควรใช้เมทฟอร์มินต่อ — ติดต่อหมอเพื่อเปลี่ยนยา (อย่าหยุดยาเบาหวานทั้งหมดเอง)",
        "en": "With eGFR under 30, metformin shouldn't be continued — contact your doctor to switch (don't stop all diabetes medicine on your own).",
        "es": "Con eGFR menor de 30 no se debe seguir con metformina — contacta a tu médico para cambiarla (no suspendas todos los medicamentos de diabetes por tu cuenta).",
        "vi": "eGFR dưới 30 không nên tiếp tục metformin — liên hệ bác sĩ để đổi thuốc (đừng tự ngừng hết thuốc tiểu đường).",
        "zh": "eGFR 低于 30 不宜继续用二甲双胍——请联系医生换药（不要自行停掉所有降糖药）。",
        "ko": "eGFR 30 미만이면 메트포르민을 계속 쓰면 안 돼요. 의사와 상의해 약을 바꾸세요(당뇨약을 모두 임의로 끊지는 마세요).",
        "ja": "eGFR 30 未満ではメトホルミンを続けるべきではありません。医師に連絡して変更を（糖尿病の薬を全部自己判断でやめないで）。",
    },
    "metformin_reduce": {
        "th": "eGFR 30–44 มักต้องลดขนาดเมทฟอร์มิน — ถามหมอว่าขนาดที่กินอยู่เหมาะไหม",
        "en": "With eGFR 30–44, metformin usually needs a lower dose — ask your doctor if your dose is right.",
        "es": "Con eGFR 30–44 la metformina suele requerir menos dosis — pregunta a tu médico si tu dosis es adecuada.",
        "vi": "eGFR 30–44 thường cần giảm liều metformin — hỏi bác sĩ liều hiện tại có phù hợp không.",
        "zh": "eGFR 30–44 时二甲双胍通常需要减量——请问医生现在的剂量是否合适。",
        "ko": "eGFR 30–44이면 메트포르민 용량을 줄여야 하는 경우가 많아요. 지금 용량이 맞는지 의사에게 물어보세요.",
        "ja": "eGFR 30–44 ではメトホルミンの減量が必要なことが多いです。今の量で合っているか医師に確認を。",
    },
    "star_fruit": {
        "th": "ห้ามกินมะเฟืองและน้ำมะเฟือง — มีสารพิษต่อสมองที่ไตไม่ดีขับไม่ออก ทำให้สะอึกไม่หยุด สับสน ชักได้",
        "en": "Do not eat star fruit or its juice — it has a nerve toxin weak kidneys can't clear, causing nonstop hiccups, confusion and seizures.",
        "es": "No comas carambola ni su jugo — tiene una toxina nerviosa que el riñón débil no elimina y causa hipo sin parar, confusión y convulsiones.",
        "vi": "Không ăn khế và nước khế — có độc tố thần kinh mà thận yếu không thải được, gây nấc liên tục, lú lẫn, co giật.",
        "zh": "不要吃杨桃或喝杨桃汁——其中的神经毒素肾功能差时排不出，会导致打嗝不止、意识混乱甚至抽搐。",
        "ko": "스타프루트와 그 주스는 먹지 마세요. 약해진 콩팥이 배출하지 못하는 신경 독소가 있어 멈추지 않는 딸꾹질, 혼미, 경련을 일으켜요.",
        "ja": "スターフルーツとそのジュースは食べないでください。弱った腎臓では排出できない神経毒があり、しゃっくりが止まらない、混乱、けいれんを起こします。",
    },
    "herbs": {
        "th": "ไม่มีสมุนไพรตัวไหนพิสูจน์แล้วว่ารักษาโรคไตให้หายได้ บางชนิด (เช่น ที่มีกรดอริสโตโลคิก ยาต้ม ยาลูกกลอนที่ไม่รู้ส่วนผสม) ทำไตวายได้ — ปรึกษาหมอไตก่อนกินอะไรทุกครั้ง",
        "en": "No herb has been proven to cure kidney disease, and some (aristolochic acid, unlabeled decoctions or pills) cause kidney failure — ask your kidney doctor before taking anything.",
        "es": "Ninguna hierba ha demostrado curar la enfermedad renal y algunas (ácido aristolóquico, cocimientos o píldoras sin etiqueta) causan falla renal — consulta a tu nefrólogo antes de tomar cualquier cosa.",
        "vi": "Chưa có loại thảo dược nào được chứng minh chữa khỏi bệnh thận, một số (acid aristolochic, thuốc nam, thuốc viên không rõ thành phần) còn gây suy thận — hỏi bác sĩ thận trước khi uống bất cứ thứ gì.",
        "zh": "没有任何草药被证实能治愈肾病，有些（含马兜铃酸的、成分不明的汤药或丸药）还会导致肾衰竭——服用任何东西前先问肾科医生。",
        "ko": "콩팥병을 낫게 한다고 증명된 약초는 없고, 일부(아리스톨로크산, 성분을 모르는 달인 약·환약)는 콩팥을 망가뜨려요. 무엇이든 먹기 전에 신장내과 의사와 상의하세요.",
        "ja": "腎臓病を治すと証明された生薬はなく、一部（アリストロキア酸、成分不明の煎じ薬や丸薬）は腎不全を起こします。何か飲む前に必ず腎臓の医師に相談を。",
    },
    "potassium": {
        "th": "ไตระยะนี้ขับโพแทสเซียมได้น้อย — จำกัดกล้วย ส้ม ทุเรียน น้ำมะพร้าว มันฝรั่ง ตามที่หมอหรือนักกำหนดอาหารแนะนำ ถ้าใจสั่นหรืออ่อนแรงให้ไปโรงพยาบาล",
        "en": "At this stage kidneys clear little potassium — limit bananas, oranges, durian, coconut water and potatoes as your doctor or dietitian advises; palpitations or weakness need the hospital.",
        "es": "En esta etapa el riñón elimina poco potasio — limita plátano, naranja, durián, agua de coco y papa según tu médico o nutricionista; palpitaciones o debilidad requieren hospital.",
        "vi": "Ở giai đoạn này thận thải kali kém — hạn chế chuối, cam, sầu riêng, nước dừa, khoai tây theo hướng dẫn của bác sĩ hoặc chuyên gia dinh dưỡng; hồi hộp hoặc yếu người thì đến bệnh viện.",
        "zh": "此阶段肾脏排钾能力差——按医生或营养师建议限制香蕉、橙子、榴莲、椰子水、土豆；出现心慌或无力要去医院。",
        "ko": "이 단계에선 콩팥이 칼륨을 잘 못 내보내요. 의사나 영양사 지시대로 바나나, 오렌지, 두리안, 코코넛 워터, 감자를 제한하고 두근거림이나 힘 빠짐이 있으면 병원에 가세요.",
        "ja": "この段階では腎臓がカリウムをあまり出せません。医師や管理栄養士の指示でバナナ、オレンジ、ドリアン、ココナッツウォーター、じゃがいもを控え、動悸や脱力があれば病院へ。",
    },
    "sick_day": {
        "th": "กฎวันป่วย: ถ้าอาเจียน ท้องเสีย หรือกินน้ำไม่ได้ ให้ติดต่อหมอเรื่องหยุดยาขับปัสสาวะ ยาความดันบางกลุ่ม และเมทฟอร์มินชั่วคราว — ช่วงขาดน้ำยาเหล่านี้ทำไตแย่ลงเร็ว",
        "en": "Sick-day rule: if you're vomiting, have diarrhea or can't drink, contact your doctor about pausing diuretics, some blood pressure pills and metformin — when dehydrated these can hurt kidneys fast.",
        "es": "Regla de días de enfermedad: si vomitas, tienes diarrea o no puedes beber, consulta a tu médico sobre pausar diuréticos, algunos antihipertensivos y metformina — con deshidratación pueden dañar el riñón rápido.",
        "vi": "Quy tắc ngày ốm: nếu nôn, tiêu chảy hoặc không uống được, liên hệ bác sĩ về việc tạm ngừng thuốc lợi tiểu, một số thuốc huyết áp và metformin — khi mất nước các thuốc này làm thận xấu nhanh.",
        "zh": "生病日规则：如果呕吐、腹泻或喝不下水，联系医生是否暂停利尿药、部分降压药和二甲双胍——脱水时这些药会让肾脏迅速变差。",
        "ko": "아픈 날 규칙: 토하거나 설사하거나 물을 못 마시면 이뇨제, 일부 혈압약, 메트포르민을 잠시 멈출지 의사와 상의하세요. 탈수 상태에선 이 약들이 콩팥을 빨리 나빠지게 해요.",
        "ja": "シックデイ・ルール：吐く、下痢、水が飲めないときは、利尿剤、一部の降圧剤、メトホルミンを一時休むか医師に相談を。脱水時はこれらが腎臓を急速に悪化させます。",
    },
    "sleep_short": {
        "th": "นอน {h} ชั่วโมงน้อยไป — การนอนน้อยต่อเนื่องทำให้ความดันและน้ำตาลคุมยาก ลองให้ได้ 7–9 ชั่วโมง ถ้านอนกรนหยุดหายใจให้ปรึกษาหมอ",
        "en": "{h} hours of sleep is short — ongoing short sleep makes blood pressure and sugar harder to control. Aim for 7–9 hours; snoring with pauses in breathing needs a doctor.",
        "es": "Dormir {h} horas es poco — dormir poco de forma continua dificulta controlar presión y azúcar. Busca 7–9 horas; si roncas con pausas respiratorias consulta al médico.",
        "vi": "Ngủ {h} giờ là ít — thiếu ngủ kéo dài khiến huyết áp và đường huyết khó kiểm soát. Cố ngủ 7–9 giờ; ngáy kèm ngưng thở cần đi khám.",
        "zh": "睡 {h} 小时偏少——长期睡眠不足会让血压和血糖更难控制。争取 7–9 小时；打鼾伴呼吸暂停需就医。",
        "ko": "{h}시간 수면은 부족해요. 수면 부족이 계속되면 혈압과 혈당 조절이 어려워져요. 7–9시간을 목표로 하고, 코골이와 호흡 멈춤이 있으면 진료를 받으세요.",
        "ja": "睡眠 {h} 時間は短いです。睡眠不足が続くと血圧や血糖が管理しにくくなります。7〜9時間を目標に。いびきと呼吸停止があれば受診を。",
    },
    "sleep_long": {
        "th": "นอน {h} ชั่วโมงต่อวันนานกว่าปกติ ถ้าเหนื่อยเพลียทั้งที่นอนเยอะ อาจเป็นจากโลหิตจางหรือของเสียคั่งจากไต ควรบอกหมอ",
        "en": "{h} hours a day is more sleep than usual — if you're still exhausted, anemia or kidney waste build-up are possible; tell your doctor.",
        "es": "{h} horas al día es más de lo habitual — si aun así estás agotado, puede ser anemia o acumulación de desechos por el riñón; díselo a tu médico.",
        "vi": "Ngủ {h} giờ mỗi ngày là nhiều hơn bình thường — nếu vẫn mệt, có thể do thiếu máu hoặc ứ chất thải do thận; hãy báo bác sĩ.",
        "zh": "每天睡 {h} 小时比一般多——如果仍然疲惫，可能是贫血或肾功能导致毒素蓄积，请告诉医生。",
        "ko": "하루 {h}시간은 보통보다 많이 자는 편이에요. 그래도 피곤하다면 빈혈이나 콩팥 노폐물 축적일 수 있으니 의사에게 알리세요.",
        "ja": "1日 {h} 時間は通常より長い睡眠です。それでも疲れているなら貧血や腎臓の老廃物の蓄積の可能性があるので医師に伝えてください。",
    },
    "sitting": {
        "th": "นั่งวันละ {h} ชั่วโมง — ลุกเดินหรือยืดเส้น 2–5 นาทีทุก 30–60 นาที ช่วยเรื่องน้ำตาลและความดันได้จริง และดื่มน้ำตามที่หมอแนะนำ (คนโรคไตบางระยะต้องจำกัดน้ำ)",
        "en": "Sitting {h} hours a day — stand, walk or stretch 2–5 minutes every 30–60 minutes; it genuinely helps sugar and blood pressure. Drink as your doctor advises (some kidney stages need fluid limits).",
        "es": "Sentado {h} horas al día — levántate, camina o estírate 2–5 minutos cada 30–60 minutos; de verdad ayuda al azúcar y la presión. Bebe según tu médico (algunas etapas renales limitan líquidos).",
        "vi": "Ngồi {h} giờ mỗi ngày — cứ 30–60 phút đứng dậy đi lại hoặc giãn cơ 2–5 phút, thực sự giúp đường huyết và huyết áp. Uống nước theo hướng dẫn bác sĩ (một số giai đoạn bệnh thận phải hạn chế nước).",
        "zh": "每天坐 {h} 小时——每 30–60 分钟起身走动或拉伸 2–5 分钟，对血糖和血压确实有帮助。按医生建议饮水（部分肾病阶段需限水）。",
        "ko": "하루 {h}시간 앉아 있어요. 30–60분마다 2–5분 일어나 걷거나 스트레칭하면 혈당과 혈압에 실제로 도움이 돼요. 물은 의사 지시대로 마시세요(콩팥병 일부 단계는 수분 제한이 필요해요).",
        "ja": "1日 {h} 時間座っています。30〜60分ごとに2〜5分立って歩くかストレッチすると血糖と血圧に本当に効きます。水分は医師の指示どおりに（腎臓病の段階によっては制限が必要）。",
    },
    "standing": {
        "th": "ยืนวันละ {h} ชั่วโมง — ขยับข้อเท้าและเดินเป็นระยะ ถ้าขาบวมมากขึ้นทุกวัน หรือบวมแล้วหายใจเหนื่อย ต้องบอกหมอ เพราะอาจเป็นน้ำเกินจากไตหรือหัวใจ",
        "en": "Standing {h} hours a day — move your ankles and walk at intervals. Legs swelling more each day, or swelling with breathlessness, must be reported: it can be fluid overload from kidneys or heart.",
        "es": "De pie {h} horas al día — mueve los tobillos y camina a ratos. Si las piernas se hinchan más cada día, o con falta de aire, avisa al médico: puede ser exceso de líquido por riñón o corazón.",
        "vi": "Đứng {h} giờ mỗi ngày — cử động cổ chân và đi lại định kỳ. Chân phù tăng dần mỗi ngày, hoặc phù kèm khó thở, phải báo bác sĩ: có thể là ứ dịch do thận hoặc tim.",
        "zh": "每天站 {h} 小时——定时活动脚踝、走一走。腿肿一天比一天重，或水肿伴气短，一定要告诉医生：可能是肾或心脏导致的液体潴留。",
        "ko": "하루 {h}시간 서 있어요. 발목을 움직이고 틈틈이 걸으세요. 다리 부기가 날마다 심해지거나 붓고 숨이 차면 꼭 의사에게 알리세요. 콩팥이나 심장 때문에 수분이 쌓인 것일 수 있어요.",
        "ja": "1日 {h} 時間立っています。足首を動かし、ときどき歩いてください。足のむくみが日ごとに増える、またはむくみと息切れがあるなら必ず医師に。腎臓や心臓による水分過多の可能性があります。",
    },
    "salt": {
        "th": "ลดเค็ม: โซเดียมไม่เกิน 2,000 มก./วัน (เกลือราว 1 ช้อนชา รวมทุกอย่าง) ระวังน้ำปลา ซีอิ๊ว ผงชูรส บะหมี่กึ่งสำเร็จรูป อาหารแปรรูป — ช่วยทั้งความดันและไต",
        "en": "Cut salt: sodium under 2,000 mg a day (about 1 teaspoon of salt in total). Watch fish sauce, soy sauce, instant noodles and processed food — it helps both blood pressure and kidneys.",
        "es": "Menos sal: sodio bajo 2.000 mg al día (alrededor de 1 cucharadita de sal en total). Cuidado con salsas, fideos instantáneos y procesados — ayuda a la presión y al riñón.",
        "vi": "Giảm muối: natri dưới 2.000 mg/ngày (khoảng 1 thìa cà phê muối tổng cộng). Cẩn thận nước mắm, xì dầu, mì gói, thực phẩm chế biến — tốt cho cả huyết áp và thận.",
        "zh": "少盐：每天钠不超过 2000 毫克（总计约 1 茶匙盐）。注意鱼露、酱油、方便面和加工食品——对血压和肾脏都有好处。",
        "ko": "싱겁게: 나트륨 하루 2,000mg 미만(소금 총 1티스푼 정도). 액젓, 간장, 라면, 가공식품을 조심하세요. 혈압과 콩팥 모두에 도움이 돼요.",
        "ja": "減塩：ナトリウム1日2,000mg未満（食塩で合計小さじ1程度）。魚醤、しょうゆ、インスタント麺、加工食品に注意。血圧にも腎臓にも効きます。",
    },
    "protein": {
        "th": "โปรตีนพอดี ไม่ต้องอดและไม่ต้องเพิ่ม: ราว 0.8 กรัมต่อน้ำหนักตัว 1 กก. ต่อวัน{w} — เลี่ยงอาหารเสริมโปรตีนสูงหรือสูตรลดน้ำหนักโปรตีนสูง",
        "en": "Protein in moderation, neither cutting nor loading: about 0.8 g per kg of body weight a day{w} — avoid high-protein supplements or diets.",
        "es": "Proteína moderada, ni recortar ni cargar: cerca de 0,8 g por kg de peso al día{w} — evita suplementos o dietas altas en proteína.",
        "vi": "Đạm vừa đủ, không cắt cũng không tăng: khoảng 0,8 g mỗi kg cân nặng mỗi ngày{w} — tránh thực phẩm bổ sung hoặc chế độ ăn nhiều đạm.",
        "zh": "蛋白质适量，不必节食也不要加量：每天约每公斤体重 0.8 克{w}——避免高蛋白补充剂或高蛋白减肥餐。",
        "ko": "단백질은 적당히, 줄이지도 늘리지도 말고 하루 체중 1kg당 약 0.8g{w} — 고단백 보충제나 고단백 다이어트는 피하세요.",
        "ja": "たんぱく質は適量で、減らしすぎも増やしすぎもせず1日体重1kgあたり約0.8g{w}。高たんぱくのサプリや食事法は避けて。",
    },
    "protein_w": {
        "th": " (ของคุณราว {g} กรัม)", "en": " (about {g} g for you)", "es": " (unos {g} g para ti)", "vi": " (khoảng {g} g với bạn)",
        "zh": "（您约 {g} 克）", "ko": " (약 {g}g)", "ja": "（あなたは約 {g}g）",
    },
    "activity": {
        "th": "ขยับร่างกายระดับปานกลาง (เดินเร็ว ปั่นจักรยาน) รวมสัปดาห์ละ 150 นาที ถ้ายังไม่ไหวเริ่มจากวันละ 10 นาทีก็ได้",
        "en": "Moderate activity (brisk walking, cycling) adding up to 150 minutes a week; if that's too much, start with 10 minutes a day.",
        "es": "Actividad moderada (caminar rápido, bicicleta) hasta sumar 150 minutos a la semana; si es mucho, empieza con 10 minutos al día.",
        "vi": "Vận động vừa phải (đi bộ nhanh, đạp xe) tổng 150 phút mỗi tuần; nếu chưa nổi thì bắt đầu 10 phút mỗi ngày.",
        "zh": "中等强度活动（快走、骑车）每周累计 150 分钟；做不到就从每天 10 分钟开始。",
        "ko": "빠르게 걷기, 자전거 같은 중간 강도 활동을 주 150분 하세요. 힘들면 하루 10분부터 시작해도 돼요.",
        "ja": "早歩きや自転車などの中等度の運動を週合計150分。きつければ1日10分から始めて構いません。",
    },
    "smoking": {
        "th": "การเลิกบุหรี่ช่วยชะลอไตเสื่อมและลดหัวใจวายได้มาก — ปรึกษาสายเลิกบุหรี่ 1600 ได้ฟรี",
        "en": "Quitting smoking slows kidney decline and greatly lowers heart attack risk — a quitline can help for free.",
        "es": "Dejar de fumar frena el daño renal y baja mucho el riesgo de infarto — una línea para dejar de fumar ayuda gratis.",
        "vi": "Bỏ thuốc lá làm chậm suy thận và giảm mạnh nguy cơ nhồi máu cơ tim — đường dây cai thuốc hỗ trợ miễn phí.",
        "zh": "戒烟能延缓肾功能下降并大幅降低心梗风险——戒烟热线可免费提供帮助。",
        "ko": "금연은 콩팥 기능 저하를 늦추고 심근경색 위험을 크게 낮춰요. 금연상담전화(1544-9030)에서 무료로 도와줘요.",
        "ja": "禁煙は腎機能の低下を遅らせ、心筋梗塞のリスクを大きく下げます。禁煙外来や相談窓口を活用してください。",
    },
    "red_flags": {
        "th": "ไปโรงพยาบาลทันทีถ้ามี: ฉี่ไม่ออกหรือน้อยมาก · บวมแล้วนอนราบไม่ได้ · เจ็บหน้าอก · ใจสั่นแขนขาอ่อนแรง · สับสนหรือชัก · ความดัน 180/120 ขึ้นไปพร้อมอาการ · น้ำตาลต่ำจนเหงื่อแตกตัวสั่น — โทร 1669",
        "en": "Go to hospital now if: little or no urine · swelling and can't lie flat · chest pain · palpitations with weakness · confusion or seizure · blood pressure 180/120+ with symptoms · low sugar with sweating and shaking.",
        "es": "Ve al hospital ya si: poca o nada de orina · hinchazón y no puedes acostarte · dolor de pecho · palpitaciones con debilidad · confusión o convulsión · presión 180/120 o más con síntomas · azúcar baja con sudor y temblor.",
        "vi": "Đến bệnh viện ngay nếu: tiểu rất ít hoặc không tiểu · phù và không nằm được · đau ngực · hồi hộp kèm yếu tay chân · lú lẫn hoặc co giật · huyết áp từ 180/120 kèm triệu chứng · hạ đường huyết vã mồ hôi run rẩy.",
        "zh": "出现以下情况立即去医院：尿很少或没尿 · 水肿且无法平躺 · 胸痛 · 心慌伴无力 · 意识混乱或抽搐 · 血压 180/120 以上伴症状 · 低血糖出冷汗发抖。",
        "ko": "다음이면 바로 병원에 가세요: 소변이 거의 없음 · 붓고 누울 수 없음 · 가슴 통증 · 두근거림과 힘 빠짐 · 혼미하거나 경련 · 혈압 180/120 이상과 증상 · 식은땀과 떨림이 있는 저혈당. 119에 전화하세요.",
        "ja": "次の場合はすぐ病院へ：尿がほとんど出ない · むくみで横になれない · 胸の痛み · 動悸と脱力 · 混乱やけいれん · 血圧180/120以上で症状あり · 冷や汗と震えのある低血糖。119番へ。",
    },
    "disclaimer": {
        "th": "ข้อมูลนี้ช่วยให้เข้าใจและเตรียมคุยกับหมอ ไม่ใช่การวินิจฉัย อย่าหยุดหรือเปลี่ยนยาเองโดยไม่ปรึกษาหมอ",
        "en": "This helps you understand and prepare to talk with your doctor; it isn't a diagnosis. Don't stop or change medicines without your doctor.",
        "es": "Esto te ayuda a entender y preparar la consulta; no es un diagnóstico. No suspendas ni cambies medicamentos sin tu médico.",
        "vi": "Thông tin này giúp bạn hiểu và chuẩn bị trao đổi với bác sĩ, không phải chẩn đoán. Đừng tự ngừng hay đổi thuốc khi chưa hỏi bác sĩ.",
        "zh": "本内容帮助您理解并准备与医生沟通，不是诊断。不要未经医生同意自行停药或换药。",
        "ko": "이 내용은 이해를 돕고 진료를 준비하기 위한 것이며 진단이 아니에요. 의사와 상의 없이 약을 끊거나 바꾸지 마세요.",
        "ja": "これは理解と受診の準備のための情報で、診断ではありません。医師に相談せずに薬をやめたり変えたりしないでください。",
    },
    "lang_fallback": {
        "en": "This guide isn't available in your language yet, so it's shown in English. Medical advice needs careful translation; we'd rather say so than guess.",
    },
}


def _t(key: str, lang: str, **kw) -> str:
    row = T[key]
    s = row.get(lang) or row["en"]
    return s.format(**kw) if kw else s


def _num(v, lo: float, hi: float):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) and lo <= x <= hi else None


def _fmt(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:.1f}"


# ═══ 5) รวมเป็นแผนของแต่ละคน ═════════════════════════════════════════════════════════

def plan(profile: dict | None, lang: str = "th") -> dict:
    """ข้อมูลของคนนั้น → แผนดูแล (ข้อมูลเป็นโครงสร้าง + ข้อความภาษาที่เลือก)

    profile (ทุกช่องไม่บังคับ — ไม่มีก็ถามแทนการเดา):
      creatinine, creatinine_unit ("mg/dL" | "umol/L"), age, sex, uacr (mg/g), egfr_drop_per_year,
      sys_bp, dia_bp, hba1c, ldl, weight_kg, diabetes, cvd, dialysis, frail, hypo_history, smoker,
      meds [..], foods [..], sleep_hours, sitting_hours, standing_hours
    """
    p = profile if isinstance(profile, dict) else {}
    lang_in = str(lang or "th").lower()[:2]
    supported = lang_in in LANGS
    lang = lang_in if supported else "en"

    egfr = p.get("egfr")
    egfr = _num(egfr, 1, 200)
    if egfr is None:
        egfr = egfr_ckd_epi_2021(p.get("creatinine"), p.get("age"), p.get("sex"), p.get("creatinine_unit") or "mg/dL")
    g = gfr_category(egfr)
    a = albuminuria_category(_num(p.get("uacr"), 0, 100000))
    ckd = has_ckd(g, a)
    dialysis = bool(p.get("dialysis"))
    diabetes = bool(p.get("diabetes"))
    cvd = bool(p.get("cvd"))

    lines: list[str] = []
    ask: list[str] = []
    if g is None:
        ask.append(_t("need_creat", lang))
    if a is None:
        ask.append(_t("need_acr", lang))

    stage = None
    if g is not None:
        stage = {"egfr": egfr, "g": g, "a": a, "ckd": ckd, "risk": risk_level(g, a)}
        lines.append(_t("egfr", lang, egfr=_fmt(egfr), g=g, a=a or ""))
        if ckd is False:
            lines.append(_t("not_ckd", lang))
        n = checks_per_year(g, a)
        if ckd is not False and n:
            lines.append(_t("monitor_4", lang) if n >= 4 else _t("monitor", lang, n=n))
        if needs_nephrologist(g, a, p.get("egfr_drop_per_year")):
            lines.append(_t("refer", lang))
    if ckd is not False:
        lines.append(_t("no_cure", lang))
        lines.append(_t("no_timeline", lang))

    targets = {}
    sys_bp, dia_bp = _num(p.get("sys_bp"), 50, 300), _num(p.get("dia_bp"), 30, 200)
    bp = bp_status(sys_bp, dia_bp)
    if bp:
        targets["bp"] = {"now": [sys_bp, dia_bp], "status": bp, "goal": [130, 80]}
        bp_txt = f"{_fmt(sys_bp)}/{_fmt(dia_bp)}"
        lines.append(_t("bp_crisis", lang, bp=bp_txt) if bp == "crisis" else _t("bp_target", lang, bp=bp_txt))
    a1c = _num(p.get("hba1c"), 3, 20)
    if diabetes or a1c is not None:
        goal = a1c_target(p.get("age"), bool(p.get("frail")), bool(p.get("hypo_history")))
        targets["hba1c"] = {"now": a1c, "goal": goal}
        lines.append(_t("a1c_target", lang, t=_fmt(goal), v=_fmt(a1c) if a1c is not None else "?"))
    ldl = _num(p.get("ldl"), 10, 600)
    goal_ldl = ldl_target(diabetes, cvd, ckd, p.get("age"))
    if ldl is not None or diabetes or cvd or ckd:
        targets["ldl"] = {"now": ldl, "goal": goal_ldl}
        lines.append(_t("ldl_target", lang, t=goal_ldl, v=_fmt(ldl) if ldl is not None else "?"))
    if statin_discussion(p.get("age"), diabetes, ckd, cvd, dialysis):
        lines.append(_t("statin", lang))

    warn = medication_warnings(p.get("meds"), p.get("foods"), g, ckd)
    for code in warn:
        lines.append(_t(code, lang))

    life = lifestyle_codes(p, g, ckd)
    weight = _num(p.get("weight_kg"), 20, 300)
    for code in life:
        if code in ("sleep_short", "sleep_long"):
            lines.append(_t(code, lang, h=_fmt(_num(p.get("sleep_hours"), 0, 24))))
        elif code == "sitting":
            lines.append(_t(code, lang, h=_fmt(_num(p.get("sitting_hours"), 0, 24))))
        elif code == "standing":
            lines.append(_t(code, lang, h=_fmt(_num(p.get("standing_hours"), 0, 24))))
        elif code == "protein":
            w = _t("protein_w", lang, g=round(weight * 0.8)) if weight else ""
            lines.append(_t(code, lang, w=w))
        else:
            lines.append(_t(code, lang))

    lines.append(_t("red_flags", lang))
    lines.append(_t("disclaimer", lang))
    head = [_t("title", lang)] + ([T["lang_fallback"]["en"]] if not supported else [])
    return {
        "lang": lang, "lang_supported": supported, "stage": stage, "targets": targets,
        "warnings": warn, "lifestyle": life, "ask": ask,
        "text": "\n".join(head + [f"· {x}" for x in ask + lines]),
    }
