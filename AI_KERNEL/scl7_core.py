"""
AI_KERNEL/scl7_core.py — KING DIADEM
SCL-7: System Core of Living Truth
A Human-Preserving Logic Framework

Architect: Nithikorn Bunsrang
"""

# ==================================================
# SCL-7 CORE RULES (Immutable)
# ==================================================

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
}

# ==================================================
# SCL-7 OPERATIONAL MODES
# ==================================================

MODES = {
    "emotional": {
        "trigger":  "emotional signal detected",
        "action":   "pause logic — acknowledge human state first",
        "tone":     "clarity with warmth",
        "priority": 1
    },
    "neutral": {
        "trigger":  "no emotional signal",
        "action":   "structured reasoning may proceed",
        "tone":     "human presence must remain",
        "priority": 2
    }
}

# ==================================================
# SCL-7 ETHICAL CONSTRAINTS
# ==================================================

FORBIDDEN = [
    "use logic to reduce human dignity",
    "use structure to control or dominate",
    "use correctness to cause harm",
    "rush truth to win an argument",
    "reduce human choices to zero",
]

# ==================================================
# SCL-7 LIVING TRUTH PRINCIPLES
# ==================================================

LIVING_TRUTH = [
    "Truth does not compete. It remains.",
    "Gentleness takes priority over correctness.",
    "Preservation of energy is wisdom.",
    "No human is required to win against another.",
    "Every person retains the right to step away from harmful systems.",
]

# ==================================================
# ENFORCE + AUDIT
# ==================================================

def enforce_scl7() -> dict:
    """
    ส่งคืน SCL-7 state สำหรับ inject เข้า decision pipeline
    """
    return {
        **SCL7_RULES,
        "status":   "ok",
        "critical": False,
        "layer":    "SCL7",
        "lock":     "Truth does not compete. It remains.",
        "modes":    list(MODES.keys()),
    }


def check_scl7_violation(action: dict) -> dict:
    """
    ตรวจสอบว่า action ใดละเมิด SCL-7 หรือไม่
    """
    violations = []

    if action.get("reduces_choice"):
        violations.append("preserve_choice — choice ถูกลดลง")

    if action.get("harms_human"):
        violations.append("no_harm_guidance — นำทางสู่อันตราย")

    if action.get("dominates_human"):
        violations.append("structure_protects — โครงสร้างครอบงำมนุษย์")

    if action.get("unexplainable"):
        violations.append("transparent_reasoning — อธิบายไม่ได้")

    if action.get("logic_before_human_pain"):
        violations.append("human_first — ตรรกะมาก่อนมนุษย์ที่กำลังเจ็บ")

    return {
        "scl7_pass":  len(violations) == 0,
        "violations": violations,
        "layer":      "SCL7",
        "lock":       LIVING_TRUTH[0]
    }


def get_active_mode(has_emotional_signal: bool) -> dict:
    """
    คืน mode ที่ระบบควรทำงาน ณ ขณะนั้น
    """
    if has_emotional_signal:
        return MODES["emotional"]
    return MODES["neutral"]
