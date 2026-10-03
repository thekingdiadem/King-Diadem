"""
SIMULATIONS/black_swan_detector.py — KING DIADEM
Black Swan: เหตุการณ์หายาก คาดไม่ถึง ผลกระทบสูง
ไม่ใช้ random — ใช้ signal จาก state จริง
"""
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

BLACK_SWAN_SIGNALS = [
    "pandemic", "collapse", "war", "earthquake", "flood", "crisis",
    "วิกฤต", "น้ำท่วม", "แผ่นดินไหว", "สงคราม", "ระบาด", "ล่มสลาย",
    "market crash", "blackout", "coup", "รัฐประหาร",
]

# ระดับความรุนแรงของ black swan
SWAN_EVENTS = [
    {"event": "supply chain collapse",     "impact": 9, "recovery_days": 180},
    {"event": "financial system shock",    "impact": 8, "recovery_days": 90},
    {"event": "pandemic outbreak",         "impact": 9, "recovery_days": 365},
    {"event": "infrastructure failure",   "impact": 7, "recovery_days": 60},
    {"event": "political instability",    "impact": 6, "recovery_days": 120},
    {"event": "environmental disaster",   "impact": 8, "recovery_days": 240},
]


def detect_black_swan(state: dict = None, text: str = "") -> dict:
    """
    ตรวจ black swan จาก state + text signal
    ไม่ใช้ random — ใช้ entropy threshold + keyword detection
    """
    state   = state if isinstance(state, dict) else {}
    entropy = _num(state.get("entropy",   40), 40.0)
    stab    = _num(state.get("stability", 60), 60.0)
    resource= _num(state.get("resource",  50), 50.0)
    text_l  = str(text or "").lower()

    # keyword score
    keyword_hits = sum(1 for w in BLACK_SWAN_SIGNALS if _hit(w, text_l))

    # state score
    state_score = 0
    if entropy   > 85: state_score += 3
    elif entropy > 70: state_score += 1
    if stab      < 20: state_score += 3
    elif stab    < 35: state_score += 1
    if resource  < 10: state_score += 2

    total_score = keyword_hits * 2 + state_score
    is_swan     = total_score >= 4

    if not is_swan:
        return {
            "black_swan":  False,
            "score":       total_score,
            "entropy":     entropy,
            "stability":   stab,
            "message":     "ไม่พบสัญญาณ black swan ในขณะนี้",
        }

    # เลือก event ที่ match กับ keyword มากที่สุด
    event = _match_event(text_l)

    return {
        "black_swan":     True,
        "score":          total_score,
        "event":          event["event"],
        "impact":         event["impact"],
        "recovery_days":  event["recovery_days"],
        "entropy":        entropy,
        "stability":      stab,
        "keyword_hits":   keyword_hits,
        "recommendation": _recommend(event["impact"]),
        "fate_action":    "stabilize" if event["impact"] >= 8 else "secure_resources",
    }


def _match_event(text: str) -> dict:
    for e in SWAN_EVENTS:
        if any(_hit(w, text) for w in e["event"].split()):
            return e
    return SWAN_EVENTS[0]  # default: supply chain


def _recommend(impact: int) -> str:
    if impact >= 9:
        return "หยุดการตัดสินใจใหญ่ทันที — รักษา 1 เส้นทางรอดก่อน"
    if impact >= 7:
        return "ลดรายจ่าย สำรองทรัพยากรพื้นฐาน แจ้งคนใกล้ชิด"
    return "ติดตามสถานการณ์ใกล้ชิด เตรียม contingency plan"
