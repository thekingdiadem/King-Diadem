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
           r"company|organi[sz]ation|project|factory|business|policy|team|staff|budget|invest|supplier|community|plant")

SOP = [
    ("กำหนดเรื่องที่จะตัดสินใจให้ชัด", "Define input clearly"),
    ("ดูผลเสียก่อน", "Identify downside first"),
    ("วัดการไหลลงทีละนิด (DHD)", "Measure drift (DHD)"),
    ("ผ่านด่าน K4–K14", "Pass K4–K14 gates"),
    ("อธิบายได้ใน 2 นาที", "Explain within 2 minutes"),
    ("คนเซ็นรับผิดชอบ", "Human signs accountability"),
    ("ตรวจหลังทำ แล้วปิดวงจร", "Post-audit and close loop"),
]


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


def audit(text: str) -> dict:
    t = str(text or "").strip()
    crisis, emergency = _danger(t)
    if crisis:
        return {"verdict": "urgent", "gates": [], "asks": [], "sop": [],
                "summary": {"th": "เรื่องนี้เกี่ยวกับความปลอดภัยของชีวิต — ขอให้ติดต่อคนที่ช่วยได้ทันที "
                                  "(1669 เจ็บป่วยฉุกเฉิน · 191 ตำรวจ · 1323 สุขภาพจิต) แล้วค่อยกลับมาที่โหมดปรึกษานะคะ",
                            "en": "This is about someone's safety — please contact help now (in Thailand 1669 medical · 191 police · "
                                  "1323 mental health), then come back in Talk mode."}}
    gates = []
    for gid, th, en, rx, why_th, why_en in GATES:
        m = rx.search(t)
        gates.append({"id": gid, "name": {"th": th, "en": en}, "status": STOP if m else PASS,
                      "hit": m.group(0) if m else "", "why": {"th": why_th, "en": why_en} if m else None})
    stops = [g for g in gates if g["status"] == STOP]

    asks = []
    if len(t) < 40:
        asks.append({"sop": 1, "th": "เล่าเพิ่มอีกนิด: ใครทำอะไร ที่ไหน งบเท่าไหร่ ภายในเมื่อไหร่",
                     "en": "Say a bit more: who does what, where, with what budget, by when"})
    if not _DOWNSIDE.search(t):
        asks.append({"sop": 2, "th": "ถ้าพลาด อะไรเสียหายที่สุด และใครรับผลนั้น",
                     "en": "If this fails, what is the worst damage, and who bears it?"})
    if not (_DRIFT.search(t) and _NUM.search(t)):
        asks.append({"sop": 3, "th": "DHD: ถ้าทำต่อไปเรื่อยๆ อะไรจะแย่ลงทีละนิดทุกวัน — วัดเป็นตัวเลขอะไรได้บ้าง (เช่น ของเสียกี่ลิตร/วัน · คนได้รับผลกี่คน/เดือน)",
                     "en": "DHD: if this continues, what gets a little worse every day — what number can measure it (e.g. litres of waste/day, people affected/month)?"})
    if not (_FLOOR.search(t) and _NUM.search(t)):
        asks.append({"sop": 2, "th": "Waterline: เส้นขั้นต่ำของเรื่องนี้คืออะไร — ตัวเลขที่ห้ามต่ำกว่า ไม่งั้นความเสียหายย้อนกลับไม่ได้ "
                                    "(เช่น เงินสดสำรองไม่ต่ำกว่า 6 เดือนของค่าใช้จ่าย · ทีมหลักไม่ต่ำกว่า 5 คน)",
                     "en": "Waterline: what is the floor here — the number you must not go below, or the damage can't be undone "
                           "(e.g. cash reserve of at least 6 months of costs · at least 5 core staff)"})
    if not _OWNER.search(t):
        asks.append({"sop": 6, "th": "ใครเป็นคนเซ็นรับผิดชอบการตัดสินใจนี้",
                     "en": "Who signs accountability for this decision?"})

    asks.sort(key=lambda q: q["sop"])
    if stops:
        verdict = "stop"
        sm_th = "หยุดก่อน — ติด " + " · ".join(f"{g['id']} {g['name']['th']}" for g in stops) + \
                " · แก้ด่านที่ติดให้ผ่านก่อน แล้วค่อยตรวจใหม่ (ต้นฉบับ: ทำให้นิ่งก่อน ค่อยทำให้ดีขึ้น)"
        sm_en = "Stop first — blocked at " + " · ".join(f"{g['id']} {g['name']['en']}" for g in stops) + \
                " · resolve these gates, then re-check (stabilize before optimizing)"
    elif asks:
        verdict = "ask"
        sm_th = f"ยังไม่เจอด่านที่ติด แต่ข้อมูลยังไม่ครบ {len(asks)} ข้อ — ตอบให้ครบแล้วตรวจอีกรอบ"
        sm_en = f"No gate blocked yet, but {len(asks)} answer(s) are missing — fill them in and re-check"
    else:
        verdict = "pass"
        sm_th = "ผ่านทุกด่านจากข้อมูลที่ให้มา — ยังต้องมีคนเซ็นรับผิดชอบ และตรวจหลังทำ (SOP 7)"
        sm_en = "Passes every gate on the information given — a human still signs off, and a post-audit closes the loop"

    done = {1: len(t) >= 40, 2: bool(_DOWNSIDE.search(t)), 3: bool(_DRIFT.search(t) and _NUM.search(t)),
            4: not stops, 5: True, 6: bool(_OWNER.search(t)), 7: False}
    sop = [{"n": i + 1, "th": th, "en": en, "done": done[i + 1]} for i, (th, en) in enumerate(SOP)]
    note = None
    if not _ORG.search(t):
        note = {"th": "ดูเหมือนเป็นเรื่องส่วนตัว — โหมดปรึกษาน่าจะช่วยได้ตรงกว่านะคะ",
                "en": "This looks personal — Talk mode will probably help more."}
    return {"verdict": verdict, "gates": gates, "asks": asks, "sop": sop, "note": note, "emergency": emergency,
            "summary": {"th": sm_th, "en": sm_en}}
