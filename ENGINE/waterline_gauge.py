"""Waterline gauge — วัดจริงว่าอยู่เหนือหรือใต้เส้น (ใช้ในโหมด DriftZero)

นิยามของเจ้าของโปรเจกต์ (3 ความหมายในเส้นเดียว):
  1) เส้นวัดสภาวะจม/รอด (Survivability Level) — ตัวแปรหลัก (ทรัพยากร · Drift · ทางเลือกที่เหลือ)
     ยัง "เหนือระดับน้ำ" (Above Water / Stable) หรือกำลังจม "ใต้ระดับน้ำ" (Below Water / Risk Critical)
  2) เส้นควบคุมแรงเหวี่ยง (Drift Zero Reference) — บอกว่าต้องดึงความเสี่ยงกลับตรงไหน ก่อนความเสียหาย
     ลุกลามจนสายเกินแก้ → ถ้าจะหลุดเส้น = Stop-the-Line Trigger
  3) เกราะป้องกันการพังทลาย (L0 Axiom) — ขอบล่างสุด ต่อให้ผันผวนแค่ไหนก็ห้ามต่ำกว่าเส้นนี้เด็ดขาด

อ่านตัวเลขจากข้อความ (ไม่ใช้ AI · ไม่เดา): ตอนนี้มีเท่าไหร่ · การตัดสินใจนี้ใช้เท่าไหร่ · เส้นขั้นต่ำเท่าไหร่ · ไหลลงวันละเท่าไหร่
ตัวเลขไหนไม่ได้บอก = ไม่คำนวณส่วนนั้น (ถามหาแทน)
"""
from __future__ import annotations

import re

# หน่วย: 3 ล้าน · 2.5 ลบ. · 300,000 บาท · 1.2 พันล้าน · 500k · $2M · 1.5 billion
_MULT = {"พันล้าน": 1e9, "ร้อยล้าน": 1e8, "สิบล้าน": 1e7, "ล้าน": 1e6, "ลบ": 1e6, "ลบ.": 1e6, "แสน": 1e5, "หมื่น": 1e4, "พัน": 1e3,
         "billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "m": 1e6, "k": 1e3}


def _val(num: str, unit: str | None) -> float:
    v = float(num.replace(",", ""))
    return v * _MULT.get((unit or "").lower(), 1)


def _find(rx: re.Pattern, text: str):
    m = rx.search(text)
    return _val(m.group("n"), m.group("u")) if m else None


def _rx(lead: str) -> re.Pattern:
    return re.compile(r"(?:" + lead + r")[^\d\n]{0,24}?(?P<n>\d[\d,]*(?:\.\d+)?)\s*(?P<u>พันล้าน|ร้อยล้าน|สิบล้าน|ล้าน|ลบ\.?|แสน|หมื่น|พัน|billion|million|bn|[kKmMbB](?![a-zA-Z]))?", re.I)


_FLOOR = _rx(r"ขั้นต่ำ|ไม่ต่ำกว่า|ห้ามต่ำกว่า|อย่างน้อย|waterline|floor|minimum|at least|must not (?:go |fall )?below")
_CURRENT = _rx(r"(?:ตอนนี้|ปัจจุบัน)\s*(?:มี|เหลือ)?|มีเงินสด|เงินสดคงเหลือ|เงินสด(?:ที่)?มี|เงินสด|มีเงิน|คงเหลือ|เหลือ(?:อยู่)?|(?:we )?have|cash (?:on hand|balance)?|balance of|current(?:ly)?")
_SPEND = _rx(r"(?:จะ)?(?:ใช้|ลงทุน|จ่าย|ทุ่ม|กู้มาลง|เอาไป)(?:เงิน)?|งบ(?:ประมาณ)?|spend(?:ing)?|invest(?:ing)?|cost(?:s|ing)?|put in")
_BURN = re.compile(r"(?:ขาดทุน|ติดลบ|เผาเงิน|เงินออก|รายจ่าย(?:สุทธิ)?|burn(?:ing)?|los(?:e|ing)|outflow)[^\d\n]{0,16}?"
                   r"(?P<lead>วันละ|เดือนละ)?\s*(?P<n>\d[\d,]*(?:\.\d+)?)\s*(?P<u>พันล้าน|ร้อยล้าน|สิบล้าน|ล้าน|ลบ\.?|แสน|หมื่น|พัน|million|[kKmM](?![a-zA-Z]))?", re.I)
_PER = re.compile(r"^[^\n\d]{0,10}?(วันละ|ต่อวัน|/วัน|ทุกวัน|a day|per day|/day|daily|เดือนละ|ต่อเดือน|/เดือน|a month|per month|/month|monthly)", re.I)
_PER_MONTH = re.compile(r"เดือน|month", re.I)

NEAR = 0.2          # เหลือห่างเส้นไม่ถึง 20% ของเส้น = ใกล้จม


def _burn_per_day(text: str):
    """อัตราไหลลงต่อวัน (Drift) — ต้องบอกว่าต่อวันหรือต่อเดือน ไม่งั้นไม่เดา"""
    m = _BURN.search(text)
    if not m:
        return None
    per = m.group("lead") or ""
    if not per:
        after = _PER.search(text[m.end():])
        per = after.group(1) if after else ""
    if not per:
        return None
    v = _val(m.group("n"), m.group("u"))
    return v / 30 if _PER_MONTH.search(per) else v


def gauge(text: str) -> dict:
    t = str(text or "")
    floor, current, spend = _find(_FLOOR, t), _find(_CURRENT, t), _find(_SPEND, t)
    if current is not None and floor is not None and abs(current - floor) < 1e-9:
        current = None                               # จับเลขตัวเดียวกันซ้ำ (เช่น "มีขั้นต่ำ 2 ล้าน")
    burn = _burn_per_day(t)
    out = {"floor": floor, "current": current, "spend": spend, "burn_per_day": burn,
           "after": None, "level": "unknown", "margin": None, "days_to_floor": None}
    if floor is None or current is None:
        return out
    after = current - (spend or 0)
    out["after"] = after
    margin = (after - floor) / floor if floor else None
    out["margin"] = round(margin, 3) if margin is not None else None
    if after < floor:
        out["level"] = "below"                      # Below Water / Risk Critical → Stop-the-Line
    elif margin is not None and margin < NEAR:
        out["level"] = "near"
    else:
        out["level"] = "above"                      # Above Water / Stable
    if burn and burn > 0 and after >= floor:
        out["days_to_floor"] = int((after - floor) // burn)
    elif burn and burn > 0:
        out["days_to_floor"] = 0
    return out
