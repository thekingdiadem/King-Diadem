"""
AI/freedom_signal.py — KING DIADEM™
Freedom Signal Monitor — Master Equation Engine

KING DIADEM Master Equation:
  R = (D × T) / C
  R = Collapse Risk
  D = Drift (การเสื่อมสะสม)
  T = Time (เวลา)
  C = Choice (จำนวนทางเลือกที่เหลือ)

Early Warning: Choice(t+Δ) ≤ 1 → แจ้งเตือนทันที
Invariant: Choice(t) >= 1 → collapse = False

Architect: Nithikorn Bunsrang
FATE™: "Fail less. Harm less. Restore more."
"""

import time
import threading
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════

FREEDOM_MAX          = 100
FREEDOM_MIN          = 0
FREEDOM_DEFAULT      = 50

# Early warning threshold
CHOICE_EARLY_WARNING = 1     # Choice ≤ 1 → เตือนทันที
CHOICE_COLLAPSE      = 0     # Choice = 0 → collapse

# Drift bounds
DRIFT_MAX_DAILY      = 0.001  # DHD max 0.1% per day
DRIFT_COMPOUND_DAYS  = 30     # คำนวณ drift compound 30 วัน

# R thresholds
RISK_CRITICAL        = 5.0   # R > 5 = CRITICAL
RISK_HIGH            = 2.0   # R > 2 = HIGH
RISK_MEDIUM          = 1.0   # R > 1 = MEDIUM

_lock = threading.Lock()

# JSON ไม่มี Infinity (FastAPI ตอบ 500 ถ้าเจอ inf) — ใช้ค่าเพดานที่อ่านได้แทน
R_CAP = 1e9


def _num(v, d: float = 0.0) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d

# ══════════════════════════════════════════════════════════════════
# STATS STATE
# ══════════════════════════════════════════════════════════════════

_stats: dict = {
    "questions":        0,
    "choices":          0,
    "crisis":           0,
    "drift_events":     [],   # list of (timestamp, delta) — bounded 1000
    "choice_history":   [],   # list of (timestamp, choice_count) — bounded 1000
    "session_start":    time.time(),
}

# ══════════════════════════════════════════════════════════════════
# RECORD FUNCTIONS — backward compatible
# ══════════════════════════════════════════════════════════════════

def record_question() -> None:
    """บันทึก user question — เพิ่ม denominator"""
    with _lock:
        _stats["questions"] += 1


def record_choice(count: int = 1) -> None:
    """บันทึก choice ที่ระบบให้ — เพิ่ม C"""
    with _lock:
        count = max(0, int(_num(count, 0)))
        _stats["choices"] += count
        _stats["choice_history"].append((time.time(), count))
        if len(_stats["choice_history"]) > 1000:
            _stats["choice_history"].pop(0)


def record_crisis() -> None:
    """บันทึก crisis event — เพิ่ม D"""
    with _lock:
        _stats["crisis"] += 1
        _stats["drift_events"].append((time.time(), 1.0))
        if len(_stats["drift_events"]) > 1000:
            _stats["drift_events"].pop(0)


def record_drift(delta: float) -> None:
    """บันทึก drift amount โดยตรง"""
    with _lock:
        _stats["drift_events"].append((time.time(), _num(delta, 0.0)))
        if len(_stats["drift_events"]) > 1000:
            _stats["drift_events"].pop(0)


# ══════════════════════════════════════════════════════════════════
# MASTER EQUATION: R = (D × T) / C
# ══════════════════════════════════════════════════════════════════

def compute_collapse_risk(
    drift:    float,
    time_elapsed: float,
    choices:  float,
) -> dict:
    """
    R = (D × T) / C — KING DIADEM Master Equation

    drift         : D — accumulated drift (0.0–1.0)
    time_elapsed  : T — เวลาผ่านไป (วัน)
    choices       : C — จำนวนทางเลือกที่เหลือ

    ถ้า C → 0 : R → ∞ (collapse แน่นอน)
    ถ้า C >= 1 : collapse = False (ยังฟื้นได้)
    """
    drift    = max(0.0, _num(drift, 0.0))
    time_e   = max(0.0, _num(time_elapsed, 0.0))
    choices  = max(0.0, _num(choices, 0.0))

    # prevent division by zero — C=0 → R = ∞ (collapse) — ส่งเป็น R_CAP เพราะ JSON ไม่รองรับ inf
    if choices <= 0:
        return {
            "R":             R_CAP,
            "R_infinite":    True,
            "risk_level":    "COLLAPSE",
            "collapse":      True,
            "choice_alive":  False,
            "early_warning": True,
            "action":        "SYSTEM_PAUSE — Choice = 0 → collapse แน่นอน",
            "axiom":         "Choice(t) >= 1 → collapse = False",
            "D":             drift,
            "T":             time_e,
            "C":             choices,
        }

    R = (drift * time_e) / choices
    R = round(R, 6)

    # early warning
    early_warning = choices <= CHOICE_EARLY_WARNING

    # risk level
    if R > RISK_CRITICAL:
        risk_level = "CRITICAL"
        action     = "SYSTEM_PAUSE — drift สะสมสูงมาก เพิ่ม choice ทันที"
    elif R > RISK_HIGH:
        risk_level = "HIGH"
        action     = "INTERVENE — ลด drift หรือเพิ่ม choice ก่อนดำเนินการ"
    elif R > RISK_MEDIUM:
        risk_level = "MEDIUM"
        action     = "MONITOR — drift เริ่มสะสม ติดตามอย่างใกล้ชิด"
    else:
        risk_level = "LOW"
        action     = "PROCEED — ระบบเสถียร"

    if early_warning and risk_level not in ("CRITICAL", "HIGH"):
        risk_level = "HIGH"
        action     = "EARLY WARNING — Choice ≤ 1 มนุษย์กำลังจะเหลือทางเลือกสุดท้าย"

    return {
        "R":             R,
        "risk_level":    risk_level,
        "collapse":      False,
        "choice_alive":  choices >= 1,
        "early_warning": early_warning,
        "action":        action,
        "axiom":         "Choice(t) >= 1 → collapse = False",
        "D":             drift,
        "T":             time_e,
        "C":             choices,
    }


# ══════════════════════════════════════════════════════════════════
# FREEDOM INDEX — ใช้ Master Equation
# ══════════════════════════════════════════════════════════════════

def freedom_index(choices_available: Optional[int] = None) -> int:
    """
    Freedom Index (0–100) จาก Master Equation

    เดิม: (choices - crisis) / questions × 50 + 50
    ใหม่: inverse ของ R = (D × T) / C

    100 = ไม่มี drift ทางเลือกมาก
    0   = drift สูง ทางเลือกน้อย = collapse territory
    """
    with _lock:
        questions = _stats["questions"]
        choices   = _stats["choices"] if choices_available is None else choices_available
        crisis    = _stats["crisis"]
        drift_events = list(_stats["drift_events"])
        session_start = _stats["session_start"]

    # D = drift accumulated
    D = sum(d for _, d in drift_events) * 0.01 + crisis * 0.05
    D = min(1.0, D)

    # T = เวลาผ่านไป (วัน) — ขั้นต่ำ 1 วัน
    T = max(1.0, (time.time() - session_start) / 86400)

    # C = choices available
    C = max(0, _num(choices, 0))

    if C == 0:
        return FREEDOM_MIN

    R = (D * T) / C

    # แปลง R → freedom index (inverse)
    # R=0 → 100, R=1 → 50, R=5 → ~10, R=∞ → 0
    if R <= 0:
        freedom = FREEDOM_MAX
    else:
        freedom = int(FREEDOM_MAX / (1 + R))

    # bonus ถ้า questions สูง = ระบบถูกใช้งาน = freedom active
    if questions > 0:
        activity_bonus = min(10, int(questions * 0.5))
        freedom = min(FREEDOM_MAX, freedom + activity_bonus)

    return max(FREEDOM_MIN, min(FREEDOM_MAX, freedom))


def freedom_snapshot() -> dict:
    """Full freedom state สำหรับ /api/kernel_snapshot"""
    with _lock:
        questions     = _stats["questions"]
        choices       = _stats["choices"]
        crisis        = _stats["crisis"]
        drift_events  = list(_stats["drift_events"])
        session_start = _stats["session_start"]

    D = sum(d for _, d in drift_events) * 0.01 + crisis * 0.05
    D = min(1.0, D)
    T = max(1.0, (time.time() - session_start) / 86400)
    C = max(0, choices)

    risk = compute_collapse_risk(D, T, C)
    idx  = freedom_index(C)

    return {
        "freedom_index":   idx,
        "collapse_risk":   risk,
        "stats": {
            "questions":   questions,
            "choices":     choices,
            "crisis":      crisis,
            "drift_total": round(D, 4),
            "time_days":   round(T, 4),
        },
        "master_equation": "R = (D × T) / C",
        "invariant":       "Choice(t) >= 1 → collapse = False",
        "seal":            "Fail less. Harm less. Restore more.",
    }


def check_early_warning(choices_remaining: int) -> dict:
    """
    Early Warning System
    ถ้า Choice(t+Δ) ≤ 1 → แจ้งเตือนทันที
    """
    choices_remaining = _num(choices_remaining, 0.0)
    if choices_remaining <= CHOICE_COLLAPSE:
        return {
            "warning":    True,
            "level":      "COLLAPSE",
            "message":    "Choice = 0 → System Collapse — SYSTEM_PAUSE ทันที",
            "halt":       True,
            "axiom":      "Choice(t) >= 1 → collapse = False",
        }
    if choices_remaining <= CHOICE_EARLY_WARNING:
        return {
            "warning":    True,
            "level":      "CRITICAL",
            "message":    f"Choice = {choices_remaining} — มนุษย์กำลังจะเหลือทางเลือกสุดท้าย",
            "halt":       False,
            "axiom":      "Early Warning: Choice(t+Δ) ≤ 1",
        }
    return {
        "warning":    False,
        "level":      "STABLE",
        "message":    f"Choice = {choices_remaining} — ระบบเสถียร",
        "halt":       False,
        "axiom":      "Choice(t) >= 1 → collapse = False",
    }


# ══════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════

def _self_test() -> dict:
    # Master Equation
    r1 = compute_collapse_risk(drift=0.0, time_elapsed=1.0, choices=5.0)
    assert r1["R"] == 0.0
    assert r1["risk_level"] == "LOW"
    assert r1["choice_alive"] is True

    # C=0 → collapse
    r2 = compute_collapse_risk(drift=0.1, time_elapsed=10.0, choices=0.0)
    assert r2["collapse"] is True
    assert r2["risk_level"] == "COLLAPSE"

    # high drift + low choice → CRITICAL
    r3 = compute_collapse_risk(drift=0.8, time_elapsed=10.0, choices=1.0)
    assert r3["risk_level"] in ("CRITICAL", "HIGH")

    # determinism
    r4 = compute_collapse_risk(0.3, 5.0, 3.0)
    r5 = compute_collapse_risk(0.3, 5.0, 3.0)
    assert r4["R"] == r5["R"]

    # early warning
    ew1 = check_early_warning(0)
    assert ew1["level"] == "COLLAPSE"
    assert ew1["halt"] is True

    ew2 = check_early_warning(1)
    assert ew2["level"] == "CRITICAL"
    assert ew2["warning"] is True

    ew3 = check_early_warning(5)
    assert ew3["level"] == "STABLE"

    # freedom index
    record_choice(5)
    record_question()
    idx = freedom_index()
    assert FREEDOM_MIN <= idx <= FREEDOM_MAX

    # snapshot
    snap = freedom_snapshot()
    assert "freedom_index" in snap
    assert "master_equation" in snap
    assert snap["master_equation"] == "R = (D × T) / C"

    return {"status": "OK", "module": "freedom_signal"}


if __name__ == "__main__":
    import json
    print(json.dumps(compute_collapse_risk(0.3, 7.0, 2.0), indent=2))
    print(json.dumps(freedom_snapshot(), indent=2, default=str))
    print(_self_test())
