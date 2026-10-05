"""
core/feedback_loop.py — วงจรเรียนรู้จากเสียงผู้ใช้ (👍 / 👎 ใต้คำตอบ)

ต่อไฟล์ที่เคยไม่มีใครเรียก 3 ตัวเข้าด้วยกัน:
- DATABASE/decision_history.py  เก็บถาวรใน SQLite (เดิม feedback อยู่ในหน่วยความจำ รีสตาร์ทแล้วหาย)
- AI/reality_feedback.py        อัตราที่คำตอบช่วยได้ แยกตามเส้นทาง
- AI/reality_learning.py        แนวโน้ม (ดีขึ้น/แย่ลง) และความเสี่ยงที่คำตอบจะเพี้ยน (drift)

เก็บเฉพาะ: เส้นทาง · ระดับความเสี่ยง · ผลโหวต — ไม่เก็บข้อความของผู้ใช้หรือคำตอบ
"""
from __future__ import annotations

ROUTES = ("general", "risk", "civil", "survival", "collapse", "vega")
VOTES = ("up", "down")
_DOMAIN = "feedback"
_WARM_LIMIT = 200

try:
    from DATABASE.decision_history import save_decision, get_recent_decisions, count_decisions
except Exception:  # pragma: no cover
    save_decision = get_recent_decisions = count_decisions = None
try:
    from AI.reality_feedback import record_feedback, feedback_stats
except Exception:  # pragma: no cover
    record_feedback = feedback_stats = None
try:
    from AI.reality_learning import record_outcome, learning_summary
except Exception:  # pragma: no cover
    record_outcome = learning_summary = None


def _risk_level(risk: float) -> str:
    return "critical" if risk >= 75 else "high" if risk >= 55 else "medium" if risk >= 35 else "low"


def _clean(vote, route, risk):
    vote = str(vote or "").lower().strip()
    if vote not in VOTES:
        return None
    route = str(route or "general").lower().strip()
    if route not in ROUTES:
        route = "general"
    try:
        risk = float(risk)
    except (TypeError, ValueError):
        risk = 0.0
    risk = max(0.0, min(100.0, risk if risk == risk else 0.0))
    return vote, route, round(risk)


def _remember(vote: str, route: str, risk: float) -> None:
    """ใส่ลงสถิติในหน่วยความจำ (reality_feedback + reality_learning)"""
    lvl = _risk_level(risk)
    if record_feedback:
        record_feedback(f"คำตอบเส้นทาง {route}", f"ความเสี่ยง {lvl}", vote == "up", route=route)
    if record_outcome:
        # คำตอบตอนความเสี่ยงสูงมีน้ำหนักมากกว่า — พลาดตอนนั้นเสียหายกว่า
        record_outcome("", route, "positive" if vote == "up" else "negative",
                       route=route, confidence=0.5 + risk / 200, tags=[lvl])


def record(vote, route, risk) -> dict:
    c = _clean(vote, route, risk)
    if not c:
        return {"ok": False, "error": "vote ต้องเป็น up หรือ down"}
    vote, route, risk = c
    saved = bool(save_decision and save_decision({
        "domain": _DOMAIN, "route": route, "strategy": vote,
        "risk_level": _risk_level(risk), "risk_score": risk,
    }))
    _remember(vote, route, risk)
    return {"ok": True, "saved": saved}


def warm() -> int:
    """โหลดโหวตล่าสุดจาก SQLite กลับเข้าสถิติหลังรีสตาร์ท"""
    if not get_recent_decisions:
        return 0
    try:
        rows = get_recent_decisions(limit=_WARM_LIMIT, domain=_DOMAIN)
    except Exception as e:
        print(f"⚠ feedback_loop.warm: {type(e).__name__}")
        return 0
    n = 0
    for r in reversed(rows):                       # เก่า → ใหม่ ให้แนวโน้มถูกทิศ
        d = r.get("decision") if isinstance(r.get("decision"), dict) else {}
        c = _clean(r.get("strategy"), r.get("route"), d.get("risk_score"))
        if c:
            _remember(*c)
            n += 1
    return n


def stats() -> dict:
    fb = feedback_stats() if feedback_stats else {}
    ln = learning_summary() if learning_summary else {}
    try:
        total = count_decisions(_DOMAIN) if count_decisions else fb.get("samples", 0)
    except Exception:
        total = fb.get("samples", 0)
    up = (fb.get("breakdown") or {}).get("success", 0)
    down = (fb.get("breakdown") or {}).get("fail", 0)
    return {
        "votes": total, "recent_up": up, "recent_down": down,
        "helpful_rate": fb.get("success_rate", 0.0),
        "signal": fb.get("signal", "NO_DATA"),
        "trend": ln.get("recent_trend", "FLAT"), "drift_risk": ln.get("drift_risk", "UNKNOWN"),
        "routes": fb.get("top_routes", []),
    }

