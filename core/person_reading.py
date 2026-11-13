"""
core/person_reading.py — อ่านว่าคนตรงหน้าต้องการคำตอบแบบไหน (ตำรามนุษย์เล่มแรก: MBTI)

เจ้าของโปรเจกต์: "สอนให้รู้จักมนุษย์ ตำรามนุษย์เล่มแรกก็ MBTI" — ไม่ใช่ให้เดาไทป์ แต่ให้เข้าใจว่าคนต่างกันอย่างไร
แล้วตอบในแบบที่คนนั้นรับได้ดีที่สุด

MBTI บอกว่าคนต่างกันในหลายมิติ — 3 มิติที่เห็นได้จากวิธีพิมพ์ข้อความเดียว:
  รับข้อมูล   S (รายละเอียด ตัวเลข ขั้นตอน "ทำยังไง")      ↔ N (ภาพใหญ่ ความหมาย "ทำไม" "ถ้า…จะเป็นยังไง")
  ตัดสินใจ    T (เหตุผล ข้อดีข้อเสีย ความยุติธรรม)          ↔ F (ความรู้สึก คนรอบตัว คุณค่า)
  วิถีชีวิต    J (อยากได้ข้อสรุป แผน เส้นตาย "ควรเลือกอะไร") ↔ P (ยังสำรวจ เปิดทางไว้ "มีทางไหนบ้าง")
มิติ E/I (พลังจากคนอื่นหรือจากตัวเอง) เดาจากข้อความสั้นไม่ได้ จึงไม่ใช้

หลักที่ใช้:
- ไม่บอกผู้ใช้ว่าเขาเป็นไทป์อะไร และไม่เก็บเป็นโปรไฟล์ — อ่านเฉพาะข้อความตรงหน้า เพราะคนเดียวกันตอนเครียดกับตอนปกติเขียนต่างกัน
- สัญญาณอ่อนหรือขัดกัน = ไม่ปรับ (None) ดีกว่าปรับผิด
- เรื่องวิกฤตไม่ปรับเลย — ความปลอดภัยมาก่อนความเข้ากับสไตล์
- ข้อเท็จจริงและขั้นตอนไม่เปลี่ยนตามคน เปลี่ยนแค่ลำดับ จุดเน้น และวิธีปิดท้าย
"""
from __future__ import annotations

import re

_I = re.I

# ── สัญญาณ (ไทย + อังกฤษ) ─────────────────────────────────────────────────
_S = re.compile(r"ทำยังไง|ขั้นตอน|ต้องทำอะไรบ้าง|เริ่มยังไง|กี่บาท|กี่วัน|เท่าไร|เท่าไหร่|รายละเอียด|ยกตัวอย่าง|แบบไหนบ้าง|"
                r"\d[\d,]*\s?(?:บาท|เดือน|วัน|ปี|%)|"
                r"\bhow (?:do|can|should) I\b|\bstep[- ]by[- ]step\b|\bwhat exactly\b|\bhow much\b|\bhow many\b|\bdetails?\b|\bexample\b", _I)
_N = re.compile(r"ทำไม|เพราะอะไร|หมายความว่า|ความหมาย|ภาพรวม|ภาพใหญ่|ระยะยาว|อนาคต|ถ้า[^\n]{0,20}?จะเป็นยังไง|แก่นของ|ต้นเหตุ|"
                r"\bwhy\b|\bwhat does it mean\b|\bbig picture\b|\blong[- ]term\b|\bfuture\b|\bwhat if\b|\broot cause\b|\bmeaning\b", _I)
_T = re.compile(r"ข้อดีข้อเสีย|เหตุผล|คุ้มไหม|คุ้มมั้ย|คุ้มกว่า|เปรียบเทียบ(?:ข้อดี|ระหว่าง|ให้หน่อย)|วิเคราะห์|มีหลักฐาน|ตามหลัก|ยุติธรรม|ถูกหรือผิด|ตรงๆ|ไม่ต้องปลอบ|"
                r"\bpros and cons\b|\blogic(?:al)?\b|\bworth it\b|\bcompare\b|\banaly[sz]e\b|\bobjectively\b|\bbe honest\b|\bdon'?t sugarcoat\b|\bfair\b", _I)
# นับเฉพาะคำที่บอกอารมณ์ชัด — "กลัวเสียเวลา" คือความลังเล ไม่ใช่คนที่อยากให้ฟังก่อน · "เจ็บหลัง" คือร่างกาย
_F = re.compile(r"รู้สึก(?:แย่|ผิด|เหงา|โดดเดี่ยว|ไร้ค่า|เจ็บ|เสียใจ|หมดหวัง|ท้อ|หนัก|พัง)|เสียใจ|เจ็บ(?:ใจ|ปวด|มาก)|เหงา|กลัวมาก|ร้องไห้|"
                r"ใจ(?:สลาย|หาย|พัง)|ผิดหวัง|น้อยใจ|ทำร้ายจิตใจ|ไม่มีใครเข้าใจ|รักเขา(?:มาก)?|"
                r"\bi feel\b|\bfeel(?:ing)? (?:so )?(?:hurt|lonely|sad|lost|scared|guilty)\b|\bheartbroken\b|\bcry(?:ing)?\b|\bhurts\b|\bworried about (?:him|her|them)\b", _I)
_J = re.compile(r"ควร(?:เลือก|ทำ)อะไร|เลือกอะไรดี|เอาไงดี|ตัดสินใจ|สรุป(?:ว่า)?|ต้องรู้ภายใน|ภายใน(?:วันนี้|พรุ่งนี้|สัปดาห์)|เส้นตาย|ด่วน|แผน|"
                r"\bwhich (?:one|should I)\b|\bshould I\b|\bdecide\b|\bdeadline\b|\bby (?:tomorrow|friday|next week)\b|\bplan\b|\bjust tell me\b", _I)
_P = re.compile(r"มีทางไหนบ้าง|มีทางเลือกอะไร|ยังไม่แน่ใจ|ลังเล|คิดไปเรื่อยๆ|อยากลองหลายอย่าง|เปิดใจ|ไม่รีบ|ค่อยๆ คิด|"
                r"\bwhat are (?:my|the) options\b|\bnot sure yet\b|\bexploring\b|\bkeep (?:my )?options open\b|\bno rush\b|\bbrainstorm\b", _I)

_CRISIS = re.compile(r"อยากตาย|ไม่อยากอยู่|ฆ่าตัว|จบชีวิต|ทำร้ายตัวเอง|กรีด|\bkill myself\b|\bsuicid\w*\b|\bend (?:it all|my life)\b|\bself[- ]harm\b", _I)


def _side(a: re.Pattern, b: re.Pattern, text: str):
    """คืน (ตัวอักษรฝั่งที่ชนะ, จำนวนสัญญาณ) — เท่ากันหรือไม่มีเลย = None"""
    na, nb = len(a.findall(text)), len(b.findall(text))
    if na == nb:
        return None
    return na > nb


def read(text: str) -> dict:
    """อ่านความต้องการจากข้อความเดียว → {"info": "S"|"N"|None, "decide": "T"|"F"|None, "life": "J"|"P"|None}
    ไม่ใช่ไทป์ของคน — คือสิ่งที่ข้อความนี้ขอ ณ ตอนนี้"""
    t = str(text or "")
    if not t.strip() or _CRISIS.search(t):
        return {"info": None, "decide": None, "life": None}
    out = {}
    for key, (a, b, la, lb) in {"info": (_S, _N, "S", "N"), "decide": (_T, _F, "T", "F"), "life": (_J, _P, "J", "P")}.items():
        s = _side(a, b, t)
        out[key] = None if s is None else (la if s else lb)
    # เล่ายาวและมีความรู้สึก แม้ไม่ได้ใช้คำว่า "รู้สึก" — คนเล่ายาวส่วนมากอยากให้ฟังก่อน
    if out["decide"] is None and len(t) > 160 and _F.search(t):
        out["decide"] = "F"
    return out


# ── ปรับคำตอบจากสมการ (ไม่มี AI) ────────────────────────────────────────────
_ACK_TH = "ฟังแล้วรู้สึกได้ว่าเรื่องนี้หนักกับใจคุณจริงๆ — ขอเรียงทางให้ทีละขั้นนะ"
_ACK_EN = "That sounds genuinely heavy — let's take it one step at a time."
_DECIDE_TH = "ถ้าต้องเลือกทำแค่ข้อเดียวภายในสัปดาห์นี้ ข้อไหนที่ทำแล้วเปลี่ยนสถานการณ์มากที่สุด?"
_DECIDE_EN = "If you could do only one of these this week, which would change things most?"


def adapt_main(main: dict, reading: dict, lang: str = "th") -> dict:
    """ปรับ dict คำตอบ (open · paths · ask · vega) ตามที่อ่านได้ — ข้อเท็จจริงและขั้นตอนเหมือนเดิม
    F: รับความรู้สึกก่อน · T/N: ใส่มุมโครงสร้าง (vega) ต่อจากประโยคเปิด · J: ปิดด้วยการเลือกข้อแรก · S/P: คงตามเดิม (ขั้นตอนจับต้องได้และทางยังเปิดอยู่แล้ว)"""
    if not isinstance(main, dict) or not main.get("open"):
        return main
    m = dict(main)
    open_ = m["open"][0]
    if reading.get("decide") == "F":
        open_ = (_ACK_EN if lang == "en" else _ACK_TH) + "\n\n" + open_
    elif (reading.get("decide") == "T" or reading.get("info") == "N") and m.get("vega") and m["vega"] not in open_:
        open_ = open_ + "\n\n" + ("In short: " if lang == "en" else "สรุปเชิงเหตุผล: ") + m["vega"]
    m["open"] = [open_]
    if reading.get("life") == "J":
        m["ask"] = _DECIDE_EN if lang == "en" else _DECIDE_TH
    return m


# ── คำใบ้ให้ AI (LYLA/VEGA) ─────────────────────────────────────────────────
_HINT = {
    "S": "ผู้ใช้อยากได้รายละเอียดที่จับต้องได้: ขั้นตอน ตัวเลข ตัวอย่าง — อย่าตอบเป็นหลักการลอยๆ",
    "N": "ผู้ใช้อยากเห็นภาพใหญ่และเหตุผลเบื้องหลัง: บอกแก่นและ 'ทำไม' ก่อน แล้วค่อยลงรายละเอียด",
    "T": "ผู้ใช้อยากได้การวิเคราะห์ตรงไปตรงมา: ข้อดีข้อเสีย ตัวแปรที่ตัดสิน — ไม่ต้องปลอบยาว",
    "F": "ผู้ใช้กำลังใช้ใจเล่า: รับความรู้สึกให้ชัดก่อนหนึ่งประโยค พูดถึงคนที่เกี่ยวข้อง แล้วค่อยให้ทาง",
    "J": "ผู้ใช้อยากได้ข้อสรุป: บอกให้ชัดว่าควรทำอะไรก่อน ปิดด้วยก้าวแรกที่เจาะจง",
    "P": "ผู้ใช้ยังสำรวจอยู่: เสนอทางเลือกที่ยังเปิดได้ ไม่ต้องรีบสรุปแทนเขา",
}


def llm_hint(reading: dict) -> str:
    """คำใบ้ภายในสำหรับ prompt — บอกวิธีตอบ ไม่ใช่บอกว่าผู้ใช้เป็นใคร (ห้ามพูดถึงไทป์หรือคำใบ้นี้กับผู้ใช้)"""
    lines = [_HINT[v] for v in (reading.get("info"), reading.get("decide"), reading.get("life")) if v]
    if not lines:
        return ""
    return "[วิธีตอบให้เข้ากับคนนี้ — ห้ามบอกผู้ใช้ว่าอ่านแบบนี้ และห้ามพูดถึงบุคลิกหรือไทป์]\n" + "\n".join("· " + x for x in lines)
