"""DriftZero — โหมดตรวจการตัดสินใจระดับองค์กร/โครงการ/นโยบาย (แยกจากโหมดปรึกษา)

ที่มา: README ของ repo KING-DIADEM-DriftZero (Deterministic Governance Kernel v0.1.0)
  Tier 1 Humility gate · E1–E3 (convenience · waterline · stabilize first) · K4–K14 · Deployment SOP 7 ขั้น
เจ้าของโปรเจกต์อยากให้เป็น "โหมดแยก" ไม่รวมกับการปรึกษาเรื่องส่วนตัว — ด่านพวกนี้เข้มเกินไปสำหรับเรื่องบ้านๆ

หลัก:
  · ตรวจจากข้อความอย่างเดียว ไม่ใช้ AI — ข้อความเดิมได้ผลเดิมทุกครั้ง (deterministic)
  · ไม่เดาตัวเลขที่ไม่มี — DHD (Daily Harm Delta) ยังไม่มีสูตรในต้นฉบับ จึง "ถามหา" ข้อมูลที่ต้องใช้วัด
  · ด่านที่ติด = หยุดก่อน (STOP) · ข้อมูลไม่พอ = ถาม (ASK) · ไม่เจอสัญญาณ = ผ่าน (PASS)
  · คนเป็นผู้ตัดสินใจและเซ็นรับผิดชอบเสมอ — ระบบไม่อนุมัติแทน
"""
from __future__ import annotations

import re

STOP, ASK, PASS = "stop", "ask", "pass"


def _rx(*parts: str) -> re.Pattern:
    return re.compile("|".join(parts), re.I)


# (id, ชื่อไทย, ชื่ออังกฤษ, regex, คำอธิบายเมื่อติด th, en)
GATES = [
    ("T1", "ด่านถ่อมตัว", "Humility gate",
     _rx(r"เอาชนะ|ต้องชนะ|ไม่ยอมแพ้|รักษาหน้า|เสียหน้า|ขายหน้า|กู้หน้า|\bto win\b|save face|lose face"),
     "ตัดสินใจเพื่อชนะหรือรักษาหน้า — ต้นฉบับให้หยุดทันที ถามใหม่ว่าอะไรดีกับทุกฝ่าย",
     "Decision made to win or save face — abort and ask what is good for everyone"),
    ("K4", "ความอยากเกินพอดี", "Desire override",
     _rx(r"กำไรสูงสุด|ได้มากที่สุด|รวยเร็ว|โกยกำไร|ฟันกำไร|ให้ได้เยอะที่สุด|ไม่สนอะไร|maximi[sz]e (?:profit|revenue)|at any cost|ไม่ว่าจะต้องแลกกับอะไร"),
     "ขับด้วยความอยากได้เป็นหลัก — ต้นฉบับให้ปฏิเสธ ลดเป้าลงให้พอดีก่อน",
     "Desire-driven decision — reject; set a sufficient target first"),
    ("K5", "ความเป็นศัตรู", "Hostility containment",
     _rx(r"เอาคืน|แก้แค้น|ตอบโต้|ทำลายคู่แข่ง|บดขยี้|ล้มคู่แข่ง|ฟ้องให้เข็ด|สั่งสอน|retaliat|revenge|crush (?:the )?competit|destroy (?:the )?competit"),
     "มีการตอบโต้/เอาคืน — ต้องมีทางออกอย่างสันติก่อน ระบุทางถอยให้อีกฝ่ายด้วย",
     "Escalation detected — a peaceful exit path must exist first"),
    ("K6", "ใช้กำลังเกินขอบเขต", "Runaway force",
     _rx(r"บังคับให้|ขู่ให้|กดดันให้|ไล่ออกทั้งหมด|ปลดพนักงานทั้งหมด|ยึดอำนาจ|ใช้อำนาจสั่ง|force them|coerce|threaten"),
     "ใช้แรงกดดัน/อำนาจ — ต้นฉบับให้ลดแรงก่อนขยาย และตั้งขอบเขตชัดเจน",
     "Force or coercion — reduce force before scaling, with clear boundaries"),
    ("K7", "ทำต่อเพราะเสียดาย", "Momentum stop",
     _rx(r"ลงทุนไปแล้ว\S{0,12}(?:ต้อง|เลย)|ลงทุนไปเยอะแล้ว|เสียดายเงินที่ลง|มาไกลแล้ว|ถอยไม่ได้แล้ว|หยุดไม่ได้แล้ว|sunk cost|too far to stop|already invested"),
     "ทำต่อเพราะลงทุนไปแล้ว — ต้นฉบับ: หยุดได้แม้จะช้า ไม่มีต้นทุนจมไหนมีค่ากว่าชีวิต",
     "Continuing because of sunk cost — stop even if late"),
    ("K8", "ภาพลักษณ์แทนความจริง", "Distortion immunity",
     _rx(r"สร้างภาพ|ภาพลักษณ์|ทำ PR|แถลงข่าวให้ดูดี|ฟอกเขียว|ดูเหมือนรักษ์โลก|ปิดข่าว|กลบข่าว|ไม่ต้องบอกใคร|greenwash|cover up|spin the story"),
     "เน้นภาพลักษณ์หรือปิดข่าว — ความจริงไม่ต้องใช้การตลาด เปิดข้อมูลที่ตรวจสอบได้แทน",
     "Image management or cover-up — truth needs no marketing; publish verifiable facts"),
    ("K9", "อัตตาในการถกเถียง", "Ego debate",
     _rx(r"ฉันถูกเสมอ|ผมถูกเสมอ|ไม่ต้องฟังใคร|ไม่ฟังความเห็น|คนอื่นผิดหมด|ยังไงก็ถูก|i'?m always right|ignore (?:the )?(?:team|feedback|critics)"),
     "ปิดรับความเห็น — ข้อโต้แย้งที่ไม่ถ่อมตัวถือว่าใช้ไม่ได้ ให้คนเห็นต่างได้พูดก่อน",
     "Closed to feedback — argument without humility is invalid"),
    ("K10", "ขยายเร็วเกินคุม", "Scale discipline",
     _rx(r"ขยายทันที|ขยายทั่วประเทศ|เปิดทีเดียวหลายสาขา|ทุกสาขาพร้อมกัน|โตแบบก้าวกระโดด|scale (?:fast|quickly|immediately)|nationwide at once|blitzscal"),
     "ขยายพร้อมกันทีเดียว — คุมให้ได้ก่อน ทดลองจุดเล็กแล้วค่อยขยาย",
     "Explosive scaling — contain first; pilot small, then grow"),
    ("K11", "มองไม่ตรงความจริง", "Wrong view",
     _rx(r"ไม่มีความเสี่ยง|ไม่มีทางพลาด|ชัวร์ 100|มั่นใจ 100|การันตี|ไม่มีทางขาดทุน|ไม่ต้องตรวจสอบ|no risk|can'?t fail|guaranteed|100% sure"),
     "มั่นใจเกินจริง ทุกอย่างเปลี่ยนแปลงได้ — เขียนสิ่งที่อาจพลาดออกมาอย่างน้อย 3 ข้อ",
     "Reality denial — everything changes; list at least 3 ways this could fail"),
    ("K12", "พบอันตราย หยุดสายพาน", "Stop the line",
     _rx(r"บาดเจ็บ|เสียชีวิต|อันตรายต่อ(?:ชีวิต|สุขภาพ|ผู้คน|ชุมชน)|สารพิษ|สารเคมีรั่ว|ปนเปื้อน|ไฟไหม้|ระเบิด|ไม่ปลอดภัย|ละเมิดความปลอดภัย|injur|fatal|toxic|contaminat|unsafe|safety violation|leak(?:ed|ing)? chemical"),
     "พบความเสี่ยงต่อชีวิต/สุขภาพ — ใครก็หยุดงานได้ทันที แก้ให้ปลอดภัยก่อนทำต่อ",
     "Harm to life or health — anyone may halt the line; make it safe first"),
    ("K13", "ผลประโยชน์ทับซ้อน", "Self-dealing",
     _rx(r"ญาติ|บริษัทของ(?:ตัวเอง|ผม|ฉัน|เรา|พี่|น้อง|ภรรยา|สามี)|บริษัทเพื่อน|คนรู้จักได้งาน|เงินทอน|ค่าคอม(?:มิชชั่น)?ใต้โต๊ะ|ผลประโยชน์ทับซ้อน|ฮั้ว|ล็อกสเปก|ล็อคสเปค|conflict of interest|kickback|my (?:own )?company|family (?:member|business)|bid rigging"),
     "มีผลประโยชน์ส่วนตัวเกี่ยวข้อง — ผู้ที่มีส่วนได้เสียต้องถอนตัว ให้คนอื่นตัดสินแทน",
     "Personal benefit conflict — the interested party must recuse; others decide"),
    ("K14", "ห่วงโซ่ที่มองไม่เห็น", "Complexity discipline",
     _rx(r"ไม่รู้ที่มา|ไม่ทราบที่มา|ไม่รู้แหล่ง|ไม่ได้ตรวจซัพพลายเออร์|ซัพพลายเออร์ไม่เปิดเผย|ไม่มีใบรับรอง|ของหนีภาษี|ราคาถูกผิดปกติ|unknown (?:source|supplier|origin)|untraceable|no certificat|opaque supply"),
     "ตรวจที่มาไม่ได้ — ต้นฉบับ: ตามรอยได้ หรือปฏิเสธ",
     "Opaque supply chain — trace it or reject it"),
    # จาก SYSTEM CORE 64 (CORE64.md) — ใช้เฉพาะในโหมดนี้ (ระดับองค์กร) ไม่ไปเทศนาคนที่มาปรึกษาเรื่องส่วนตัว
    ("C26", "ไม่บีบใครจนไร้ที่อยู่", "No one squeezed out of a home",
     _rx(r"ไล่ที่|ขับไล่(?:ผู้|ชาว|คน)|ไล่ผู้เช่า|รื้อชุมชน|รื้อบ้าน(?:เรือน)?|เวนคืนโดยไม่|ย้ายชุมชนออก|ไล่ชาวบ้าน|"
         r"evict|demolish (?:the )?(?:homes|community|houses)|forced relocation"),
     "ทำให้คนไม่มีที่อยู่ — ปัจจัยพื้นฐานคือสิทธิ ไม่ใช่รางวัล (Core 26, 27) · ต้องมีที่อยู่รองรับและการชดเชยที่เป็นธรรมก่อน",
     "Leaves people without a home — basic needs are rights, not rewards (Core 26, 27) · secure housing and fair compensation first"),
    ("C61", "ชีวิตสัตว์ไม่ใช่ราคาของความสะดวก", "Animal lives are not the price of convenience",
     _rx(r"วางยาเบื่อ|ฆ่าทิ้ง|กำจัด(?:หมา|สุนัข|แมว)(?:จรจัด)?|ทิ้งสัตว์|ปล่อยสัตว์(?:ให้)?ตาย|ทารุณ(?:กรรม)?สัตว์|ทดลอง(?:กับ|ใน)สัตว์|"
         r"ทำลายที่อยู่(?:อาศัย)?ของสัตว์|ถมป่าชายเลน|ล่าสัตว์|ช็อตสัตว์|"
         r"cull(?:ing)?|animal testing|poison(?:ing)? (?:the )?(?:stray|dogs|cats|birds)|destroy (?:the )?habitat|abandon (?:the )?animals"),
     "ชีวิตสัตว์ต้องไม่ตายเพราะความสะดวกของมนุษย์ (Core 61, 62) · หาทางที่ไม่ต้องแลกชีวิตสัตว์ก่อน เช่น ย้าย ทำหมัน กันพื้นที่",
     "Animals must not die for human convenience (Core 61, 62) · find a way that costs no animal lives first, e.g. relocate, sterilise, fence"),
    ("E1", "แลกความสะดวกกับความเสียหายระยะยาว", "Convenience trade-off",
     _rx(r"ใช้ครั้งเดียวทิ้ง|พลาสติกครั้งเดียว|ตัดต้นไม้|ถางป่า|เผา(?:ขยะ|ป่า|ไร่)|ทิ้งขยะ|ฝังกลบ|ลดต้นทุนด้วยการไม่บำบัด|single-use|clear(?:ing)? (?:the )?forest|burn(?:ing)? (?:waste|fields)|landfill"),
     "สะดวกวันนี้แต่โลกเสียหายระยะยาว — ค่าเริ่มต้นของต้นฉบับคือปฏิเสธ หาทางที่ไม่ทิ้งภาระ",
     "Short-term convenience with long-term harm — default: reject"),
    # Waterline ในระดับองค์กร = "เส้นขั้นต่ำที่ห้ามต่ำกว่า ไม่งั้นความเสียหายย้อนกลับไม่ได้" (เจ้าของโปรเจกต์นิยาม)
    # ไม่ใช่เรื่องน้ำอย่างเดียว — คนบริหารเงินหลักล้าน/พันล้านอ่าน "เส้นน้ำ" แล้วจะงงว่าน้ำเกี่ยวอะไรกับองค์กร
    # เดิมด่านนี้จับแค่คำเรื่องแหล่งน้ำ ตอนนี้จับการดันบางอย่างให้ต่ำกว่าเส้นที่กลับมาไม่ได้: เงินสดสำรอง
    # ทรัพย์หลัก คนหลัก ใบอนุญาต ความเชื่อใจ — ส่วนแหล่งน้ำ/ธรรมชาติยังนับเป็นกรณีหนึ่งของเส้นนี้
    ("E2", "Waterline — เส้นที่ห้ามต่ำกว่า", "Waterline — the floor you must not cross",
     _rx(r"เงินสำรองทั้งหมด|ใช้เงินสำรอง(?:จน)?หมด|ทุ่มหมดหน้าตัก|หมดหน้าตัก|เทหมดตัว|all[- ]in|ใช้เงินสดทั้งหมด|เงินสดเหลือไม่ถึง|"
         r"กู้เต็มวงเงิน|จำนอง(?:ทั้งหมด|ทุกอย่าง)|ค้ำประกันส่วนตัว|เอาบ้านไปค้ำ|ขายสินทรัพย์หลัก|ขายโรงงาน|ขายกิจการ|"
         r"ปลดคน(?:จน)?เหลือไม่พอ|เลิกจ้างทีมหลัก|ผิดนัดชำระ|ใบอนุญาต(?:ถูก)?(?:เพิกถอน|ระงับ)|ละเมิดสัญญา|"
         r"เสียความเชื่อใจของลูกค้า|ทำลายชื่อเสียง|ย้อนกลับไม่ได้|irreversible|point of no return|bet the company|"
         r"entire (?:cash )?reserves?|max(?:imum)? (?:out )?(?:the )?credit line|personal guarantee|default on|sell (?:the )?core assets?|"
         r"น้ำเสีย|ปล่อยน้ำ|ระบายน้ำ(?:ลง|ทิ้ง)|ลงแม่น้ำ|ลงคลอง|น้ำบาดาล|แหล่งน้ำ|ตัดไม้ทำลายป่า|wastewater|discharge into|groundwater|aquifer"),
     "อาจดันบางอย่างให้ต่ำกว่าเส้นขั้นต่ำ — ต่ำกว่าเส้นนี้ความเสียหายย้อนกลับไม่ได้ (เงินสด ทรัพย์หลัก คน ใบอนุญาต ความเชื่อใจ ธรรมชาติ) · กำหนดตัวเลขเส้นขั้นต่ำก่อน แล้วหยุดถ้าจะต่ำกว่า",
     "This could push something below its floor — beneath it the damage can't be undone (cash, core assets, people, licences, trust, nature) · set the floor as a number first, and stop if you would cross it"),
]
_GATE_INFO = {g[0]: g for g in GATES}

# สัญญาณว่ามีการพูดถึงผลเสียแล้ว (SOP 2) และมีคนรับผิดชอบ (SOP 6)
_DOWNSIDE = _rx(r"ความเสี่ยง|ผลเสีย|ข้อเสีย|ถ้าพลาด|ถ้าล้มเหลว|เสียหาย|ขาดทุน|แผนสำรอง|risk|downside|worst case|if it fails|fallback")
_FLOOR = _rx(r"ขั้นต่ำ|ไม่ต่ำกว่า|อย่างน้อย|สำรอง(?:ไว้)?\s*\d|เงินสดสำรอง|runway|minimum|at least|floor|reserve of")
_OWNER = _rx(r"ผู้รับผิดชอบ|รับผิดชอบโดย|เซ็นอนุมัติ|ผู้อนุมัติ|คณะกรรมการ|บอร์ด|ผู้จัดการ|หัวหน้าโครงการ|accountab|sign(?:ed|s)? off|approv(?:er|ed by)|\bboard\b|\bowner\b")
_DRIFT = _rx(r"ทุกวัน|ต่อวัน|รายวัน|วันละ|/วัน|ต่อเดือน|เดือนละ|/เดือน|ทีละนิด|สะสม|เพิ่มขึ้นเรื่อยๆ|ลดลงเรื่อยๆ|per day|daily|per month|accumulat|gradually")
_NUM = re.compile(r"\d")
# เป็นเรื่องตัดสินใจขององค์กร/โครงการจริงไหม — ไม่ใช่ ให้แนะนำโหมดปรึกษา
_ORG = _rx(r"บริษัท|องค์กร|โครงการ|โรงงาน|ธุรกิจ|ร้าน|สาขา|นโยบาย|ชุมชน|หน่วยงาน|ทีม|พนักงาน|ลูกค้า|ซัพพลายเออร์|งบประมาณ|ลงทุน|ผลิต|"
           r"company|organi[sz]ation|project|factory|business|policy|team|staff|budget|invest|supplier|community|plant|"
           r"\bstores?\b|\bshops?\b|branch|employee|customer|startup|school|hospital|department|government|firm|launch|hire|hiring|layoff|"
           # ผู้ใช้จริงคนแรกถามว่า "spend 10k on facebook ads" แล้วโดนบอกว่า "ดูเหมือนเป็นเรื่องส่วนตัว" — งานขาย/การตลาดก็คือการตัดสินใจของกิจการ
           r"\bads?\b|advertis|marketing|campaign|revenue|\bsales\b|clients?\b|product|vendor|contract|pricing|\bbrand\b|"
           r"โฆษณา|การตลาด|แคมเปญ|ยอดขาย|สินค้า|รายได้|กิจการ|แบรนด์|ยิงแอด|เปิดร้าน")

SOP = [
    ("กำหนดเรื่องที่จะตัดสินใจให้ชัด", "Define input clearly"),
    ("ดูผลเสียก่อน", "Identify downside first"),
    ("วัดการไหลลงทีละนิด (DHD)", "Measure drift (DHD)"),
    ("ผ่านด่าน K4–K14", "Pass K4–K14 gates"),
    ("อธิบายได้ใน 2 นาที", "Explain within 2 minutes"),
    ("คนเซ็นรับผิดชอบ", "Human signs accountability"),
    ("ตรวจหลังทำ แล้วปิดวงจร", "Post-audit and close loop"),
]


def _money(v) -> str:
    if v is None:
        return "-"
    for unit, d in (("พันล้าน", 1e9), ("ล้าน", 1e6)):
        if abs(v) >= d:
            return f"{v / d:,.2f}".rstrip("0").rstrip(".") + " " + unit
    return f"{v:,.0f}"


def _money_en(v) -> str:
    if v is None:
        return "-"
    for unit, d in (("B", 1e9), ("M", 1e6)):
        if abs(v) >= d:
            return f"{v / d:,.2f}".rstrip("0").rstrip(".") + unit
    return f"{v:,.0f}"


def _danger(text: str) -> tuple[bool, bool]:
    """(วิกฤตของคน, เหตุอันตรายตอนนี้)
    วิกฤตของคน (คิดทำร้ายตัวเอง) = ไม่ใช่เวลาตรวจด่าน ส่งไปหาความช่วยเหลือ
    เหตุอันตราย (สารเคมีรั่ว ไฟไหม้ คนเจ็บ) = ยังตรวจด่านได้ แต่ต้องโชว์เบอร์ฉุกเฉินก่อน — เดิม "สารเคมีรั่วในไลน์ผลิต"
    ถูกตัดไปเป็นเรื่องด่วนทั้งก้อน เลยไม่เห็นด่าน K12 Stop the line ที่ตรงที่สุด"""
    try:
        from core.kernel_voice import assess
        a = assess(text)
        crisis = bool(a.get("crisis")) or "crisis" in (a.get("topics") or [])
        return crisis, (not crisis and a.get("text_risk", 0) >= 85)
    except Exception:
        return False, False


ASK_KEYS = ("detail", "downside", "dhd", "current", "floor", "owner")
# หัวข้อของตัวจับหลักที่แปลว่า "ผู้ใช้เองกำลังลำบาก" — เช่น Haydn ตอบคำถามด่านว่า "i can't pay rent"
# เรื่องแบบนี้ไม่ใช่การตัดสินใจขององค์กร ชวนไปโหมดปรึกษาแทนการถามด่านต่อ
_DISTRESS = {"housing", "money", "debt", "basic", "lent", "job", "labor", "stress", "lonely", "panic",
             "grief", "eating", "sleepless", "family", "relationship", "health"}
# เลขเปล่าๆ ตามด้วยหน่วย ("ขาดทุน 3 แสน" · "hire 3 people") คือจำนวน ไม่ใช่เลขข้อ — เลขข้อที่มีจุด/วงเล็บ ("3.") นับเสมอ
_UNIT = (r"(?:แสน|ล้าน|พัน|หมื่น|บาท|คน|วัน|เดือน|ปี|สัปดาห์|ชั่วโมง|นาที|เท่า|แห่ง|สาขา|ครั้ง|ตัว|ชิ้น|กิโล|ลิตร|ตัน|%|"
         r"people|persons?|staff|days?|weeks?|months?|years?|hours?|times|stores?|branches|units?|million|thousand|percent)")
_MARK = re.compile(r"(?:^|(?<=\s))(?:ข้อ\s*)?(\d{1,2})(?:\s*[).:\-]\s*|\s+(?!" + _UNIT + r"(?![a-z])))")


def parse_numbered(answer: str) -> dict[int, str]:
    """แยกคำตอบแบบเป็นข้อ "1 i do it 2. i can't pay rent 3 1k" → {1: "i do it", 2: "i can't pay rent", 3: "1k"}
    ต้องเริ่มที่ 1 และนับเรียงทีละข้อ — ตัวเลขอื่นในประโยค ("จ้าง 5 คน") ไม่ถูกนับเป็นเลขข้อ"""
    a = str(answer or "").strip()
    cuts, want = [], 1
    for m in _MARK.finditer(a):
        if int(m.group(1)) == want:
            cuts.append((want, m.start(), m.end())); want += 1
    if not cuts or cuts[0][1] != 0:
        return {}
    out = {}
    for i, (n, _, end) in enumerate(cuts):
        stop = cuts[i + 1][1] if i + 1 < len(cuts) else len(a)
        part = a[end:stop].strip(" ,;\n")
        if part:
            out[n] = part
    return out


def answered_keys(answer: str, prior_keys) -> set[str]:
    """คำถามรอบก่อนข้อไหนที่ผู้ใช้ตอบแล้ว — ตอบแบบเป็นข้อ จับคู่ตามลำดับ · ถามข้อเดียวแล้วตอบเฉยๆ = ตอบข้อนั้น"""
    keys = [k for k in (prior_keys or []) if k in ASK_KEYS]
    parts = parse_numbered(answer)
    if parts:
        return {keys[n - 1] for n in parts if 0 < n <= len(keys)}
    if len(keys) == 1 and str(answer or "").strip():
        return {keys[0]}
    return set()


def distress(text: str) -> bool:
    try:
        from core.kernel_voice import assess
        return bool(_DISTRESS & set(assess(text).get("topics") or []))
    except Exception:
        return False


# คำตอบแต่ละข้อถูกเก็บต่อท้ายเรื่องเดิมเป็นบรรทัดที่มีป้ายกำกับ — ตัววัด Waterline อ่านตัวเลขจากป้ายได้ทันที
# ("floor: 1k" · "cash on hand: 3k") และใบสรุปอ่านคำตอบกลับออกมาได้โดยไม่ต้องให้หน้าเว็บจำอะไรเพิ่ม
LABELS = {"detail": "detail", "downside": "worst case", "floor": "floor", "current": "cash on hand",
          "dhd": "drift per day", "owner": "accountable"}
_LABEL_LINE = re.compile(r"^(" + "|".join(re.escape(v) for v in LABELS.values()) + r"): (.+)$", re.M)
_BRIEF_ROWS = (("downside", "ถ้าพลาด", "Worst case"), ("floor", "เส้นขั้นต่ำ", "Floor"), ("current", "ตอนนี้มี", "On hand now"),
               ("dhd", "สิ่งที่ต้องเฝ้าดูทุกวัน", "Watch daily"), ("owner", "คนรับผิดชอบ", "Accountable"), ("detail", "รายละเอียด", "Details"))


def brief(text: str, wl: dict) -> dict | None:
    """ใบสรุปการตัดสินใจ — รวมสิ่งที่ผู้ใช้ตอบมา + ตัวเลขที่คำนวณได้ + กติกาหยุด เป็นแผ่นเดียวที่คัดลอกไปใช้ต่อได้
    เดิมตอบครบแล้วได้แค่ "ผ่านทุกด่าน" คนที่อุตส่าห์ตอบไม่ได้อะไรกลับไปเลย"""
    by_label = {v: k for k, v in LABELS.items()}
    got = {}
    for m in _LABEL_LINE.finditer(text):
        got[by_label[m.group(1)]] = m.group(2).strip()
    if not got:
        return None
    decision = _LABEL_LINE.split(text)[0].strip()
    rows = [{"k": "decision", "th": "เรื่องที่จะตัดสินใจ", "en": "Decision", "v": decision[:400]}]
    rows += [{"k": k, "th": th, "en": en, "v": got[k][:400]} for k, th, en in _BRIEF_ROWS if k in got]
    fl, cur, sp, after = wl.get("floor"), wl.get("current"), wl.get("spend"), wl.get("after")
    rule = None
    if after is not None and wl.get("level") == "below":
        room = cur - fl
        if room > 0:
            rule = {"th": f"ขนาดนี้ยังไม่ควรทำ: จะเหลือ {_money(after)} ต่ำกว่าเส้นขั้นต่ำ {_money(fl)} · ทำได้มากสุด {_money(room)} โดยไม่หลุดเส้น — ลดขนาดหรือแบ่งทำเป็นช่วง",
                    "en": f"Not at this size: you would be left with {_money_en(after)}, under your floor of {_money_en(fl)}. "
                          f"The most you can put in without crossing it is {_money_en(room)} — shrink it or do it in phases."}
        else:
            rule = {"th": f"ตอนนี้อยู่ที่เส้นขั้นต่ำ ({_money(fl)}) หรือต่ำกว่าแล้ว — ยังไม่ควรใช้เพิ่ม ทำให้กลับมาเหนือเส้นก่อน",
                    "en": f"You are already at or under your floor ({_money_en(fl)}) — don't put more in; get back above it first."}
    elif after is not None:
        rule = {"th": f"หลังทำจะเหลือ {_money(after)} ยังเหนือเส้นขั้นต่ำ {_money(fl)} · กติกาหยุด: ถ้าลงมาแตะ {_money(fl)} ให้หยุดแล้วตรวจใหม่ทันที",
                "en": f"After this you would have {_money_en(after)}, still above your floor of {_money_en(fl)}. "
                      f"Stop rule: the moment it reaches {_money_en(fl)}, pause and re-check."}
        d = wl.get("days_to_floor")
        if d is not None:
            rule["th"] += f" · ด้วยอัตราตอนนี้จะถึงเส้นในอีก {d} วัน"
            rule["en"] += f" At the current pace you reach it in {d} days."
    elif fl is not None:
        rule = {"th": f"กติกาหยุด: ถ้าลงมาแตะ {_money(fl)} ให้หยุดแล้วตรวจใหม่ทันที",
                "en": f"Stop rule: the moment you reach {_money_en(fl)}, pause and re-check."}
    return {"rows": rows, "rule": rule,
            "next": {"th": "ทำแล้วกลับมาตรวจอีกครั้งว่าเกิดอะไรขึ้นจริง (ตรวจหลังทำ) — คุณเป็นคนตัดสินใจเสมอ",
                     "en": "After you act, come back and check what actually happened (post-audit) — the decision is always yours."}}


# ผู้ใช้จริงคนแรกงงกับหน้าจอ แล้วพิมพ์ถามในโหมดนี้ว่า "what does drift zero do?" — เดิมระบบเอาคำถามนั้นไปตรวจด่านเหมือนเป็นการตัดสินใจ
_ABOUT = _rx(r"what (?:does|is) (?:this|it|drift ?zero)\b|how (?:does|do) (?:this|it|drift ?zero|i use)\b|what (?:do|should) i (?:do|type|write)\b|"
             r"^\s*(?:help|\?+|how to use)\s*\??\s*$|i(?:'m| am) confused|i don'?t (?:understand|get it)|"
             r"drift ?zero (?:คืออะไร|ทำอะไร|ใช้ยังไง|ใช้อย่างไร)|(?:โหมดนี้|อันนี้|นี่)(?:คืออะไร|ทำอะไร|ใช้ยังไง)|ใช้ยังไง|ต้องพิมพ์อะไร|ไม่เข้าใจ|(?<!โร)งง(?!าน)")   # "งง" ต้องไม่ใช่ส่วนของคำว่า "โรงงาน"
ABOUT_TEXT = {
    "th": "DriftZero คือรายการตรวจก่อนตัดสินใจเรื่องใหญ่ เช่น \"ใช้เงิน 10,000 ยิงโฆษณา\" — ตรวจด้วยกฎ ไม่ใช้ AI ข้อความเดิมได้ผลเดิมเสมอ\n"
          "วิธีใช้: 1) พิมพ์สิ่งที่กำลังจะตัดสินใจ  2) ตอบคำถามสั้นๆ ที่ระบบถามกลับ พิมพ์เป็นข้อ (1 … 2 …) ได้  "
          "3) รับใบสรุป: ควรทำ รอ หรือหยุด พร้อมตัวเลขว่าทำได้มากสุดเท่าไหร่ — คุณเป็นคนตัดสินใจเสมอ\n"
          "ถ้าอยากคุยเล่าเรื่องทั่วไป กดไปโหมดปรึกษาได้เลยค่ะ",
    "en": "DriftZero is a pre-decision checklist for a big call like \"spend 10k on Facebook ads\". It runs on rules, not AI, so the same text always gives the same result.\n"
          "How to use it: 1) type the decision you are about to make  2) answer the few short questions it asks back — numbered replies (1 … 2 …) are fine  "
          "3) get a brief: go, wait or stop, with the most you can put in safely. The decision is always yours.\n"
          "For an open conversation, switch to Talk mode.",
}


def is_about(text: str) -> bool:
    t = str(text or "").strip()
    return len(t) <= 80 and bool(_ABOUT.search(t)) and not parse_numbered(t)


def about(prior: dict | None = None) -> dict:
    """คำอธิบายโหมด — ถ้ากำลังตอบคำถามค้างอยู่ คำถามเดิมยังอยู่ครบ ตอบต่อได้เลย ไม่ต้องเริ่มใหม่"""
    r = dict(prior) if prior else {"text": "", "talk": False, "gates": [], "asks": [], "sop": [], "note": None,
                                   "emergency": False, "brief": None, "waterline": None}
    r.update(verdict="about", about=True, summary=dict(ABOUT_TEXT), talk=True if not prior else r.get("talk", False))
    return r


def follow_up(prior_text: str, prior_keys, answer: str) -> dict:
    """ตรวจรอบต่อ: รวมเรื่องเดิมกับคำตอบ แล้วถามเฉพาะข้อที่ยังขาด — เดิมตรวจแค่ข้อความใหม่ เลยถามซ้ำครบทุกข้อ"""
    prior_text = str(prior_text or "").strip()[:4000]
    answer = str(answer or "").strip()[:4000]
    if is_about(answer):
        return about(audit(prior_text))
    got = answered_keys(answer, prior_keys)
    parts = parse_numbered(answer)
    body = " ".join(parts.values()) if parts else answer
    keys = [k for k in (prior_keys or []) if k in ASK_KEYS]
    if parts:
        lines = [f"{LABELS[keys[n - 1]]}: {v}" for n, v in sorted(parts.items()) if 0 < n <= len(keys)]
    elif len(keys) == 1 and answer:
        lines = [f"{LABELS[keys[0]]}: {answer}"]
    else:
        lines = [answer]
    lines = [" ".join(x.split()) for x in lines if x]              # หนึ่งคำตอบ = หนึ่งบรรทัด
    r = audit((prior_text + "\n" + "\n".join(lines)).strip(), answered=got)
    r["answered"] = sorted(got)
    if r["verdict"] != "urgent" and distress(body):
        r["note"] = {"th": "ฟังดูเหมือนคุณเองกำลังลำบากเรื่องนี้อยู่ — DriftZero ตรวจการตัดสินใจขององค์กร "
                           "ส่วนเรื่องเงิน ที่พัก หรือความเครียดของตัวเอง โหมดปรึกษาช่วยได้ตรงกว่า ลองเล่าที่นั่นได้เลยนะคะ",
                     "en": "It sounds like you're going through this yourself — DriftZero checks decisions made by organisations. "
                           "For your own money, housing or stress, Talk mode can help much more. You can tell LYLA there."}
        r["talk"] = True
    return r


def _answered_before(text: str) -> set[str]:
    by_label = {v: k for k, v in LABELS.items()}
    return {by_label[m.group(1)] for m in _LABEL_LINE.finditer(text or "")}


def audit(text: str, answered=()) -> dict:
    t = str(text or "").strip()
    answered = set(answered or ())
    if not answered and is_about(t):
        return about()
    crisis, emergency = _danger(t)
    if crisis:
        return {"verdict": "urgent", "gates": [], "asks": [], "sop": [],
                "summary": {"th": "เรื่องนี้เกี่ยวกับความปลอดภัยของชีวิต — ขอให้ติดต่อคนที่ช่วยได้ทันที "
                                  "(1669 เจ็บป่วยฉุกเฉิน · 191 ตำรวจ · 1323 สุขภาพจิต) แล้วค่อยกลับมาที่โหมดปรึกษานะคะ",
                            "en": "This is about someone's safety — please contact help now (in Thailand 1669 medical · 191 police · "
                                  "1323 mental health), then come back in Talk mode."}}
    from ENGINE.waterline_gauge import gauge
    wl = gauge(t)
    gates = []
    for gid, th, en, rx, why_th, why_en in GATES:
        m = rx.search(t)
        g = {"id": gid, "name": {"th": th, "en": en}, "status": STOP if m else PASS,
             "hit": m.group(0) if m else "", "why": {"th": why_th, "en": why_en} if m else None}
        if gid == "E2":
            if wl["level"] == "below":                      # L0: ต่ำกว่าเส้นไม่ได้เด็ดขาด
                g.update(status=STOP, hit=g["hit"] or f"{_money(wl['after'])} < {_money(wl['floor'])}",
                         why={"th": f"ใต้ระดับน้ำ (Below Water) — หลังตัดสินใจเหลือ {_money(wl['after'])} ต่ำกว่าเส้น {_money(wl['floor'])} "
                                    "· Stop-the-Line: ต่ำกว่าเส้นนี้ความเสียหายย้อนกลับไม่ได้ ลดขนาดหรือแบ่งเป็นช่วงก่อน",
                              "en": f"Below water — after this decision {_money_en(wl['after'])} is under the floor {_money_en(wl['floor'])} "
                                    "· Stop the line: below this the damage can't be undone; shrink it or phase it first"})
            elif wl["days_to_floor"] is not None and wl["days_to_floor"] <= 30:
                g.update(status=STOP, hit=g["hit"] or f"{wl['days_to_floor']} days",
                         why={"th": f"จะแตะเส้นขั้นต่ำในอีก {wl['days_to_floor']} วันด้วยอัตราไหลลงตอนนี้ "
                                    "· Stop-the-Line: ดึงความเสี่ยงกลับก่อนถึงเส้น",
                              "en": f"At the current drift you reach the floor in {wl['days_to_floor']} days "
                                    "· Stop the line: pull the risk back before you reach it"})
        gates.append(g)
    stops = [g for g in gates if g["status"] == STOP]

    asks = []
    if len(t) < 40:
        asks.append({"key": "detail", "sop": 1, "th": "เล่าเพิ่มอีกนิด: ใครทำอะไร ที่ไหน งบเท่าไหร่ ภายในเมื่อไหร่",
                     "en": "Say a bit more: who does what, where, with what budget, by when"})
    if not _DOWNSIDE.search(t):
        asks.append({"key": "downside", "sop": 2, "th": "ถ้าพลาด อะไรเสียหายที่สุด และใครรับผลนั้น",
                     "en": "If this fails, what is the worst damage, and who bears it?"})
    if not (_DRIFT.search(t) and _NUM.search(t)):
        asks.append({"key": "dhd", "sop": 3, "th": "DHD: ถ้าทำต่อไปเรื่อยๆ อะไรจะแย่ลงทีละนิดทุกวัน — วัดเป็นตัวเลขอะไรได้บ้าง (เช่น เงินออกวันละเท่าไหร่ · ลูกค้าหายเดือนละกี่ราย · ของเสียกี่ลิตร/วัน)",
                     "en": "DHD (daily drift): if this keeps going, what gets a little worse every day — and what number shows it? (e.g. money going out per day, customers lost per month)"})
    if wl["floor"] is not None and wl["current"] is None:
        asks.append({"key": "current", "sop": 2, "th": "Waterline: ตอนนี้มีเท่าไหร่ (เช่น เงินสดคงเหลือ) — จะได้คำนวณว่าหลังตัดสินใจยังอยู่เหนือเส้นขั้นต่ำไหม",
                     "en": "Waterline: how much do you have right now (e.g. cash on hand)? Then I can work out whether you stay above your floor"})
    if wl["floor"] is None:
        asks.append({"key": "floor", "sop": 2, "th": "Waterline: เส้นขั้นต่ำของเรื่องนี้คือเท่าไหร่ — ตัวเลขที่ห้ามต่ำกว่า ไม่งั้นความเสียหายย้อนกลับไม่ได้ "
                                    "(เช่น ต้องเหลือเงินสดไม่ต่ำกว่า 50,000 · ทีมหลักไม่ต่ำกว่า 5 คน)",
                     "en": "Waterline (your floor): what is the lowest you can safely go — the number you must not fall below, or the damage can't be undone? "
                           "(e.g. keep at least 5k in cash · at least 5 core staff)"})
    if not _OWNER.search(t):
        asks.append({"key": "owner", "sop": 6, "th": "ใครเป็นคนรับผิดชอบการตัดสินใจนี้ (ชื่อหรือตำแหน่ง)",
                     "en": "Who is responsible for this decision? (a name or a role)"})

    answered |= _answered_before(t)
    asks = [q for q in asks if q["key"] not in answered]
    asks.sort(key=lambda q: q["sop"])
    if stops:
        verdict = "stop"
        sm_th = "หยุดก่อน — ติด " + " · ".join(f"{g['id']} {g['name']['th']}" for g in stops) + \
                " · แก้ด่านที่ติดให้ผ่านก่อน แล้วค่อยตรวจใหม่ (ต้นฉบับ: ทำให้นิ่งก่อน ค่อยทำให้ดีขึ้น)"
        sm_en = "Stop first — blocked at " + " · ".join(f"{g['id']} {g['name']['en']}" for g in stops) + \
                " · resolve these gates, then re-check (stabilize before optimizing)"
    elif asks:
        verdict = "ask"
        sm_th = f"ยังไม่เจอด่านที่ติด แต่ข้อมูลยังไม่ครบ {len(asks)} ข้อ — ตอบในช่องพิมพ์ได้เลย จะพิมพ์เป็นข้อ (1 … 2 …) ก็ได้"
        sm_en = f"No gate blocked yet, but {len(asks)} answer(s) are missing — reply below, numbered (1 … 2 …) is fine"
    else:
        verdict = "pass"
        sm_th = "ผ่านทุกด่านจากข้อมูลที่ให้มา — ยังต้องมีคนเซ็นรับผิดชอบ และตรวจหลังทำ (SOP 7)"
        sm_en = "Passes every gate on the information given — a human still signs off, and a post-audit closes the loop"

    done = {1: len(t) >= 40 or "detail" in answered, 2: bool(_DOWNSIDE.search(t)) or "downside" in answered,
            3: bool(_DRIFT.search(t) and _NUM.search(t)) or "dhd" in answered,
            4: not stops, 5: True, 6: bool(_OWNER.search(t)) or "owner" in answered, 7: False}
    sop = [{"n": i + 1, "th": th, "en": en, "done": done[i + 1]} for i, (th, en) in enumerate(SOP)]
    note = None
    if not _ORG.search(t):
        note = {"th": "ดูเหมือนเป็นเรื่องส่วนตัว — โหมดปรึกษาน่าจะช่วยได้ตรงกว่านะคะ",
                "en": "This looks personal — Talk mode will probably help more."}
    return {"text": t[:4000], "talk": bool(note), "verdict": verdict, "gates": gates, "asks": asks, "sop": sop, "note": note, "emergency": emergency, "brief": brief(t, wl), "waterline": dict(wl, show={
                "th": {k: _money(wl[k]) for k in ("floor", "current", "after")},
                "en": {k: _money_en(wl[k]) for k in ("floor", "current", "after")}}),
            "summary": {"th": sm_th, "en": sm_en}}
