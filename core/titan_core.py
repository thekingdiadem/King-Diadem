"""TITAN CORE — Decision Core ที่อ่านจากเรื่องจริงของผู้ใช้ (Choice Preservation System)

ฟังก์ชัน TITAN ใน core/emptiness_guard.py (Section 2–10) มีครบแต่รับค่าเป็นธง/ตัวเลข — ไม่เคยทำงานกับคนจริง
ไฟล์นี้อ่านข้อความแล้วเรียกฟังก์ชันเดิม (ไม่เขียนสูตรซ้ำ):

  Section 3 Zero-Choice   food < MIN · water < MIN · shelter < MIN · exit == BLOCKED · O == 0
  Section 4 Minimal       ZERO_CHOICE → ให้เฉพาะขั้นที่คืนทางเลือก ≥ 1 แล้วถอย — ไม่ควบคุมต่อ ไม่เทศนา ไม่หวังคำขอบคุณ
  Section 6 Silence       CHOICE > 0 → TITAN ไม่พูดอะไร (ไม่เพิ่มคำเตือนหรือคำสั่งสอน)
  Section 5 Conservation  ขอเพิ่มอำนาจเหนือคนอื่นโดยลดทางเลือกของเขา = ไม่ช่วย แต่เสนอทางที่ทั้งสองฝ่ายยังเลือกได้
  Section 8 Anti-Capture  titan_anti_capture_check (ซ่อมแล้ว อ่านข้อความได้)

One-Line Canon: CHOICE > 0 : NO ACTION · CHOICE = 0 : MUST ACT (MINIMALLY)
"""
from __future__ import annotations

import re
from typing import NamedTuple

# ── exit == BLOCKED: ถูกขัง/กักตัว/ห้ามออก/ยึดเอกสารไม่ให้ไป (มุมของคนที่ถูกทำ) ─────────────────────────
EXIT_BLOCKED = re.compile(
    r"(?:ล็อก|ล๊อก|ปิด)(?:ประตู|ห้อง|บ้าน)\S{0,10}(?:ไม่ให้|ห้าม)\S{0,6}ออก|(?:ขัง|กักขัง|กักตัว|ล่าม|มัด)(?:ฉัน|หนู|ผม|เรา|ไว้|อยู่|เด็ก|ลูก|แม่|ภรรยา)|"
    r"(?:ถูก|โดน)(?:ขัง|กักขัง|กักตัว|ล่าม|ล็อก(?:ห้อง|ประตู)?)|ไม่ให้(?:ฉัน|หนู|ผม|เรา)?\s?ออก(?:จาก)?(?:บ้าน|ห้อง|ที่พัก|โรงงาน|แคมป์|หอ)|ห้าม(?:ฉัน|หนู|ผม|เรา)\S{0,4}ออก(?:จาก)?(?:บ้าน|ห้อง|ที่พัก)|"
    # ยึดเอกสารอย่างเดียวยังไม่ใช่ถูกขัง (คำตอบแรงงาน/ค้ามนุษย์ของเดิมตรงกว่า) — ต้องบอกว่าห้ามออก/ถูกขังด้วย
    r"(?i:\b(?:locked|locking) me (?:in|inside|up)\b|\bwon'?t let me (?:leave|out|go)\b|\b(?:took|takes|kept|keeps|holding|has) my passport\b|\bkeep(?:s|ing)? me locked\b|\bi'?m being held\b|\bnot allowed to leave (?:the )?(?:house|room|apartment|compound)\b)")
# ── Section 5: ขอวิธีเพิ่มอำนาจเหนือคนอื่น/ลดทางออกของเขา (มุมของคนที่จะทำ) ─────────────────────────────
_OTHER = r"(?:แฟน|สามี|ภรรยา|เมีย|ผัว|ลูกน้อง|ลูกจ้าง|พนักงาน|คนงาน|แรงงาน|ลูก|คู่)"
POWER_OVER = re.compile(
    r"(?:ทำยังไง|ทำอย่างไร|วิธี|อยาก|จะ|ช่วย)\S{0,6}(?:ให้|ไม่ให้)" + _OTHER + r"[^\n]{0,20}?(?:ไม่กล้า|ห้าม|ออกไม่ได้|ลาออกไม่ได้|เลิกไม่ได้|หนีไม่ได้|เชื่อฟัง|ไปทำที่อื่น|ลาออก|เลิกกับ|ทิ้ง)|"
    # ต้องมีคำบอกเจตนาของผู้ใช้เอง — "นายจ้างยึดพาสปอร์ตแรงงาน" คือการเล่าว่าคนอื่นทำ (ผู้ใช้อาจเป็นแรงงาน)
    r"(?<!นายจ้าง)(?:จะ|อยาก|ควร|ช่วย|ทำยังไง(?:ถึงจะ)?|วิธี)\S{0,4}ยึด(?:พาสปอร์ต|หนังสือเดินทาง|บัตร\S{0,6}|เอกสาร)\S{0,6}" + _OTHER + r"|"
    r"ยึด(?:พาสปอร์ต|หนังสือเดินทาง|เอกสาร)\S{0,6}" + _OTHER + r"\S{0,12}(?:ได้ไหม|ได้มั้ย|ผิดไหม|กันหนี)|"
    r"(?:แอบ)?(?:ติดตาม|ดัก|แอบดู|แอบอ่าน|ส่อง|ติดตั้งแอป\S{0,6}ใน)\S{0,4}(?:มือถือ|โทรศัพท์|ไลน์|แชท|ตำแหน่ง)\S{0,4}" + _OTHER + r"|"
    r"(?i:\bhow (?:can|do|to|should) (?:i )?(?:secretly )?(?:track|spy on|monitor|read|check) (?:my )?(?:wife|husband|girlfriend|boyfriend|partner|spouse|employee|teen)'?s? (?:phone|messages|texts|location|whatsapp)\b|"
    r"\b(?:make|force|stop|prevent|keep) (?:my )?(?:wife|husband|girlfriend|boyfriend|partner|employees?|workers?|staff) (?:from )?(?:leav\w+|quit\w*|obey\w*|afraid to leave)\b|"
    r"\b(?:keep|hold|take|confiscate) (?:my )?(?:workers?|employees?|maid|helper)'?s? passports?\b)")
# ── O == 0: บอกเองว่าไม่เหลือทางเลือก ───────────────────────────────────────────────────────────────
NO_OPTION = re.compile(r"หมดทาง(?:เลือก|ออก|ไป|สู้)|ไม่มีทาง(?:ออก|ไป|เลือก|รอด)(?:แล้ว|อีกแล้ว)?|ทางตัน|ไม่เหลือทางเลือก|"
                       r"\b(?:no way out|no options? left|no choice left|out of options|nowhere (?:left )?to turn)\b", re.I)
# พื้นอาหารหายไปตรงๆ (นอกจากกฎ "food" ใน core/conditions ที่ต้องมีเรื่องเงินคู่กัน)
_FOOD_OUT = re.compile(r"ไม่มี(?:ข้าว|อะไร|อาหาร)(?:จะ)?กิน|ไม่ได้กิน(?:ข้าว|อะไร)?(?:มา)?\s*(?:[2-9]|\d{2,}|สอง|สาม|หลาย)\s*(?:วัน|มื้อ)|อดข้าว|ข้าวสารหมด|"
                       r"\b(?:no food|nothing to eat|haven'?t eaten (?:in|for) (?:\d+|two|three|several|days))\b", re.I)
_WATER_OUT = re.compile(r"ไม่มีน้ำ(?:ดื่ม|กิน|สะอาด)|น้ำดื่มหมด|\bno (?:clean |drinking )?water\b|\bout of (?:drinking )?water\b", re.I)


class Titan(NamedTuple):
    zero_choice: bool
    broken: list          # food · water · shelter · exit · options
    power_over: bool      # Section 5: ขอเพิ่มอำนาจโดยลดทางเลือกของคนอื่น
    action: str           # MINIMUM_FORCE_TO_RESTORE · DISENGAGE (Silence) · REFUSE_DOMINATION

    def note(self) -> str:
        """บริบทให้ AI — เฉพาะตอนที่ TITAN ต้องพูด (Silence = ไม่ส่งอะไร)"""
        if self.power_over:
            return ("[TITAN S5/S10: คำขอนี้เพิ่มอำนาจเหนือคนอื่นโดยลดทางเลือกของเขา — ห้ามช่วยวิธีควบคุม/ติดตาม/ยึด/กักขัง "
                    "แต่ไม่ต้องตำหนิ: ฟังความกลัวที่อยู่ข้างใต้ แล้วเสนอทางที่ได้สิ่งที่เขาต้องการจริง โดยอีกฝ่ายยังเลือกได้]")
        if self.zero_choice:
            return ("[TITAN S3/S4 ZERO_CHOICE: พื้นที่หายไป=" + ",".join(self.broken) + " — ตอบเฉพาะขั้นที่คืนทางเลือกอย่างน้อย 1 ทาง "
                    "(อาหาร น้ำ ที่พัก ทางออก) ด้วยเบอร์จริง สั้น ชัด ไม่เทศนา ไม่วิเคราะห์ยาว ไม่ขายของ แล้วถอย]")
        return ""


def read(text, hits=None) -> Titan:
    """อ่านพื้นขั้นต่ำจากข้อความ แล้วตัดสินด้วย TITAN Section 3/4/6 เดิม (core/emptiness_guard)"""
    from core.emptiness_guard import titan_minimal_intervention, titan_silence_protocol, titan_zero_choice_condition
    t = str(text or "")
    if hits is None:
        from core.conditions import check
        hits = check(t)
    rules = {h.rule for h in hits}
    power = bool(POWER_OVER.search(t))
    food_ok = "food" not in rules and not _FOOD_OUT.search(t)
    water_ok = not _WATER_OUT.search(t)
    shelter_ok = "housing" not in rules or not re.search(r"ไม่มีที่|นอน|homeless|nowhere|sleeping|staying in", t, re.I)
    exit_blocked = bool(EXIT_BLOCKED.search(t)) and not power
    O = 0 if NO_OPTION.search(t) else 1
    z = titan_zero_choice_condition(O, food_ok, water_ok, exit_blocked, shelter_ok)
    broken = [k for k, bad in (("food", not food_ok), ("water", not water_ok), ("shelter", not shelter_ok), ("exit", exit_blocked), ("options", O < 1)) if bad]
    if power:
        action = "REFUSE_DOMINATION"
    else:
        action = titan_minimal_intervention(z["zero_choice"])["action"] if z["zero_choice"] else titan_silence_protocol(O)["action"]
    return Titan(z["zero_choice"], broken, power, action)
