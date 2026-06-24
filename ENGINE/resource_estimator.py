# ENGINE/resource_estimator.py
"""
KING DIADEM — Resource Estimator
คำนวณ survival runway จาก inputs จริง
ไม่ใช่ if food >= 5: += 5 แบบ flat
"""
from __future__ import annotations
from typing import Optional
import time


# Daily consumption baseline (adjustable)
DAILY_FOOD_COST  = 120.0   # บาท/วัน (กินข้าว 3 มื้อ ราคาประหยัด)
DAILY_FIXED_COST = 50.0    # ค่าใช้จ่ายคงที่/วัน (น้ำ, เดินทาง)


def estimate_resources(
    food:          float,          # มื้อที่มีอยู่
    money:         float,          # บาท
    daily_expense: float = DAILY_FOOD_COST + DAILY_FIXED_COST,
    water_liters:  float = 2.0,    # ลิตร/วัน ที่มี
    energy:        float = 50.0,   # 0-100
    shelter_ok:    bool  = True,
    context:       Optional[dict] = None,
) -> dict:

    ctx = context or {}
    alerts = []

    # ── Food runway ───────────────────────────────────────────────
    meals_per_day  = 3.0
    food_days      = round(food / meals_per_day, 2) if food > 0 else 0.0

    # ── Money runway ──────────────────────────────────────────────
    if daily_expense > 0:
        money_days = round(money / daily_expense, 2)
    else:
        money_days = 999.0

    # ── Water runway ─────────────────────────────────────────────
    water_need_daily = 2.0   # minimum liters
    water_days = round(water_liters / water_need_daily, 2) if water_liters >= 0 else 0.0

    # ── Binding constraint = shortest runway ──────────────────────
    runways = {"food": food_days, "money": money_days, "water": water_days}
    if not shelter_ok:
        runways["shelter"] = 0.0
        alerts.append("SHELTER_MISSING — อยู่กลางแจ้ง ต้องหาที่พักทันที")

    binding        = min(runways.values())
    binding_factor = min(runways, key=runways.get)
    survival_days  = round(binding, 2)

    # ── Alerts ────────────────────────────────────────────────────
    if food_days < 1:
        alerts.append("FOOD_CRITICAL — อาหารไม่ถึง 24 ชั่วโมง")
    if money_days < 2:
        alerts.append("MONEY_CRITICAL — เงินไม่ถึง 48 ชั่วโมง")
    if water_days < 1:
        alerts.append("WATER_CRITICAL — น้ำไม่พอ 24 ชั่วโมง")
    if energy < 20:
        alerts.append("ENERGY_LOW — decision quality จะพัง")

    # ── Waterline score ───────────────────────────────────────────
    # normalize แต่ละ runway เป็น 0-100 (cap ที่ 7 วัน)
    def _cap(days: float, cap: float = 7.0) -> float:
        return min(100.0, (days / cap) * 100)

    waterline = round(
        _cap(food_days)  * 0.35 +
        _cap(money_days) * 0.30 +
        _cap(water_days) * 0.20 +
        (80 if shelter_ok else 0) * 0.15,
        2
    )

    # ── Status ───────────────────────────────────────────────────
    if survival_days < 1:
        status = "COLLAPSE_RISK"
    elif survival_days < 2:
        status = "CRITICAL"
    elif survival_days < 4:
        status = "WARNING"
    else:
        status = "STABLE"

    return {
        "food":             food,
        "money":            money,
        "food_days":        food_days,
        "money_days":       money_days,
        "water_days":       water_days,
        "survival_days":    survival_days,
        "binding_factor":   binding_factor,
        "waterline":        waterline,
        "status":           status,
        "alerts":           alerts,
        "daily_expense":    daily_expense,
        "choice_preserved": survival_days > 0,
        "axiom":            "Choice(t) ≥ 1 → collapse = False",
        "timestamp":        time.time(),
    }
