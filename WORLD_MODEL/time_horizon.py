"""WORLD_MODEL/time_horizon.py — ผลระยะสั้นกับระยะยาวขัดกันไหม (ให้เสียง COSMOS)

ดูว่าผู้ใช้กำลังมองระยะไหน (วันนี้ · เดือนนี้ · ปีหน้า · หลายปี) แล้วชวนมองอีกระยะที่ยังไม่ได้มอง
"""
import re

_SHORT = re.compile(r"วันนี้|คืนนี้|พรุ่งนี้|ตอนนี้|ด่วน|เดือนนี้|สิ้นเดือน|\b(?:today|tonight|tomorrow|right now|this month)\b", re.I)
_LONG = re.compile(r"(?:อีก|ใน)\s*\d+\s*ปี|ระยะยาว|อนาคต|เกษียณ|ตอนแก่|\b(?:long[- ]term|in \d+ years|retire\w*|future)\b", re.I)


def horizon(text) -> str:
    t = str(text or "")
    s, l = bool(_SHORT.search(t)), bool(_LONG.search(t))
    return "both" if s and l else "short" if s else "long" if l else "unspecified"


def prompt(text) -> str:
    """คำถามให้มองอีกระยะที่ยังไม่ได้มอง"""
    h = horizon(text)
    if h == "short":
        return "คุณกำลังมองแค่ช่วงนี้ — ลองถามว่าอีก 3 ปี ทางนี้พาไปอยู่ตรงไหน และยังมีทางถอยไหม"
    if h == "long":
        return "ภาพระยะยาวสำคัญ แต่ต้องรอดช่วงแรกให้ได้ก่อน — 6 เดือนแรกเงินและแรงพอไหม"
    return "ลองมอง 2 ระยะ: 6 เดือนแรกรอดไหม และ 3 ปีข้างหน้าทางนี้ยังเป็นทางที่อยากอยู่ไหม"
