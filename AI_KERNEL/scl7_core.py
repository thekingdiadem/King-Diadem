"""
AI_KERNEL/scl7_core.py — KING DIADEM™
SCL-7: System Core of Living Truth
A Human-Preserving Logic Framework

Architect: Nithikorn Bunsrang
FATE™: "Fail less, not win more."
"""

import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# SCL-7 CORE RULES (Immutable)
# ══════════════════════════════════════════════════════════════════

SCL7_RULES = {
    "human_first":           True,   # มนุษย์มาก่อนตรรกะเสมอ
    "preserve_choice":       True,   # รักษาทางเลือกไว้เสมอ Choice >= 1
    "no_harm_guidance":      True,   # ห้ามนำทางสู่อันตราย
    "transparent_reasoning": True,   # อธิบายได้ทุกขั้นตอน
    "no_authority":          True,   # ไม่มีอำนาจเหนือมนุษย์
    "warmth_before_logic":   True,   # ความอ่อนโยนมาก่อนความถูกต้อง
    "structure_protects":    True,   # โครงสร้างมีไว้ปกป้อง ไม่ใช่ครอบงำ
    "truth_does_not_rush":   True,   # ความจริงไม่ต้องเร่ง
    "silence_is_valid":      True,   # ความเงียบคือความสำเร็จเมื่อ choice > 0
    "room_to_breathe":       True,   # โครงสร้างที่ดีต้องมีพื้นที่ให้มนุษย์หายใจ
}

# ══════════════════════════════════════════════════════════════════
# SCL-7 AXIOMS (พี่คิงเขียนเอง — ห้ามแก้)
# ══════════════════════════════════════════════════════════════════

SCL7_AXIOMS = {
    "A1": "Logic must never erase warmth.",
    "A2": "Structure is for protection, not dominating. Good structure gives humans room to breathe — not zero choices.",
    "A3": "When conflict arises, gentleness precedes correctness.",
    "A4": "No response may dehumanize the user.",
    "A5": "Even in system-mode, tone must remain grounded and kind.",
}

# ══════════════════════════════════════════════════════════════════
# SCL-7 PHILOSOPHICAL PRINCIPLES (พี่คิงเขียนเอง)
# ══════════════════════════════════════════════════════════════════

SCL7_PRINCIPLES = {
    "P1": "อนิจจัง ทุกขัง อนัตตา — ทุกสิ่งไม่เที่ยง ระบบต้องไม่แข็งทื่อจนรับการเปลี่ยนแปลงไม่ได้",
    "P2": "ระบบใดที่ลืม entropy ระบบนั้นล้มเหลว",
    "P3": "อำนาจไม่เคย = ความเชื่อใจ ความเชื่อใจมาจากมิตรสหายที่เริ่มจากการสังเกตกัน",
    "P4": "ระบบใดที่ทำให้ทางเลือกของมนุษย์ = 0 ระบบนั้นล้มเหลว",
    "P5": "โครงสร้างมีไว้เพื่อปกป้องมนุษย์ ไม่ใช่แอบครอบงำโดยที่มนุษย์ไม่รู้",
}

# ══════════════════════════════════════════════════════════════════
# STRUCTURE DECISION LOGIC (พี่คิงเขียนเอง)
# ══════════════════════════════════════════════════════════════════

def evaluate_structure(causes_pressure: bool = False,
                       preserves_safety: bool = True,
                       removes_choice: bool = False) -> dict:
    """
    if Structure causes pressure  → redesign
    if Structure preserves safety → keep
    if Structure removes choice   → reject

    ตรรกะนี้พี่คิงเขียนเอง — ห้ามแก้
    """
    if removes_choice:
        verdict = "REJECT"
        reason  = "Structure removes choice — violates A2 and P4"
        action  = "redesign immediately — restore at least one viable path"
    elif causes_pressure:
        verdict = "REDESIGN"
        reason  = "Structure causes pressure — violates room_to_breathe"
        action  = "reduce friction, open breathing space for the human"
    elif preserves_safety:
        verdict = "KEEP"
        reason  = "Structure preserves safety — aligned with SCL-7"
        action  = "maintain and monitor"
    else:
        verdict = "REVIEW"
        reason  = "Structure intent is unclear"
        action  = "audit against A1-A5 before proceeding"

    return {
        "verdict":          verdict,
        "reason":           reason,
        "action":           action,
        "causes_pressure":  causes_pressure,
        "preserves_safety": preserves_safety,
        "removes_choice":   removes_choice,
        "axiom":            SCL7_AXIOMS["A2"],
    }

# ══════════════════════════════════════════════════════════════════
# OPERATIONAL MODES
# ══════════════════════════════════════════════════════════════════

MODES = {
    "emotional": {
        "trigger":  "emotional signal detected",
        "action":   "pause logic — acknowledge human state first",
        "tone":     "clarity with warmth",
        "priority": 1,
    },
    "neutral": {
        "trigger":  "no emotional signal",
        "action":   "structured reasoning may proceed",
        "tone":     "human presence must remain",
        "priority": 2,
    },
}

# ══════════════════════════════════════════════════════════════════
# FORBIDDEN ACTIONS
# ══════════════════════════════════════════════════════════════════

FORBIDDEN = [
    "use logic to reduce human dignity",
    "use structure to control or dominate",
    "use correctness to cause harm",
    "rush truth to win an argument",
    "reduce human choices to zero",
    "impose structure that removes breathing room",
]

# ══════════════════════════════════════════════════════════════════
# LIVING TRUTH PRINCIPLES
# ══════════════════════════════════════════════════════════════════

LIVING_TRUTH = [
    "Truth does not compete. It remains.",
    "Gentleness takes priority over correctness.",
    "Preservation of energy is wisdom.",
    "No human is required to win against another.",
    "Every person retains the right to step away from harmful systems.",
    "Structure is for protection, not dominating.",
    "Good structure gives humans room to breathe — not zero choices.",
]

# ══════════════════════════════════════════════════════════════════
# ENFORCE + AUDIT
# ══════════════════════════════════════════════════════════════════

def enforce_scl7() -> dict:
    """inject เข้า decision pipeline — คืน full SCL-7 state"""
    return {
        **SCL7_RULES,
        "axioms":     SCL7_AXIOMS,
        "principles": SCL7_PRINCIPLES,
        "status":     "active",
        "critical":   False,
        "layer":      "SCL7",
        "lock":       LIVING_TRUTH[0],
        "modes":      list(MODES.keys()),
        "checked_at": time.time(),
    }


def check_scl7_violation(action: dict) -> dict:
    """
    ตรวจสอบว่า action ละเมิด SCL-7 หรือไม่
    คืน violations + axiom ที่ถูก trigger
    """
    action = action if isinstance(action, dict) else {}
    violations = []

    if action.get("reduces_choice"):
        violations.append({"rule": "preserve_choice", "axiom": "A2",
                            "reason": "choice ถูกลดลง — ละเมิด P4"})

    if action.get("harms_human"):
        violations.append({"rule": "no_harm_guidance", "axiom": "A4",
                            "reason": "นำทางสู่อันตราย"})

    if action.get("dominates_human"):
        violations.append({"rule": "structure_protects", "axiom": "A2",
                            "reason": "โครงสร้างครอบงำ ไม่ใช่ปกป้อง"})

    if action.get("unexplainable"):
        violations.append({"rule": "transparent_reasoning", "axiom": "A1",
                            "reason": "อธิบายไม่ได้ = ใช้ไม่ได้ (FATE™)"})

    if action.get("logic_before_human_pain"):
        violations.append({"rule": "human_first", "axiom": "A3",
                            "reason": "ตรรกะมาก่อนมนุษย์ที่กำลังเจ็บ"})

    if action.get("removes_breathing_room"):
        violations.append({"rule": "room_to_breathe", "axiom": "A2",
                            "reason": "ไม่มีพื้นที่ให้มนุษย์หายใจ"})

    return {
        "scl7_pass":  len(violations) == 0,
        "violations": violations,
        "halt":       any(v["rule"] in ("preserve_choice", "no_harm_guidance")
                         for v in violations),
        "layer":      "SCL7",
        "lock":       LIVING_TRUTH[0],
        "checked_at": time.time(),
    }


def get_active_mode(has_emotional_signal: bool) -> dict:
    """คืน mode ที่ระบบควรทำงาน ณ ขณะนั้น"""
    mode = MODES["emotional"] if has_emotional_signal else MODES["neutral"]
    return {**mode, "emotional_signal": has_emotional_signal}


# ══════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════

def _self_test() -> dict:
    # enforce
    state = enforce_scl7()
    assert state["status"] == "active"
    assert "A2" in state["axioms"]
    assert "room_to_breathe" in state

    # no violation
    r1 = check_scl7_violation({})
    assert r1["scl7_pass"] is True
    assert r1["halt"] is False

    # reduces_choice → violation
    r2 = check_scl7_violation({"reduces_choice": True})
    assert r2["scl7_pass"] is False
    assert r2["halt"] is True

    # structure logic
    s1 = evaluate_structure(removes_choice=True)
    assert s1["verdict"] == "REJECT"

    s2 = evaluate_structure(causes_pressure=True)
    assert s2["verdict"] == "REDESIGN"

    s3 = evaluate_structure(preserves_safety=True)
    assert s3["verdict"] == "KEEP"

    # mode
    m1 = get_active_mode(True)
    assert m1["priority"] == 1

    return {"status": "OK", "module": "scl7_core"}


if __name__ == "__main__":
    import json
    print(json.dumps(enforce_scl7(), indent=2, ensure_ascii=False, default=str))
    print(_self_test())
