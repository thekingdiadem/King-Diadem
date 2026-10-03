# ENGINE/input_interpreter.py
# KING DIADEM — Input Interpreter
# แปลงภาษาไทยธรรมชาติ → ตัวเลขที่ engine ใช้ได้
# ไม่ใช่ if "น้อย" return 50

from __future__ import annotations
import re


# ── Money parser ─────────────────────────────────────────────────

_MONEY_WORDS = {
    "ไม่มีเงิน": 0, "หมดแล้ว": 0, "ติดลบ": -1, "ไม่เหลือ": 0,
    "น้อยมาก": 20, "น้อย": 80, "นิดหน่อย": 50,
    "พอกิน": 150, "พอใช้": 300, "โอเค": 500,
    "พอสมควร": 800, "เยอะ": 2000, "เยอะมาก": 5000,
}
_UNIT_MULTIPLIER = {"พัน": 1_000, "หมื่น": 10_000, "แสน": 100_000, "ล้าน": 1_000_000}


def _longest_first(d: dict) -> list:
    # คำยาวต้องตรวจก่อน — เดิม "เยอะ" ชนะ "เยอะมาก", "ดี" ชนะ "ไม่ดี"
    return sorted(d.items(), key=lambda kv: -len(kv[0]))


def _num(v, d: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        m = re.search(r"-?\d+(?:\.\d+)?", str(v or "").replace(",", ""))
        return float(m.group(0)) if m else d


def _bool(v, d: bool = True) -> bool:
    # เดิม bool("false") == True, bool("ไม่มี") == True
    if isinstance(v, bool):
        return v
    if v is None:
        return d
    if isinstance(v, (int, float)):
        return v != 0
    t = str(v).strip().lower()
    if t in ("false", "0", "no", "n", "ไม่", "ไม่มี", "ไม่ใช่", "off"):
        return False
    if t in ("true", "1", "yes", "y", "มี", "ใช่", "on"):
        return True
    return d


def parse_money(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().lower().replace(",", "")   # "1,500" เดิมอ่านได้ 1
    neg = text.startswith("-") or "ติดลบ" in text

    # หน่วย: "5 พัน", "2.5 หมื่น" (ตัวเลขชัดเจนมาก่อนคำกว้างๆ)
    for unit, mult in _UNIT_MULTIPLIER.items():
        pattern = r"(\d+(?:\.\d+)?)\s*" + unit
        m = re.search(pattern, text)
        if m:
            v = float(m.group(1)) * mult
            return -v if neg else v

    # ตัวเลขธรรมดา
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        v = float(nums[0])
        return -v if neg else v

    # คำบรรยาย (คำยาวก่อน)
    for word, amount in _longest_first(_MONEY_WORDS):
        if word in text:
            return float(amount)

    return 0.0


# ── Energy / stress parser ────────────────────────────────────────

_ENERGY_WORDS = {
    "หมดแรง": 5, "ล้ามาก": 10, "ล้า": 25, "เหนื่อย": 30,
    "พอไหว": 45, "โอเค": 55, "ดี": 70, "แข็งแรง": 85, "สดชื่น": 95,
    # คำปฏิเสธ — เดิม "ไม่ดี" ได้ 70 เพราะมีคำว่า "ดี"
    "ไม่ไหว": 10, "ไม่ดี": 25, "ไม่โอเค": 30, "ไม่ค่อยดี": 30, "ไม่สดชื่น": 35,
}

def parse_energy(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(100.0, float(value)))

    text = str(value).strip().lower()
    for word, score in _longest_first(_ENERGY_WORDS):
        if word in text:
            return float(score)

    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        return max(0.0, min(100.0, float(nums[0])))
    return 50.0


# ── Sleep hours parser ───────────────────────────────────────────

def parse_sleep(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(24.0, float(value)))

    text = str(value).strip().lower()

    # ตัวเลขพร้อมหน่วยชัดเจนมาก่อน — เดิม "นอนน้อย 5 ชม" ได้ 4 (เจอ "น้อย" ก่อน)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:ชั่วโมง|ชม|h|hr|hours?)", text)
    if m:
        return max(0.0, min(24.0, float(m.group(1))))

    if "ไม่ได้นอน" in text or "อดนอน" in text:
        return 0.0
    if "นิดหน่อย" in text or "แป๊บ" in text:
        return 2.0
    if "น้อย" in text:
        return 4.0
    if "พอ" in text:
        return 6.0
    if "เยอะ" in text or "เต็มอิ่ม" in text:
        return 8.0

    # "นอน 5 ชั่วโมง" / "5h"
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:ชั่วโมง|h|hr|hours?)", text)
    if m:
        return max(0.0, min(24.0, float(m.group(1))))

    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        return max(0.0, min(24.0, float(nums[0])))
    return 6.0


# ── Time available parser ─────────────────────────────────────────

def parse_time_available(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(24.0, float(value)))

    text = str(value).strip().lower()

    if "ไม่มีเวลา" in text or "ไม่มี" in text:
        return 0.5
    if "แป๊บ" in text or "นิดหน่อย" in text:
        return 1.0
    if "น้อย" in text:
        return 2.0
    if "พอสมควร" in text:
        return 4.0
    if "เยอะ" in text:
        return 8.0

    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:ชั่วโมง|h|hr|hours?)", text)
    if m:
        return max(0.0, min(24.0, float(m.group(1))))

    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        return max(0.0, min(24.0, float(nums[0])))
    return 8.0


# ── Master parser — แปลง raw context dict ─────────────────────────

def parse_context(raw: dict) -> dict:
    """
    รับ raw context จาก frontend (อาจเป็น string ปนตัวเลข)
    return dict ที่ engine ทุกตัวใช้ได้ทันที
    """
    raw = raw if isinstance(raw, dict) else {}
    return {
        # ไม่ได้บอกเงิน = ไม่รู้ (None) ไม่ใช่ 0 — เดิมกลายเป็น NO_MONEY ทุกข้อความ
        "money":          parse_money(raw["money"]) if raw.get("money") not in (None, "") else None,
        "energy":         parse_energy(raw.get("energy", 50)),
        "sleep_hours":    parse_sleep(raw.get("sleep_hours", 6)),
        "time_available": parse_time_available(raw.get("time_available", 8)),
        "stress":         max(0.0, min(100.0, _num(raw.get("stress", 50), 50.0))),
        "food_access":    _bool(raw.get("food_access", True)),
        "safe_place":     _bool(raw.get("safe_place", True)),
        "mental_state":   str(raw.get("mental_state", "stable")),
        "days_in_crisis": max(0, int(_num(raw.get("days_in_crisis", 0), 0.0))),
        "relationships":  max(0.0, min(100.0, _num(raw.get("relationships", 50), 50.0))),
        "purpose":        max(0.0, min(100.0, _num(raw.get("purpose", 50), 50.0))),
        # passthrough
        "route":          raw.get("route", "general"),
        "input":          raw.get("input", ""),
    }
