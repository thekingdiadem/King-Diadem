"""WORLD_MODEL/consequences.py — ผลลำดับสองและสาม: ใครได้รับผล และเมื่อไหร่ (ให้เสียง CIVIL · COSMOS)

ผลลำดับแรกคือสิ่งที่ผู้ใช้ตั้งใจ · ลำดับสองคือสิ่งที่ตามมา (คนในบ้าน งาน สุขภาพ ความสัมพันธ์)
ไม่เดาอนาคต — บอกแค่ว่า "ควรถามเรื่องนี้ก่อน" จากสิ่งที่เห็นในข้อความ
"""
import re
from typing import NamedTuple


class Ripple(NamedTuple):
    who: str
    th: str
    ask: str


_WHO = (
    ("children", r"ลูก(?!ค้า|น้อง|หนี้|จ้าง)|\b(?:kids?|children|son|daughter)\b", "ลูก", "ลูกต้องย้ายโรงเรียน เปลี่ยนคนดูแล หรือเสียค่าเรียนไหม ถ้าทางนี้พลาด?"),
    ("partner", r"แฟน|สามี|ภรรยา|คู่ชีวิต|\b(?:wife|husband|partner|spouse)\b", "คู่ชีวิต", "คู่ชีวิตรู้ตัวเลขทั้งหมดและเห็นด้วยไหม — เงินก้อนนี้เป็นของคุณคนเดียวหรือของทั้งคู่?"),
    ("parents", r"พ่อแม่|แม่(?!ค้า|น้ำ|บ้าน)|พ่อ(?!ค้า|บ้าน)|ยาย|ตา(?=\s|$)|\b(?:parents?|mom|mum|dad|grand(?:ma|pa|mother|father))\b", "พ่อแม่/ผู้สูงอายุ", "ถ้าพลาด คนที่ต้องดูแลพ่อแม่หรือผู้สูงอายุจะยังทำได้ไหม?"),
    ("employees", r"ลูกน้อง|พนักงาน(?:ใน)?ร้าน|จ้างคน|\b(?:employees?|staff|workers? i (?:hire|employ))\b", "ลูกจ้าง", "ถ้าต้องปิด ลูกจ้างได้ค่าชดเชยและรู้ล่วงหน้าแค่ไหน?"),
    ("health", r"สุขภาพ|โรคประจำตัว|นอนไม่หลับ|เครียดจน|\b(?:health|sleep|burn ?out|stress)\b", "สุขภาพของคุณ", "ทางนี้กินเวลาและแรงแค่ไหน และคุณจะรักษาการนอนกับสุขภาพไว้อย่างไร?"),
)
_RX = [(k, re.compile(rx, re.I), th, ask) for k, rx, th, ask in _WHO]


def ripples(text) -> list:
    t = str(text or "")
    return [Ripple(k, th, ask) for k, rx, th, ask in _RX if rx.search(t)]
