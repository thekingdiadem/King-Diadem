# core/time_engine.py
# KING DIADEM™ — Time Awareness Engine
# "ตอบถูกบริบท ถูกเวลา — ระบบที่รู้ว่าตอนนี้คืออะไรสำหรับมนุษย์คนนี้"
#
# SCL-7 A5: Even in system-mode, tone must remain grounded and kind.
# Article 1: Reality is measured, not assumed.

import time
import datetime
from typing import Optional

# ── Time Zone (Thailand UTC+7) ────────────────────────────────────
TZ_OFFSET_HOURS = 7

# ── Time Windows ──────────────────────────────────────────────────
# ใช้กำหนด context ของผู้ใช้ ณ เวลานั้น
TIME_WINDOWS = {
    "DEEP_NIGHT":   (0,  5),    # 00:00–04:59 — อาจเหนื่อย/คิดมาก
    "EARLY_MORNING":(5,  8),    # 05:00–07:59 — เริ่มวัน
    "MORNING":      (8,  12),   # 08:00–11:59 — active
    "AFTERNOON":    (12, 17),   # 12:00–16:59 — productive
    "EVENING":      (17, 21),   # 17:00–20:59 — winding down
    "NIGHT":        (21, 24),   # 21:00–23:59 — rest / reflect
}

# ── Human context per window ──────────────────────────────────────
_WINDOW_CONTEXT = {
    "DEEP_NIGHT": {
        "label":       "ดึกมาก",
        "energy":      "low",
        "note":        "ผู้ใช้อาจเหนื่อยหรือกำลังคิดหนัก — ตอบสั้น อบอุ่น ไม่ overwhelm",
        "tone_hint":   "gentle",
        "urgency":     "low",
    },
    "EARLY_MORNING": {
        "label":       "เช้าตรู่",
        "energy":      "rising",
        "note":        "เริ่มวันใหม่ — ตอบกระชับ ให้แรงบันดาลใจได้",
        "tone_hint":   "encouraging",
        "urgency":     "medium",
    },
    "MORNING": {
        "label":       "เช้า",
        "energy":      "high",
        "note":        "พลังงานสูง — ตอบได้เต็มที่ ลงรายละเอียดได้",
        "tone_hint":   "direct",
        "urgency":     "normal",
    },
    "AFTERNOON": {
        "label":       "บ่าย",
        "energy":      "medium",
        "note":        "ช่วงทำงาน — ตอบตรงประเด็น ไม่วกเวียน",
        "tone_hint":   "direct",
        "urgency":     "normal",
    },
    "EVENING": {
        "label":       "เย็น",
        "energy":      "declining",
        "note":        "ใกล้หมดวัน — ตอบให้จบได้ ไม่เพิ่มภาระ",
        "tone_hint":   "calm",
        "urgency":     "low",
    },
    "NIGHT": {
        "label":       "กลางคืน",
        "energy":      "low",
        "note":        "เวลาพัก/คิดทบทวน — ตอบอบอุ่น ไม่เร่ง",
        "tone_hint":   "gentle",
        "urgency":     "low",
    },
}

# ── TTF severity ──────────────────────────────────────────────────
_TTF_SEVERITY = [
    (80, "STABLE",   "ระบบยังมีเวลา — ไม่ต้องรีบ"),
    (50, "WARNING",  "เริ่มตึง — ควรเริ่มลดความเสี่ยง"),
    (25, "CRITICAL", "เวลาน้อยมาก — intervene ทันที"),
    (0,  "COLLAPSE", "ถึง floor แล้ว — SYSTEM_PAUSE"),
]


# ── Core: TTF computation ─────────────────────────────────────────
def compute_time_to_failure(state: dict) -> dict:
    """
    คำนวณ time-to-failure score (0–100)
    100 = ปลอดภัยมาก / 0 = collapse

    สูตร: risk = drift×0.4 + entropy×0.3 + resource_deficit×0.3
    TTF  = 100 - risk  (bounded 0–100)

    Article 1 — ค่าทุกตัวมาจาก state จริง อธิบายได้
    """
    drift    = max(0.0, min(100.0, float(state.get("drift",    0.0))))
    entropy  = max(0.0, min(100.0, float(state.get("entropy",  50.0))))
    resource = max(0.0, min(100.0, float(state.get("resource", 50.0))))

    risk = (drift * 0.4) + (entropy * 0.3) + ((100.0 - resource) * 0.3)
    ttf  = round(max(0.0, 100.0 - risk), 2)

    # severity label
    severity = "COLLAPSE"
    severity_note = _TTF_SEVERITY[-1][2]
    for threshold, label, note in _TTF_SEVERITY:
        if ttf >= threshold:
            severity = label
            severity_note = note
            break

    return {
        "ttf":            ttf,
        "risk_score":     round(risk, 2),
        "severity":       severity,
        "severity_note":  severity_note,
        "inputs": {
            "drift":    drift,
            "entropy":  entropy,
            "resource": resource,
        },
        "axiom": "Choice(t) >= 1 -> collapse = False",
    }


def compute_decision_window(ttf_result: dict) -> dict:
    """
    คำนวณ decision window จาก TTF
    window = TTF - 10 (bounded 0)
    ยิ่ง window กว้าง = มีเวลาคิดมากกว่า
    """
    ttf    = ttf_result if isinstance(ttf_result, float) else ttf_result.get("ttf", 50.0)
    window = round(max(0.0, ttf - 10.0), 2)

    return {
        "decision_window": window,
        "ttf":             ttf,
        "has_window":      window > 0,
        "urgency":         "HIGH" if window < 20 else "MEDIUM" if window < 50 else "LOW",
    }


# ── Core: Time awareness ──────────────────────────────────────────
def get_current_time_context(unix_ts: Optional[float] = None) -> dict:
    """
    คืน time context ปัจจุบัน (Thailand UTC+7)
    ใช้ดู window, energy level, tone_hint สำหรับปรับ response

    SCL-7 A5 — ระบบรู้เวลา → ตอบให้เหมาะกับบริบทมนุษย์
    """
    ts  = unix_ts or time.time()
    utc = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    th  = utc.replace(tzinfo=None) + datetime.timedelta(hours=TZ_OFFSET_HOURS)
    h   = th.hour

    window = "NIGHT"
    for name, (start, end) in TIME_WINDOWS.items():
        if start <= h < end:
            window = name
            break

    ctx = _WINDOW_CONTEXT[window]

    return {
        "window":        window,
        "label":         ctx["label"],
        "hour_th":       h,
        "minute":        th.minute,
        "time_str":      th.strftime("%H:%M"),
        "date_str":      th.strftime("%Y-%m-%d"),
        "weekday":       th.strftime("%A"),
        "energy":        ctx["energy"],
        "tone_hint":     ctx["tone_hint"],
        "urgency":       ctx["urgency"],
        "context_note":  ctx["note"],
        "is_late_night": window == "DEEP_NIGHT",
        "is_working_hours": window in ("MORNING", "AFTERNOON"),
    }


def get_response_timing_advice(state: dict, unix_ts: Optional[float] = None) -> dict:
    """
    รวม TTF + time context → คืน advice สำหรับ response engine
    ใช้ใน gateway / eternal_snapshot เพื่อปรับ tone + urgency

    "ตอบถูกบริบท ถูกเวลา"
    """
    ttf_result  = compute_time_to_failure(state)
    dw_result   = compute_decision_window(ttf_result)
    time_ctx    = get_current_time_context(unix_ts)

    # ถ้าดึกมาก + system critical → warn แต่ไม่ตื่นตระหนก
    combined_urgency = "HIGH"
    if ttf_result["severity"] == "STABLE" and time_ctx["urgency"] == "low":
        combined_urgency = "LOW"
    elif ttf_result["severity"] in ("STABLE", "WARNING") and time_ctx["urgency"] != "low":
        combined_urgency = "MEDIUM"
    elif ttf_result["severity"] in ("CRITICAL", "COLLAPSE"):
        combined_urgency = "HIGH"

    return {
        "ttf":              ttf_result,
        "decision_window":  dw_result,
        "time_context":     time_ctx,
        "combined_urgency": combined_urgency,
        "response_hint":    time_ctx["tone_hint"],
        "should_be_brief":  time_ctx["is_late_night"] or combined_urgency == "HIGH",
        "seal":             "Logic must never erase warmth.",
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    import json

    # TTF stable
    r1 = compute_time_to_failure({"drift": 10, "entropy": 20, "resource": 80})
    assert r1["severity"] == "STABLE", f"expected STABLE got {r1['severity']}"
    assert r1["ttf"] > 70

    # TTF collapse
    r2 = compute_time_to_failure({"drift": 90, "entropy": 80, "resource": 10})
    assert r2["severity"] in ("CRITICAL", "COLLAPSE")
    assert r2["ttf"] < 30

    # determinism
    r3 = compute_time_to_failure({"drift": 50, "entropy": 50, "resource": 50})
    r4 = compute_time_to_failure({"drift": 50, "entropy": 50, "resource": 50})
    assert r3["ttf"] == r4["ttf"]

    # decision window
    dw = compute_decision_window(r1)
    assert dw["has_window"] is True
    assert dw["decision_window"] == round(r1["ttf"] - 10, 2)

    # time context
    tc = get_current_time_context()
    assert "window" in tc
    assert "tone_hint" in tc
    assert 0 <= tc["hour_th"] <= 23

    # full advice
    advice = get_response_timing_advice({"drift": 30, "entropy": 40, "resource": 60})
    assert "ttf" in advice
    assert "time_context" in advice
    assert "combined_urgency" in advice

    return {"status": "OK", "module": "time_engine"}


if __name__ == "__main__":
    import json
    advice = get_response_timing_advice({"drift": 30, "entropy": 55, "resource": 45})
    print(json.dumps(advice, indent=2, ensure_ascii=False))
    print(_self_test())
