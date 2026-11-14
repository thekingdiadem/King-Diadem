"""
core/human_protocol.py — HUMAN PROTOCOL (ENFORCED): ตรวจคำตอบของ AI ว่าคืนทางเลือกจริง ไม่ใช่แค่สั่ง

ที่มา: AI/HUMAN_PROTOCOL.py ของเจ้าของโปรเจกต์ (เม.ย. 2026) — "Choice(t) must always be > 0 ·
ทุกคำตอบต้องมีอย่างน้อย 2 ทางเลือก · ทางสำรองที่ปลอดภัย · ไม่สรุปแทนผู้ใช้ · รักษาการถอยกลับได้"
ไฟล์เดิมเป็นข้อความ markdown ที่ตั้งชื่อ .py จึงไม่เคยถูกรัน และหายไปจาก branch หลักแล้ว
หลักนี้ถูกสั่งไว้ใน prompt (KD_DNA) แล้ว แต่ "สั่ง" ไม่เท่ากับ "บังคับใช้" — ไฟล์นี้คือตัวตรวจหลังคำตอบ

และเป็นการใช้สมการของเจ้าของโปรเจกต์: Wisdom = Outcome Usefully / Spent Energy
คำตอบยาวที่ไม่มีทางให้เลือกเลย ใช้แรงของผู้อ่านเยอะแต่ได้ผลที่ใช้ได้น้อย

ทำอะไร:
1. นับทางเลือกในคำตอบ (ข้อที่ขึ้นต้นด้วยเลข/ขีด/จุด หรือคำว่า "ทางที่/ทางเลือก/Option")
2. หาประโยคที่สรุปแทนผู้ใช้ ("ทางเดียวคือ" "ไม่มีทางอื่น" "ต้อง…เท่านั้น" "you have no choice")
3. ถ้าทางเลือก < 2 หรือสรุปแทน และเรื่องนี้มีเลนส์ปัญหารองรับ → เติม "ทางที่ยังเปิดอยู่" จากเลนส์
   ไม่มีเลนส์ → ไม่เติมอะไรเดาๆ แต่ส่งผลการตรวจกลับไปให้นับเป็นสถิติ
ไม่แตะ: เรื่องวิกฤต/ด่วน/เสี่ยงสูง (ขั้นตอนปลอดภัยต้องมาก่อนทางเลือก) · คำทักทายหรือคำถามสั้นที่ไม่ได้ขอให้ตัดสินใจ
"""
from __future__ import annotations

import re

_I = re.I

_ITEM = re.compile(r"^\s*(?:\d{1,2}[).]|[-•·▸◦*]|ข้อ\s?\d|ทาง(?:ที่|เลือกที่)\s?\d|(?:option|choice)\s?[a-c1-3][:.)]?)\s+\S", _I | re.M)
_INLINE = re.compile(r"ทาง(?:แรก|ที่สอง|ที่สาม|เลือกแรก)|อีกทาง(?:หนึ่ง)?คือ|หรือจะ|\boption (?:a|b|1|2)\b|\balternatively\b|\banother option\b", _I)
_FORCED = re.compile(r"ทางเดียว(?:ที่ทำได้)?คือ|ไม่มีทางอื่น|ไม่มีทางเลือก(?:อื่น)?|ต้อง[^\n]{0,30}?เท่านั้น|ห้ามทำอย่างอื่น|"
                     r"\b(?:the only (?:option|way|choice) is|you have no (?:other )?choice|there is no other (?:option|way)|you must only)\b", _I)
# ผู้ใช้ไม่ได้ขอให้ช่วยตัดสินใจหรือแก้ปัญหา — ไม่ต้องบังคับให้มีทางเลือก
_SIGN = re.compile(r"\n\s*— (?:LYLA|VEGA|สภา KING DIADEM)[^\n]*(?:\n[^\n]*)?\s*$")
_NOT_A_PROBLEM = re.compile(r"^\s*(?:สวัสดี|หวัดดี|ขอบคุณ|ขอบใจ|ฝันดี|hi|hello|hey|thanks|thank you)\b", _I)


# เลนส์ที่ไม่ใช่เรื่องตัดสินใจ: "i got the job!!" เคยถูกเติม "Options you still have:" ต่อท้ายคำยินดี
_NOT_A_DECISION = {"good_news_en", "birthday", "anyone_there", "short_tired", "why_me", "pet_died"}


def options_in(reply: str) -> int:
    """จำนวนทางเลือกที่เห็นในคำตอบ (ข้อรายการ + ทางเลือกที่เขียนในประโยค)"""
    t = str(reply or "")
    return max(len(_ITEM.findall(t)), len(_INLINE.findall(t)))     # ไม่นับซ้ำ "- ทางแรก" เป็นสองทาง


def forced(reply: str) -> bool:
    return bool(_FORCED.search(str(reply or "")))


def audit(reply: str) -> dict:
    """ผลตรวจ: {"options": n, "forced": bool, "ok": bool}"""
    n, f = options_in(reply), forced(reply)
    return {"options": n, "forced": f, "ok": n >= 2 and not f}


def enforce(user_text: str, reply: str, lang: str = "th", urgent: bool = False):
    """คืน (คำตอบ, ผลตรวจ) — เติมทางเลือกจากเลนส์ปัญหาเมื่อคำตอบไม่คืนทางเลือก"""
    a = audit(reply)
    a["patched"] = False
    # applies = เรื่องนี้ควรมีทางเลือกไหม (ไม่ใช่วิกฤต ไม่ใช่คำทักทาย) — ใช้แยกสถิติ ไม่ให้คำทักทายนับเป็น "ไม่คืนทางเลือก"
    a["applies"] = not (urgent or not reply or _NOT_A_PROBLEM.search(str(user_text or "")) or len(str(user_text or "").strip()) < 8)
    if not a["applies"] or a["ok"]:
        return reply, a
    try:
        from core import problem_lens
        lz = problem_lens.find(user_text, "en" if lang == "en" else "th")
    except Exception:
        lz = None
    if not lz or not lz.get("paths"):
        return reply, a                       # ไม่เดา — ให้ผู้เรียกนับเป็นสถิติ
    if lz.get("key") in _NOT_A_DECISION:     # ข่าวดี คำทัก ความรู้สึกสั้นๆ — ไม่ต้องยื่นทางเลือกให้
        a["applies"] = False
        return reply, a
    head = "Options you still have:" if lang == "en" else "ทางที่ยังเปิดอยู่:"
    tail = "The choice is yours." if lang == "en" else "คุณเป็นคนเลือกเสมอ"
    extra = f"\n\n{head}\n" + "\n".join(f"{i + 1}) {p}" for i, p in enumerate(lz["paths"][:3])) + f"\n{tail}"
    a["patched"] = True
    body = str(reply).rstrip()
    m = _SIGN.search(body)                    # ใส่ก่อนลายเซ็น "— LYLA ◈" ไม่ใช่ต่อท้ายลายเซ็น
    if m:
        return body[:m.start()].rstrip() + extra + "\n\n" + body[m.start():].lstrip(), a
    return body + extra, a
