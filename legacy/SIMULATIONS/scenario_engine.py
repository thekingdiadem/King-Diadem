"""
SIMULATIONS/scenario_engine.py — KING DIADEM
Scenario Engine: ประเมินอนาคตจาก context จริง
ไม่ใช้ random — ใช้ pattern จาก input
"""
import time
import re


def _hit(w: str, text: str) -> bool:
    """คำอังกฤษเป็นคำเต็ม ("war" ไม่ติด "software", "ok" ไม่ติด "book"); ไทยเป็นวลี"""
    if w.isascii():
        return re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", text) is not None
    return w in text


def _num(v, d: float) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d


_RISK_KW   = ["risk","เสี่ยง","หนี้","ตกงาน","พังหมด","วิกฤต","crisis","debt","loss"]
_GROWTH_KW = ["โอกาส","เติบโต","เริ่มใหม่","growth","opportunity","expand","improve"]
# "ดี" "ใหม่" "พัง" เดี่ยวติดแทบทุกประโยค; "ok" ติด "book" → ใช้วลี + คำเต็ม
_STABLE_KW = ["มั่นคง","stable","สบายดี","ไปได้ดี","good","ok","ปกติดี","normal"]


def simulate_future(context: dict) -> dict:
    """
    ประเมิน future projection จาก context dict
    คืน success_probability, risk_level, outlook แบบ deterministic
    """
    if not isinstance(context, dict):
        return {"error": "context ต้องเป็น dict"}

    text     = str(context.get("input", context.get("text", ""))).lower()
    entropy  = _num(context.get("entropy",  50), 50.0)
    stability= _num(context.get("stability",60), 60.0)
    resource = _num(context.get("resource", 50), 50.0)

    # score จาก keywords
    risk_hits   = sum(1 for w in _RISK_KW   if _hit(w, text))
    growth_hits = sum(1 for w in _GROWTH_KW if _hit(w, text))
    stable_hits = sum(1 for w in _STABLE_KW if _hit(w, text))

    # base success จาก state
    base = (stability - entropy + resource) / 300 + 0.5
    base = max(0.05, min(0.95, base))

    # adjust จาก keywords
    base += growth_hits * 0.05
    base -= risk_hits   * 0.05
    base += stable_hits * 0.02
    success = round(max(0.05, min(0.95, base)), 3)

    # risk = inverse ของ success + entropy factor
    risk = round(max(0.05, min(0.95, 1 - success + (entropy / 200))), 3)

    # outlook
    if success > 0.72:   outlook = "growth"
    elif success > 0.52: outlook = "stable"
    elif success > 0.35: outlook = "uncertain"
    else:                outlook = "decline"

    return {
        "timestamp": time.time(),
        "input":     context,
        "future_projection": {
            "success_probability": success,
            "risk_level":          risk,
            "outlook":             outlook,
            "horizon_30d":         _horizon(success, 30),
            "horizon_90d":         _horizon(success, 90),
        },
        "fate_note": "Human retains final authority.",
    }


def _horizon(success: float, days: int) -> str:
    decay = 1 - (days / 1000)
    proj  = success * decay
    if proj > 0.65: return "positive trajectory"
    if proj > 0.45: return "stable with monitoring"
    return "intervention recommended"
