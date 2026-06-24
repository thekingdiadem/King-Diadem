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


def parse_money(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().lower()

    # ตรงตัว
    for word, amount in _MONEY_WORDS.items():
        if word in text:
            return float(amount)

    # หน่วย: "5 พัน", "2.5 หมื่น"
    for unit, mult in _UNIT_MULTIPLIER.items():
        pattern = r"(\d+(?:\.\d+)?)\s*" + unit
        m = re.search(pattern, text)
        if m:
            return float(m.group(1)) * mult

    # ตัวเลขธรรมดา
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        return float(nums[0])

    return 0.0


# ── Energy / stress parser ────────────────────────────────────────

_ENERGY_WORDS = {
    "หมดแรง": 5, "ล้ามาก": 10, "ล้า": 25, "เหนื่อย": 30,
    "พอไหว": 45, "โอเค": 55, "ดี": 70, "แข็งแรง": 85, "สดชื่น": 95,
}

def parse_energy(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(100.0, float(value)))

    text = str(value).strip().lower()
    for word, score in _ENERGY_WORDS.items():
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
    return {
        "money":          parse_money(raw.get("money", 0)),
        "energy":         parse_energy(raw.get("energy", 50)),
        "sleep_hours":    parse_sleep(raw.get("sleep_hours", 6)),
        "time_available": parse_time_available(raw.get("time_available", 8)),
        "stress":         max(0.0, min(100.0, float(raw.get("stress", 50)))),
        "food_access":    bool(raw.get("food_access", True)),
        "safe_place":     bool(raw.get("safe_place", True)),
        "mental_state":   str(raw.get("mental_state", "stable")),
        "days_in_crisis": int(raw.get("days_in_crisis", 0)),
        "relationships":  max(0.0, min(100.0, float(raw.get("relationships", 50)))),
        "purpose":        max(0.0, min(100.0, float(raw.get("purpose", 50)))),
        # passthrough
        "route":          raw.get("route", "general"),
        "input":          raw.get("input", ""),
    }
