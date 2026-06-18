# ENGINE/risk_engine.py
# KING DIADEM — Risk Engine
# เพิ่ม assess(pattern) ให้ตรงกับที่ app.py และ engine_router เรียก
# คง evaluate_risk(text) ไว้เพื่อ backward compat
from __future__ import annotations

def evaluate_risk(text: str) -> dict:
    """ประเมิน risk จาก text — scale score 0-7"""
    t = (text or "").casefold()
    score = 0
    if any(k in t for k in ("error", "พัง", "ล่ม", "traceback", "exception",
                              "module not found", "500", "502", "503")):
        score += 2
    if any(k in t for k in ("deploy", "render", "github pages", "cors",
                              "uvicorn", "fastapi", "start command")):
        score += 1
    if any(k in t for k in ("อดข้าว", "ไม่มีเงิน", "เงินหมด", "ตาย",
                              "kill myself", "suicide", "ทำร้ายตัวเอง")):
        score += 3
    if any(k in t for k in ("now", "ด่วน", "เดี๋ยวนี้", "ทันที",
                              "immediately", "urgent")):
        score += 1
    level = "high" if score >= 4 else "medium" if score >= 2 else "low"
    return {
        "score": score,
        "level": level,
        "pause": level == "high",
    }

def assess(pattern: dict) -> dict:
    """
    ประเมิน risk จาก pattern dict (entropy/resource/stability/input)
    คืน dict ที่ engine_router และ decision_engine ใช้ได้ทันที
    scale risk_score 0-100 เหมือนกับ emptiness_guard
    """
    if not isinstance(pattern, dict):
        pattern = {}
    entropy   = float(pattern.get("entropy",   40))
    resource  = float(pattern.get("resource",  50))
    stability = float(pattern.get("stability", 60))
    risk_score = entropy * 0.5 + (100.0 - resource) * 0.5
    if risk_score >= 75:
        level = "CRITICAL"
    elif risk_score >= 55:
        level = "HIGH"
    elif risk_score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"
    text_risk = evaluate_risk(str(pattern.get("input", "")))
    if text_risk["level"] == "high" and level not in ("CRITICAL", "HIGH"):
        level = "HIGH"
        risk_score = max(risk_score, 60.0)
    remaining_choices = max(1, int((100 - risk_score) / 20))
    return {
        "risk_score":        round(risk_score, 2),
        "level":             level,
        "decision_level":    level,
        "remaining_choices": remaining_choices,
        "stability":         stability,
        "resource":          resource,
        "entropy":           entropy,
        "drift":             float(pattern.get("drift", 0)),
        "text_risk":         text_risk,
    }

# ── ALIASES — backward compat ─────────────────────────────────────
# universal_engine imports analyze_risk → map ไป assess
def analyze_risk(data) -> dict:
    """Alias สำหรับ universal_engine — delegates to assess()"""
    if isinstance(data, str):
        return evaluate_risk(data)
    if isinstance(data, dict):
        return assess(data)
    return assess({})

# อื่นๆ ที่อาจ import ชื่อต่างกัน
assess_risk = assess
risk_assess = assess
