"""
WORLD_MODEL/survival_threshold.py — KING DIADEM™
Survival Threshold Engine
ตรวจ survival floor จริง — ไม่ใช่แค่ check list

Architect: Nithikorn Bunsrang
FATE™: Choice(t) >= 1 → collapse = False
"ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง"
LAYER 4 — HUMAN ENTROPY BUFFER
"""

import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# SYSTEM BELIEF — core axioms of survival
# ══════════════════════════════════════════════════════════════════

SYSTEM_BELIEF = {
    "choice_minimum":   1,         # Choice(t) >= 1 → collapse = False
    "survival_floor": ["food", "water", "shelter"],
    "human_centered":  True,
    "logic_agnostic":  True,
    "nature_aligned":  True,
    "entropy_aware":   True,       # ระบบต้องไม่ลืม entropy
    "downside_first":  True,       # ประเมินความเสียหายก่อนผลกำไร
    "seal":            "Fail less. Harm less. Restore more.",
}

# ══════════════════════════════════════════════════════════════════
# SURVIVAL DIMENSIONS — แต่ละ dimension มี threshold และ severity
# ══════════════════════════════════════════════════════════════════

SURVIVAL_DIMENSIONS = {
    "food": {
        "critical_floor": 0.2,    # ต่ำกว่านี้ = อดอาหาร
        "warn_floor":     0.4,
        "unit":           "security_score",
        "action":         "หาแหล่งอาหารทันที — survival ก่อน optimization",
    },
    "water": {
        "critical_floor": 0.2,
        "warn_floor":     0.4,
        "unit":           "security_score",
        "action":         "Stop-the-Line — น้ำคือ Waterline Tier-0",
    },
    "shelter": {
        "critical_floor": 0.2,
        "warn_floor":     0.3,
        "unit":           "security_score",
        "action":         "หาที่พักพิงก่อนดำเนินการอื่น",
    },
    "income": {
        "critical_floor": 0.15,
        "warn_floor":     0.3,
        "unit":           "security_score",
        "action":         "หารายได้เพิ่ม — ประหยัดอย่างเดียวไม่พอ",
    },
    "health": {
        "critical_floor": 0.2,
        "warn_floor":     0.4,
        "unit":           "security_score",
        "action":         "สุขภาพก่อน productivity — ร่างกายคือต้นทุนหลัก",
    },
    "social": {
        "critical_floor": 0.1,
        "warn_floor":     0.3,
        "unit":           "support_score",
        "action":         "ติดต่อคนที่ไว้ใจได้ — โดดเดี่ยวเพิ่ม entropy",
    },
    "energy": {
        "critical_floor": 0.2,
        "warn_floor":     0.35,
        "unit":           "level",
        "action":         "พักก่อน — ตัดสินใจตอนหมดแรงคือ noise ไม่ใช่ signal",
    },
}

# ══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def check_choice(options) -> dict:
    """
    ตรวจว่า options ยังมีอยู่ไหม
    Choice(t) >= 1 → collapse = False

    รับ: list, int, หรือ dict
    """
    if isinstance(options, list):
        count = len(options)
    elif isinstance(options, dict):
        count = len(options)
    elif isinstance(options, int):
        count = options
    else:
        count = 0

    if count < SYSTEM_BELIEF["choice_minimum"]:
        return {
            "status":   "COLLAPSE",
            "action":   "generate_more_options",
            "choices":  count,
            "minimum":  SYSTEM_BELIEF["choice_minimum"],
            "halt":     True,
            "axiom":    "Choice(t) >= 1 → collapse = False",
        }
    elif count == SYSTEM_BELIEF["choice_minimum"]:
        return {
            "status":   "WARNING",
            "action":   "expand_options_before_committing",
            "choices":  count,
            "minimum":  SYSTEM_BELIEF["choice_minimum"],
            "halt":     False,
            "axiom":    "A2 — Preserve at least one viable option",
        }
    return {
        "status":   "STABLE",
        "action":   "proceed",
        "choices":  count,
        "minimum":  SYSTEM_BELIEF["choice_minimum"],
        "halt":     False,
        "axiom":    "Choice(t) >= 1 → collapse = False",
    }


def survival_priority(context: dict) -> dict:
    """
    ตรวจว่า survival floor ไหนขาดอยู่
    คืน priority dimension ที่ต้องแก้ก่อน

    FATE™ Downside First — แก้ที่อันตรายที่สุดก่อน
    """
    missing   = []
    critical  = []
    warnings  = []

    for need in SYSTEM_BELIEF["survival_floor"]:
        if need not in context:
            missing.append(need)
        else:
            val = float(context[need])
            dim = SURVIVAL_DIMENSIONS.get(need, {})
            if val <= dim.get("critical_floor", 0.2):
                critical.append({"need": need, "value": val, "action": dim.get("action", "")})
            elif val <= dim.get("warn_floor", 0.4):
                warnings.append({"need": need, "value": val, "action": dim.get("action", "")})

    if critical:
        return {
            "status":   "CRITICAL",
            "priority": critical[0]["need"],
            "action":   critical[0]["action"],
            "critical": critical,
            "warnings": warnings,
            "missing":  missing,
            "halt":     True,
            "seal":     "ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง",
        }
    if missing:
        return {
            "status":   "UNKNOWN",
            "priority": missing[0],
            "action":   f"ต้องการข้อมูล '{missing[0]}' — ไม่สามารถประเมินได้",
            "missing":  missing,
            "halt":     False,
            "seal":     "ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง",
        }
    if warnings:
        return {
            "status":   "WARNING",
            "priority": warnings[0]["need"],
            "action":   warnings[0]["action"],
            "warnings": warnings,
            "halt":     False,
            "seal":     "ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง",
        }

    return {
        "status":   "STABLE",
        "priority": None,
        "action":   "proceed — all survival floors met",
        "halt":     False,
        "seal":     "ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง",
    }


def full_survival_check(context: dict) -> dict:
    """
    ตรวจ survival ทุก dimension + choice + drift
    ใช้ใน eternal_snapshot / gateway
    """
    results     = {}
    critical    = []
    warnings_   = []

    for dim, config in SURVIVAL_DIMENSIONS.items():
        val = float(context.get(dim, 0.5))
        if val <= config["critical_floor"]:
            sev = "CRITICAL"
            critical.append(dim)
        elif val <= config["warn_floor"]:
            sev = "WARNING"
            warnings_.append(dim)
        else:
            sev = "OK"

        results[dim] = {
            "value":    val,
            "severity": sev,
            "action":   config["action"] if sev != "OK" else "stable",
        }

    # choice check
    options = context.get("options_available", 2)
    choice  = check_choice(options)

    # overall
    if critical or choice["halt"]:
        overall = "CRITICAL"
        halt    = True
    elif warnings_:
        overall = "WARNING"
        halt    = False
    else:
        overall = "STABLE"
        halt    = False

    return {
        "overall":    overall,
        "halt":       halt,
        "dimensions": results,
        "critical":   critical,
        "warnings":   warnings_,
        "choice":     choice,
        "belief":     SYSTEM_BELIEF,
        "checked_at": time.time(),
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # choice — collapse
    r1 = check_choice(0)
    assert r1["status"] == "COLLAPSE"
    assert r1["halt"] is True

    # choice — warning
    r2 = check_choice(1)
    assert r2["status"] == "WARNING"
    assert r2["halt"] is False

    # choice — stable
    r3 = check_choice(["a", "b", "c"])
    assert r3["status"] == "STABLE"

    # survival priority — critical
    r4 = survival_priority({"food": 0.1, "water": 0.5, "shelter": 0.5})
    assert r4["status"] == "CRITICAL"
    assert r4["priority"] == "food"
    assert r4["halt"] is True

    # survival priority — stable
    r5 = survival_priority({"food": 0.8, "water": 0.9, "shelter": 0.7})
    assert r5["status"] == "STABLE"

    # survival priority — missing
    r6 = survival_priority({"food": 0.8})
    assert r6["status"] == "UNKNOWN"

    # full check
    fc = full_survival_check({
        "food": 0.7, "water": 0.8, "shelter": 0.6,
        "income": 0.5, "health": 0.7, "social": 0.4, "energy": 0.6,
        "options_available": 3,
    })
    assert fc["overall"] == "STABLE"
    assert fc["halt"] is False

    # full check critical
    fc2 = full_survival_check({"food": 0.1, "water": 0.1, "shelter": 0.5, "options_available": 0})
    assert fc2["halt"] is True

    return {"status": "OK", "module": "survival_threshold"}


if __name__ == "__main__":
    import json
    result = full_survival_check({
        "food": 0.3, "water": 0.6, "shelter": 0.5,
        "income": 0.2, "health": 0.6, "social": 0.3, "energy": 0.4,
        "options_available": 2,
    })
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print(_self_test())
