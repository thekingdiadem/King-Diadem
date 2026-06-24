# DOMAINS/human_engine.py
# KING DIADEM — Human Domain Engine
# วิเคราะห์สถานะมนุษย์ครบทุก dimension

import time


def analyze_human(context: dict) -> dict:
    energy        = float(context.get("energy",        50))
    money         = float(context.get("money",          0))
    stress        = float(context.get("stress",        50))
    risk_tolerance = float(context.get("risk",        0.5))
    sleep_hours   = float(context.get("sleep_hours",    6))
    relationships = float(context.get("relationships", 50))
    purpose       = float(context.get("purpose",       50))

    # ── Entropy (ความเสื่อม / ความวุ่นวายสะสม) ──────────────────
    entropy = (
        stress          * 0.40 +
        (100 - energy)  * 0.30 +
        max(0, (6 - sleep_hours) * 5) * 0.20 +
        (100 - relationships) * 0.10
    )
    entropy = min(100.0, entropy)

    # ── Waterline (ความสามารถในการตัดสินใจ) ──────────────────────
    waterline = 100.0
    waterline -= entropy * 0.50
    waterline -= max(0, (50 - energy)) * 0.20
    if money <= 0:
        waterline -= 15
    elif money < 100:
        waterline -= 8
    waterline -= (1.0 - risk_tolerance) * 10  # risk-averse + สถานการณ์แย่ = ลดลง
    waterline = max(0.0, min(100.0, waterline))

    # ── State ─────────────────────────────────────────────────────
    if entropy > 75 or waterline < 20:
        state = "overload"
    elif entropy > 55 or waterline < 40:
        state = "stressed"
    elif entropy < 25 and waterline > 70:
        state = "optimal"
    else:
        state = "stable"

    # ── Can decide ────────────────────────────────────────────────
    can_decide = waterline >= 35 and state not in ("overload",)

    # ── LYLA guidance ─────────────────────────────────────────────
    if state == "overload":
        guidance = "หยุดก่อน — ไม่ตัดสินใจใหญ่ในสถานะนี้"
    elif state == "stressed":
        guidance = "ทำได้แต่เลือก action ที่ใช้แรงน้อย — ไม่เพิ่มภาระ"
    elif state == "optimal":
        guidance = "พร้อมเต็มที่ — วิเคราะห์ได้ทุกทิศ"
    else:
        guidance = "สถานะปกติ — ดำเนินการได้อย่างระมัดระวัง"

    return {
        "domain":        "human",
        "timestamp":     time.time(),
        "entropy":       round(entropy, 1),
        "waterline":     round(waterline, 1),
        "state":         state,
        "can_decide":    can_decide,
        "guidance":      guidance,
        "inputs": {
            "energy":        energy,
            "money":         money,
            "stress":        stress,
            "risk_tolerance": risk_tolerance,
            "sleep_hours":   sleep_hours,
            "relationships": relationships,
            "purpose":       purpose,
        },
    }
