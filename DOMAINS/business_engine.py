# DOMAINS/business_engine.py
# KING DIADEM — Business Domain Engine (เลขธุรกิจล้วน)
#
# ย้ายกลับจาก legacy/ แล้วต่อเข้าระบบผ่าน core/engine_bridge (_business):
# คนพิมพ์ "ร้านขายได้เดือนละ 80,000 ต้นทุน 65,000" — เดิมระบบอธิบายสูตรอย่างเดียว ไม่ได้คิดตัวเลขให้
# ตอนนี้คิดกำไร · margin · สัดส่วนต้นทุน จากตัวเลขที่ผู้ใช้บอกเท่านั้น
#
# ตัดของเดิมออก (ขัดกับหลักของระบบ):
#   · คะแนน opportunity/waterline/risk จาก market_growth/competition/demand ที่ไม่มีใครส่งมา (ค่าเริ่ม 0.5 = ตัวเลขแต่งเอง)
#   · "recommended_strategy" ทางเดียว (เช่น pivot) — ระบบไม่ชี้ทางเดียว ผู้ใช้เลือกเอง
#   · log_decision ทุกครั้งที่เรียก — เขียนฐานข้อมูลซ่อนอยู่ และเก็บ input
#   · คืน "input" กลับไปทั้งก้อน — ส่งออกเฉพาะตัวเลข
# Deterministic ไม่มี random ไม่มี I/O


def _num(v):
    """ตัวเลขจริงที่จำกัด — ค่าเสีย/NaN/inf/ติดลบ → None"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if x != x or abs(x) == float("inf") or x < 0:
        return None
    return x


def analyze_business(revenue, cost) -> dict | None:
    """กำไร = รายรับ − ต้นทุน · margin = กำไร ÷ รายรับ · สัดส่วนต้นทุน = ต้นทุน ÷ รายรับ
    รายรับ ≤ 0 หรือค่าไม่ใช่ตัวเลข → None (เดิมให้ margin −100% แล้วสั่ง pivot)"""
    r, c = _num(revenue), _num(cost)
    if r is None or c is None or r <= 0:
        return None
    profit = r - c
    return {
        "revenue": round(r, 2),
        "cost": round(c, 2),
        "profit": round(profit, 2),
        "margin": round(profit / r, 4),
        "cost_share": round(c / r, 4),
        "breakeven_gap": round(max(0.0, -profit), 2),   # ขาดอีกเท่าไรถึงเท่าทุน (0 = ไม่ขาดทุน)
    }
