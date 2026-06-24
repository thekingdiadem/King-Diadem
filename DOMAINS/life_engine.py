# DOMAINS/life_engine.py
# KING DIADEM — Life Domain Engine
# ใช้ข้อมูลจริงจาก context ไม่ใช่ random

import time


def analyze_life(context: dict) -> dict:
    # ── รับค่าจาก context ────────────────────────────────────────
    energy       = float(context.get("energy",       50))   # 0-100
    stress       = float(context.get("stress",        50))   # 0-100
    sleep_hours  = float(context.get("sleep_hours",    6))
    money        = float(context.get("money",          0))
    relationships = float(context.get("relationships", 50))  # คุณภาพความสัมพันธ์ 0-100
    purpose      = float(context.get("purpose",        50))  # ความรู้สึกมีความหมาย 0-100

    # ── Happiness score (deterministic) ──────────────────────────
    happiness = (
        energy        * 0.25 +
        relationships * 0.25 +
        purpose       * 0.30 +
        min(sleep_hours / 8, 1.0) * 100 * 0.20
    ) / 100

    # ── Life balance waterline ─────────────────────────────────────
    stress_norm = stress / 100
    balance = happiness - (stress_norm * 0.6)
    waterline = max(0.0, min(100.0, balance * 100))

    # ── Direction ─────────────────────────────────────────────────
    if waterline >= 70:
        direction = "positive_path"
        advice    = "ระบบสมดุล — รักษาต่อเนื่อง"
    elif waterline >= 50:
        direction = "balanced"
        advice    = "ดีพอสมควร — มีจุดที่พัฒนาได้"
    elif waterline >= 30:
        direction = "stressed"
        advice    = "ความเครียดสูง — หาพื้นที่ลดแรงกดดัน"
    else:
        direction = "critical_imbalance"
        advice    = "วิกฤต — ต้องหยุดและ reset ก่อน"

    # ── Survivor context สำหรับ LYLA ─────────────────────────────
    survivor_ctx = ""
    if sleep_hours < 4:
        survivor_ctx += "[นอนน้อยมาก — ห้ามตัดสินใจใหญ่] "
    if money <= 0:
        survivor_ctx += "[ไม่มีเงิน — LYLA โฟกัส survival ก่อน] "
    if stress > 75:
        survivor_ctx += "[เครียดสูง — ลดภาระก่อนวางแผน] "

    return {
        "domain":        "life",
        "timestamp":     time.time(),
        "happiness":     round(happiness, 3),
        "life_balance":  round(balance, 3),
        "waterline":     round(waterline, 1),
        "direction":     direction,
        "advice":        advice,
        "survivor_ctx":  survivor_ctx.strip(),
        "flags": {
            "sleep_debt":   sleep_hours < 5,
            "no_money":     money <= 0,
            "high_stress":  stress > 70,
            "low_purpose":  purpose < 30,
        },
        "input": context,
    }
