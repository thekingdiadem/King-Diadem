"""WORLD_MODEL/pause_point.py — จุดพักก่อนลงมือ (วัดได้ ไม่ใช้ AI · ข้อความเดิมได้ผลเดิม)

ความพังส่วนใหญ่ไม่ได้เริ่มจากเรื่องใหญ่ แต่เริ่มจาก "ความรู้สึกแรงๆ ที่กลายเป็นการกระทำทันที"
ห่วงโซ่ที่อ่านจากข้อความ (เรียงจากต้นไปปลาย — ดู docs/PAUSE_POINT.md):
  เรื่องที่มากระทบ → ความรู้สึกแรก → แรงอยากทำทันที → คำเด็ดขาด → บทบาทที่สวม → การกระทำที่ย้อนกลับยาก

จุดตัดที่ได้ผลที่สุด = ระหว่าง "ความรู้สึก" กับ "แรงอยากทำทันที"
ถ้ามีทั้งสองอย่าง และกำลังจะลงมือ/ยึดคำเด็ดขาด/สวมบทบาท → ชวนพักตามเวลาที่วัดได้ แล้วกลับไปดูข้อเท็จจริง

ทุกค่าเป็นจำนวนเต็ม 0–3 (นับจากคำที่เจอ ตัดที่ 3) — อธิบายได้ ตรวจย้อนได้ ไม่มีสุ่ม
ไม่ตัดสินแทน ไม่เทศนา ไม่ใช้ศัพท์ทางศาสนา
"""
from __future__ import annotations

import re
from typing import NamedTuple

# ── ความรู้สึก (แยกโทน: ไม่สบายใจ / ตื่นเต้นอยากได้ — ทั้งสองแบบผลักให้รีบได้เท่ากัน) ───────────────
_UNPLEASANT = re.compile(
    r"โกรธ|โมโห|หัวร้อน|ของขึ้น|แค้น|เจ็บใจ|เจ็บปวด|น้อยใจ|เสียใจมาก|อับอาย|อายมาก|ขายหน้า|กลัวมาก|ตื่นตระหนก|แพนิค|"
    r"ทนไม่ไหว|ทนไม่ได้|เกลียด|รับไม่ได้|ผิดหวังมาก|"
    r"\b(?:furious|angry|enraged|humiliated|panick?(?:ed|ing)?|terrified|hate|devastated|can'?t stand|so hurt)\b", re.I)
_PLEASANT = re.compile(
    r"ตื่นเต้นมาก|ดีใจสุด|กลัวตกรถ|โอกาสทอง|ห้ามพลาด|รวยแน่|ปังแน่|"
    r"\b(?:fomo|so excited|once in a lifetime|can'?t miss|guaranteed win|to the moon)\b", re.I)
_INTENSE = re.compile(r"มาก|สุดๆ|ที่สุด|สุดจะ|จนตัวสั่น|จนนอนไม่หลับ|\b(?:so|extremely|really really)\b", re.I)

# ── แรงอยากทำทันที ────────────────────────────────────────────────────────────────────────
_URGE = re.compile(
    r"ทันที|เดี๋ยวนี้|ตอนนี้เลย|คืนนี้(?:เลย)?|วันนี้เลย|รีบ|ก่อนจะสาย|ให้มันรู้|เอาคืน|แก้แค้น|ตอบกลับ(?:ไป)?เลย|"
    r"ขายหมด|เทขาย|ทุ่มหมด|ทุ่มเลย|ไม่รอแล้ว|"
    r"\b(?:right now|immediately|tonight|asap|can'?t wait|get back at|get even|dump (?:it|everything)|go all in)\b", re.I)

# ── คำเด็ดขาด (มองเห็นทางเดียว) ─────────────────────────────────────────────────────────────
_FIXED = re.compile(
    r"ต้อง\S{0,12}ให้ได้|ยอมไม่ได้|ไม่มีทางอื่น|ไม่มีทางเลือก|มีทางเดียว|ทุกครั้ง|ไม่เคย\S{0,6}เลย|ตลอดเวลา|"
    r"\b(?:no other way|only option|always|never ever|must)\b", re.I)

# ── บทบาทที่กำลังจะสวม ─────────────────────────────────────────────────────────────────────
_ROLES = (
    ("ผู้แพ้", "victim", re.compile(r"ฉันมัน(?:ไม่มีค่า|โง่|แย่|ไร้ค่า|ล้มเหลว)|ผมมัน(?:ไม่มีค่า|โง่|แย่|ไร้ค่า|ล้มเหลว)|ทำไมต้องเป็น(?:ฉัน|ผม|เรา)|"
                                    r"\b(?:i'?m (?:worthless|a failure|so stupid)|why (?:always )?me)\b", re.I)),
    ("ผู้ต้องชนะ", "fighter", re.compile(r"ต้องชนะ|ให้มันรู้ว่าใคร|ไม่ยอมแพ้ใคร|ไม่ยอมให้ใครมา|ต้องได้คืน|ต้องเอาคืน|"
                                         r"\b(?:show (?:him|her|them) who|i (?:have|need) to win|teach (?:him|her|them) a lesson)\b", re.I)),
)

# ── การกระทำที่กำลังจะทำ (แยกแบบที่คนอื่นเห็นทันที เพราะย้อนกลับยากเป็นพิเศษ) ───────────────────────
_PUBLIC = re.compile(r"โพสต์|ประจาน|แฉ|ส่งข้อความ|ทักไป|โทรไปด่า|อัดคลิป|ไลฟ์|"
                     r"\b(?:post(?:ing)?|expose|text (?:him|her|them)|send (?:a |the )?(?:text|message|email)|call (?:him|her|them) out)\b", re.I)
_ACT = re.compile(r"บอกเลิก|ลาออก|ขาย(?!หน้า)|โอน|ลงทุน|กู้|เซ็น|ย้าย|ตัดขาด|บล็อก|"
                  r"\b(?:quit|resign|sell|transfer|invest|sign|break up|cut (?:him|her|them) off|block)\b", re.I)

# ผู้ใช้เป็นคนจะทำเอง ("แฟนบอกเลิก" = เขาทำ ไม่ใช่เรากำลังจะลงมือ)
_INTENT = re.compile(r"จะ|อยาก|กำลัง|ขอ|คิดจะ|ตัดสินใจ|\b(?:i'?ll|i will|going to|gonna|want to|about to|should i)\b", re.I)

# ── หลักฐานกับการเดา ──────────────────────────────────────────────────────────────────────
_FACT = re.compile(r"\d|เห็นเอง|ได้ยินเอง|มีหลักฐาน|มีเอกสาร|สลิป|ใบเสร็จ|สัญญา|\b(?:receipt|contract|evidence|i saw)\b", re.I)
_GUESS = re.compile(r"คิดว่า|น่าจะ|คงจะ|ได้ยินมา|เขาว่า|เขาลือ|ดูเหมือน|รู้สึกว่าเขา|เดาว่า|"
                    r"\b(?:i think|probably|i guess|people say|i heard|seems like|must be)\b", re.I)

QUESTIONS = (
    "ข้อเท็จจริงที่ยืนยันได้มีอะไรบ้าง และส่วนไหนที่ยังเดาอยู่?",
    "ตอนนี้รู้สึกอะไร ถ้าให้คะแนน 0–10 แรงแค่ไหน?",
    "ลึกๆ อยากได้อะไร หรืออยากหนีอะไร?",
    "ถ้าทำแบบนี้ เราจะกลายเป็นคนแบบไหนในเรื่องนี้?",
    "ถ้าความรู้สึกนี้เบาลงครึ่งหนึ่ง ยังอยากทำแบบเดิมไหม?",
)
QUESTIONS_EN = (
    "Which facts can you actually confirm, and which parts are still guesses?",
    "What are you feeling right now, and how strong is it from 0 to 10?",
    "What do you really want to get, or to get away from?",
    "If you do this, who do you become in this story?",
    "If this feeling were half as strong, would you still do the same thing?",
)


class Pause(NamedTuple):
    tone: str          # unpleasant · pleasant · neutral
    feeling: int       # 0–3
    urge: int          # 0–3
    fixed: int         # 0–3 คำเด็ดขาด
    role: str          # "" · ผู้แพ้ · ผู้ต้องชนะ
    acting: str        # "" · public (คนอื่นเห็นทันที) · lock (ย้อนกลับยาก) · act
    guess_only: bool   # มีแต่การเดา ไม่มีข้อเท็จจริงเลย
    stage: int         # ไปถึงขั้นไหนของห่วงโซ่ (0 = ไม่เห็น · 1 ความรู้สึก … 5 กำลังลงมือ)
    pause: bool        # ควรพักก่อนลงมือไหม
    wait_min: int      # พักกี่นาที (0 = ไม่ต้อง)

    def wait_th(self) -> str:
        return {1440: "24 ชั่วโมง", 60: "1 ชั่วโมง", 10: "10 นาที"}.get(self.wait_min, "")

    def wait_en(self) -> str:
        return {1440: "24 hours", 60: "1 hour", 10: "10 minutes"}.get(self.wait_min, "")

    def note(self) -> str:
        """บริบทสั้นให้ AI — เฉพาะตอนที่ควรพัก (ไม่ควรพัก = ไม่ส่งอะไร)"""
        if not self.pause:
            return ""
        tone = {"unpleasant": "ไม่สบายใจ", "pleasant": "ตื่นเต้นอยากได้"}.get(self.tone, "กลาง")
        bits = [f"ความรู้สึกแรง={self.feeling}/3({tone})", f"อยากทำทันที={self.urge}/3"]
        if self.fixed:
            bits.append(f"คำเด็ดขาด={self.fixed}/3")
        if self.role:
            bits.append("บทบาทที่กำลังสวม=" + self.role)
        if self.acting:
            bits.append({"public": "จะทำสิ่งที่คนอื่นเห็นทันที", "lock": "จะทำสิ่งที่ย้อนกลับยาก", "act": "กำลังจะลงมือ"}[self.acting])
        if self.guess_only:
            bits.append("ยังมีแต่การเดา ไม่มีข้อเท็จจริง")
        return ("[จุดพักก่อนลงมือ: " + " · ".join(bits) + f" — ชวนพัก {self.wait_th()} ก่อนลงมือ "
                "(เขียนไว้ได้แต่ยังไม่ส่ง/ยังไม่ทำ) แล้วถามข้อเท็จจริงทีละข้อ · ยอมรับความรู้สึกก่อน ไม่ตัดสินแทน ไม่เทศนา ไม่ใช้ศัพท์ทางศาสนา]")


def _count(rx, t) -> int:
    return min(3, len(rx.findall(t)))


def read(text) -> Pause:
    from WORLD_MODEL.reversibility import locks
    t = str(text or "")
    un, pl = _count(_UNPLEASANT, t), _count(_PLEASANT, t)
    tone = "unpleasant" if un >= pl and un else "pleasant" if pl else "neutral"
    feeling = min(3, max(un, pl) + (1 if (un or pl) and _INTENSE.search(t) else 0))
    urge = _count(_URGE, t)
    fixed = _count(_FIXED, t)
    role = next((th for th, _k, rx in _ROLES if rx.search(t)), "")
    acting = ""
    if _INTENT.search(t):
        acting = "public" if _PUBLIC.search(t) else "lock" if locks(t) else "act" if _ACT.search(t) else ""
    guess_only = bool(_GUESS.search(t)) and not _FACT.search(t)
    stage = 5 if acting and (feeling or urge) else 4 if role else 3 if fixed and (feeling or urge) else 2 if urge else 1 if feeling else 0
    # จุดตัด: มีความรู้สึก + แรงอยากทำทันที และเรื่องกำลังเดินต่อ (ลงมือ/คำเด็ดขาด/บทบาท)
    pause = bool((feeling or role) and urge and (acting or fixed or role))   # "ฉันมันโง่" ก็คือความรู้สึกแรงแบบหนึ่ง
    wait = (1440 if acting == "lock" else 60 if acting == "public" else 10) if pause else 0
    return Pause(tone, feeling, urge, fixed, role, acting, guess_only, stage, pause, wait)
