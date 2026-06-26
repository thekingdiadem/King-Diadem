"""
AI_KERNEL/reality_constraint.py — KING DIADEM™
Reality Constraint Engine
ตรวจว่า action/decision ยังอยู่ในความเป็นจริงไหม

Architect: Nithikorn Bunsrang
FATE™: "Reality + Evidence − Drift = Governance"

❌ REMOVED: return {"status": "ok"} ว่างๆ ของ ChatGPT
✅ REBUILT: enforce จริงจาก 3 กฎพื้นฐาน
   1. อนิจจัง — ทุกสิ่งเปลี่ยนแปลง ระบบต้องไม่แข็งทื่อ
   2. ทุกขัง  — ทุกสิ่งมีแรงกดดัน entropy เพิ่มเสมอ
   3. อนัตตา  — ไม่มีศูนย์กลางถาวร อย่าพึ่งพา single point
"""

import time
from typing import Optional

# ── Reality Laws (P1 — อนิจจัง ทุกขัง อนัตตา) ───────────────────
REALITY_LAWS = {
    "impermanence":    "อนิจจัง — ทุกสิ่งไม่เที่ยง ระบบต้องรับการเปลี่ยนแปลงได้",
    "instability":     "ทุกขัง  — ทุกสิ่งมีแรงกดดัน entropy เพิ่มเสมอ",
    "non_centrality":  "อนัตตา  — ไม่มีศูนย์กลางถาวร ห้าม single point of failure",
}

# ── Drift thresholds ──────────────────────────────────────────────
DRIFT_WARN_THRESHOLD     = 0.3    # drift เกินนี้ = WARNING
DRIFT_CRITICAL_THRESHOLD = 0.6    # drift เกินนี้ = CRITICAL
ENTROPY_CEILING          = 80.0   # entropy เกินนี้ = ระบบไม่เสถียร
ASSUMPTION_DECAY_DAYS    = 7      # assumption เก่ากว่านี้ = stale

# ── Constraint registry ───────────────────────────────────────────
CONSTRAINTS = {
    "C1": {
        "name":    "impermanence_check",
        "law":     "impermanence",
        "desc":    "action ต้องไม่สมมติว่าสิ่งใดคงที่ตลอดไป",
        "check":   "assumes_permanence",
        "severity": "WARNING",
    },
    "C2": {
        "name":    "entropy_check",
        "law":     "instability",
        "desc":    "action ต้องไม่ ignore entropy หรือแรงกดดันที่มีอยู่",
        "check":   "ignores_entropy",
        "severity": "CRITICAL",
    },
    "C3": {
        "name":    "single_point_check",
        "law":     "non_centrality",
        "desc":    "action ต้องไม่พึ่งพา single point of failure",
        "check":   "single_point_dependency",
        "severity": "CRITICAL",
    },
    "C4": {
        "name":    "evidence_check",
        "law":     "impermanence",
        "desc":    "action ต้องมี evidence รองรับ ไม่ใช่ assumption ล้วนๆ",
        "check":   "no_evidence",
        "severity": "WARNING",
    },
    "C5": {
        "name":    "drift_check",
        "law":     "instability",
        "desc":    "drift ต้องไม่เกิน threshold — ถ้าเกินต้อง intervene",
        "check":   "drift_exceeded",
        "severity": "CRITICAL",
    },
    "C6": {
        "name":    "stale_assumption_check",
        "law":     "impermanence",
        "desc":    "assumption ที่เก่าเกิน 7 วันถือว่า stale — ต้อง revalidate",
        "check":   "stale_assumption",
        "severity": "WARNING",
    },
}


# ── Core enforcement ──────────────────────────────────────────────
def enforce_reality(state: Optional[dict] = None) -> dict:
    """
    ตรวจ state ต่อ 3 กฎความเป็นจริง + drift
    คืน full constraint report

    FATE™: Reality + Evidence − Drift = Governance
    """
    if state is None:
        state = {}

    entropy   = float(state.get("entropy",   50.0))
    drift     = float(state.get("drift",      0.0))
    stability = float(state.get("stability", 50.0))

    violations  = []
    critical    = False
    drift_level = "OK"

    # C2 — entropy ceiling
    if entropy > ENTROPY_CEILING:
        violations.append({
            "constraint": "C2",
            "law":        "instability",
            "reason":     f"entropy={entropy} > ceiling={ENTROPY_CEILING}",
            "action":     "SYSTEM_PAUSE — entropy ต้องลดก่อนดำเนินการต่อ",
            "severity":   "CRITICAL",
        })
        critical = True

    # C5 — drift threshold
    if drift > DRIFT_CRITICAL_THRESHOLD:
        drift_level = "CRITICAL"
        violations.append({
            "constraint": "C5",
            "law":        "instability",
            "reason":     f"drift={drift} > critical={DRIFT_CRITICAL_THRESHOLD}",
            "action":     "HALT — arrest drift immediately",
            "severity":   "CRITICAL",
        })
        critical = True
    elif drift > DRIFT_WARN_THRESHOLD:
        drift_level = "WARNING"
        violations.append({
            "constraint": "C5",
            "law":        "instability",
            "reason":     f"drift={drift} > warn={DRIFT_WARN_THRESHOLD}",
            "action":     "MONITOR — drift approaching critical",
            "severity":   "WARNING",
        })

    # C3 — single point of failure
    if state.get("single_point_dependency"):
        violations.append({
            "constraint": "C3",
            "law":        "non_centrality",
            "reason":     "single point of failure detected",
            "action":     "diversify — add redundancy",
            "severity":   "CRITICAL",
        })
        critical = True

    # C1 — permanence assumption
    if state.get("assumes_permanence"):
        violations.append({
            "constraint": "C1",
            "law":        "impermanence",
            "reason":     "system assumes current state is permanent",
            "action":     "add change-readiness to design",
            "severity":   "WARNING",
        })

    # C4 — no evidence
    if state.get("no_evidence"):
        violations.append({
            "constraint": "C4",
            "law":        "impermanence",
            "reason":     "action has no supporting evidence",
            "action":     "gather evidence before proceeding",
            "severity":   "WARNING",
        })

    # C6 — stale assumption
    assumption_age = float(state.get("assumption_age_days", 0))
    if assumption_age > ASSUMPTION_DECAY_DAYS:
        violations.append({
            "constraint": "C6",
            "law":        "impermanence",
            "reason":     f"assumption is {assumption_age} days old > {ASSUMPTION_DECAY_DAYS}",
            "action":     "revalidate assumption against current reality",
            "severity":   "WARNING",
        })

    return {
        "status":       "critical" if critical else "warning" if violations else "ok",
        "critical":     critical,
        "violations":   violations,
        "violation_count": len(violations),
        "drift_level":  drift_level,
        "entropy":      entropy,
        "drift":        drift,
        "stability":    stability,
        "constraints":  CONSTRAINTS,
        "reality_laws": REALITY_LAWS,
        "equation":     "Reality + Evidence − Drift = Governance",
        "checked_at":   time.time(),
    }


def check_action_reality(action: dict) -> dict:
    """
    ตรวจ action เดี่ยวว่าขัดกับความเป็นจริงไหม
    ใช้ใน north_principle() และ decision pipeline
    """
    violations = []

    for cid, constraint in CONSTRAINTS.items():
        if action.get(constraint["check"]):
            violations.append({
                "constraint": cid,
                "name":       constraint["name"],
                "law":        constraint["law"],
                "desc":       constraint["desc"],
                "severity":   constraint["severity"],
            })

    critical = any(v["severity"] == "CRITICAL" for v in violations)

    return {
        "reality_pass": len(violations) == 0,
        "critical":     critical,
        "violations":   violations,
        "equation":     "Reality + Evidence − Drift = Governance",
        "checked_at":   time.time(),
    }


def get_reality_summary() -> dict:
    """dump สำหรับ /api/kernel_snapshot"""
    return {
        "reality_laws":              REALITY_LAWS,
        "constraints":               CONSTRAINTS,
        "drift_warn_threshold":      DRIFT_WARN_THRESHOLD,
        "drift_critical_threshold":  DRIFT_CRITICAL_THRESHOLD,
        "entropy_ceiling":           ENTROPY_CEILING,
        "assumption_decay_days":     ASSUMPTION_DECAY_DAYS,
        "equation":                  "Reality + Evidence − Drift = Governance",
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # healthy state
    r1 = enforce_reality({"entropy": 40, "drift": 0.1, "stability": 70})
    assert r1["status"] == "ok"
    assert r1["critical"] is False

    # high entropy → critical
    r2 = enforce_reality({"entropy": 85, "drift": 0.1})
    assert r2["critical"] is True
    assert any(v["constraint"] == "C2" for v in r2["violations"])

    # drift critical
    r3 = enforce_reality({"drift": 0.7, "entropy": 40})
    assert r3["critical"] is True
    assert r3["drift_level"] == "CRITICAL"

    # drift warning
    r4 = enforce_reality({"drift": 0.4, "entropy": 40})
    assert r4["drift_level"] == "WARNING"
    assert r4["status"] == "warning"

    # single point
    r5 = enforce_reality({"single_point_dependency": True, "entropy": 40})
    assert r5["critical"] is True

    # action check
    a1 = check_action_reality({"ignores_entropy": True})
    assert a1["reality_pass"] is False
    assert a1["critical"] is True

    a2 = check_action_reality({})
    assert a2["reality_pass"] is True

    return {"status": "OK", "module": "reality_constraint"}


if __name__ == "__main__":
    import json
    print(json.dumps(enforce_reality({"entropy": 55, "drift": 0.25}), indent=2, ensure_ascii=False, default=str))
    print(_self_test())
