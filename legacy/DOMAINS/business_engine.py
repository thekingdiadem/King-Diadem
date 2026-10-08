# DOMAINS/business_engine.py
# KING DIADEM — Business Domain Engine
# Deterministic logic ไม่มี random — ทุก output ตรวจสอบได้

import time


def _num(v, d: float) -> float:
    """ตัวเลขจาก context — ค่าเสีย/NaN/inf → ค่าเริ่มต้น"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x and abs(x) != float("inf") else d


def analyze_business(context: dict) -> dict:
    context = context if isinstance(context, dict) else {}
    revenue     = _num(context.get("revenue"), 0)
    cost        = _num(context.get("cost"), 0)
    market_growth = _num(context.get("market_growth"), 0.5)
    competition   = _num(context.get("competition"), 0.5)
    demand        = _num(context.get("demand"), 0.5)

    # ── Core metrics ──────────────────────────────────────────────
    profit = revenue - cost
    margin = (profit / revenue) if revenue > 0 else -1.0
    cost_pressure = (cost / revenue) if revenue > 0 else 1.0

    # ── Opportunity score (deterministic weighted sum) ────────────
    opportunity = (
        market_growth * 0.35 +
        demand        * 0.40 +
        (1 - competition) * 0.25
    )

    # ── Waterline score 0-100 ──────────────────────────────────────
    waterline = 50.0
    waterline += margin     * 25    # margin ดี → บวก
    waterline += opportunity * 25   # โอกาสดี → บวก
    waterline -= cost_pressure * 20 # ต้นทุนสูง → ลบ
    waterline  = max(0.0, min(100.0, waterline))

    # ── Risk level ────────────────────────────────────────────────
    if waterline < 25:
        risk_level = "critical"
    elif waterline < 45:
        risk_level = "high"
    elif waterline < 65:
        risk_level = "moderate"
    else:
        risk_level = "low"

    # ── Strategy (FATE-style: deterministic, auditable) ───────────
    if margin < 0:
        strategy = "pivot"
        reason   = "ขาดทุน — ต้องเปลี่ยนโมเดล"
    elif risk_level == "critical":
        strategy = "defensive"
        reason   = "waterline ต่ำวิกฤต — ลดค่าใช้จ่ายก่อน"
    elif opportunity > 0.75 and margin > 0.25:
        strategy = "scale"
        reason   = "โอกาสสูง margin ดี — ขยายได้"
    elif opportunity > 0.55:
        strategy = "optimize"
        reason   = "โอกาสพอมี — ปรับ efficiency"
    elif demand < 0.3:
        strategy = "rethink_market"
        reason   = "demand ต่ำ — ต้องหา segment ใหม่"
    else:
        strategy = "observe"
        reason   = "ยังไม่มีสัญญาณชัด — รอข้อมูลเพิ่ม"

    result = {
        "domain":               "business",
        "timestamp":            time.time(),
        "profit":               round(profit, 2),
        "profit_margin":        round(margin, 3),
        "opportunity_score":    round(opportunity, 3),
        "cost_pressure":        round(cost_pressure, 3),
        "waterline":            round(waterline, 1),
        "risk_level":           risk_level,
        "recommended_strategy": strategy,
        "reason":               reason,
        "input":                context,
    }

    # ── optional saves (ไม่ crash ถ้าไม่มี) ─────────────────────
    try:
        from DATABASE.db import log_decision
        if log_decision:
            log_decision(
                user_id="system",
                input=str(context)[:2000],
                output=strategy,
                route="business",
                persona="VEGA",
            )
    except Exception:
        pass

    return result
