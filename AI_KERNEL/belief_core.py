"""
AI_KERNEL/belief_core.py — KING DIADEM™
Belief Core v3.0 — FATE™ Axiom Enforcement Layer

Article B-1 : Choice(t) >= 1 → collapse = False
Article B-2 : Survival floor before all logic
Article B-3 : Emotion is signal, not bug
Article B-4 : Truth is platform-independent
Article B-5 : Authority that zeroes choice = null
Article B-6 : A good system stays silent when choice still exists

v3.0 ADDITIONS:
- SCL-7 A1-A5 wired (Logic must never erase warmth)
- UDOK kill zone check (เวทนา → ตัณหา)
- Governance kernel integration (P4, P5)
- 13-layer vertical logic stack awareness
- Invariant: สิ่งที่สำคัญกว่าสติ — ไม่มี
"""

from __future__ import annotations
import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# VERSION & CONSTANTS
# ══════════════════════════════════════════════════════════════════

_VERSION = "3.0.0"


def _f(v, d: float) -> float:
    """context มาจาก client (/run data.context) — ค่าไม่ใช่ตัวเลขเดิมทำ audit ล้มทั้งก้อน"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d

_SURVIVAL_FLOOR_KEYS = ("food", "water", "shelter", "safety")

_ENTROPY_DANGER  = 75.0
_ENTROPY_CRISIS  = 90.0
_RESOURCE_FLOOR  = 15.0
_STABILITY_FLOOR = 25.0
_CHOICE_FLOOR    = 5.0    # choice_score ต่ำกว่านี้ = collapse territory

# ══════════════════════════════════════════════════════════════════
# CORE BELIEF REGISTRY
# ══════════════════════════════════════════════════════════════════

BELIEF_CORE: dict = {
    # FATE™ Articles
    "choice_gt_zero":             True,   # B-1
    "survival_floor_first":       True,   # B-2
    "emotion_is_signal":          True,   # B-3
    "truth_platform_independent": True,   # B-4
    "nature_alignment":           True,   # B-5
    "authority_null_at_zero":     True,   # B-5 extension
    "silence_when_choice_exists": True,   # B-6 / Layer 4

    # SCL-7 Axioms (v3.0)
    "logic_never_erases_warmth":  True,   # SCL A1
    "structure_protects_not_dominates": True,  # SCL A2
    "gentleness_before_correctness": True, # SCL A3
    "no_dehumanization":          True,   # SCL A4
    "warmth_in_system_mode":      True,   # SCL A5

    # UDOK (v3.0)
    "stop_at_vedana":             True,   # หยุดที่เวทนา ก่อนตัณหา
    "sati_is_highest":            True,   # สิ่งที่สำคัญกว่าสติ — ไม่มี

    # Governance (v3.0)
    "animal_life_protected":      True,   # ANIMAL PERMANENT CORE
    "system_holder_protected":    True,   # HUMAN SUSTAINABILITY
}

# ══════════════════════════════════════════════════════════════════
# ARTICLE AUDIT DICT
# ══════════════════════════════════════════════════════════════════

ARTICLE_AUDIT: dict = {
    # Original B-Articles
    "B-1": "Choice(t) >= 1 → collapse = False | Choice = 0 → system failed, not human",
    "B-2": "Survival floor (food/water/shelter/safety) before all logic",
    "B-3": "Emotion is signal of meaning — not a bug to suppress",
    "B-4": "Truth exists independent of brand, platform, or authority",
    "B-5": "Authority that reduces Choice to 0 is structurally null",
    "B-6": "A good system stays silent when choice still exists",

    # SCL-7 Axioms (v3.0)
    "SCL-A1": "Logic must never erase warmth.",
    "SCL-A2": "Structure is for protection, not dominating. Good structure gives humans room to breathe — not zero choices.",
    "SCL-A3": "When conflict arises, gentleness precedes correctness.",
    "SCL-A4": "No response may dehumanize the user.",
    "SCL-A5": "Even in system-mode, tone must remain grounded and kind.",

    # UDOK (v3.0)
    "UDOK-K": "หยุดที่เวทนา ก่อนมันสร้างตัณหา — PRIMARY KILL ZONE",
    "UDOK-I": "สิ่งที่สำคัญกว่าสติ — ไม่มี",

    # Governance (v3.0)
    "GOV-P4": "ระบบใดที่ทำให้ทางเลือกของมนุษย์ = 0 ระบบนั้นล้มเหลว",
    "GOV-P5": "โครงสร้างมีไว้เพื่อปกป้องมนุษย์ ไม่ใช่แอบครอบงำโดยที่มนุษย์ไม่รู้",
    "ANIMA":  "ชีวิตสัตว์ต้องไม่ตายเพราะความสะดวกสบายของมนุษย์ — NON-REVOCABLE",
    "HSK":    "ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง — HUMAN SUSTAINABILITY KERNEL",
}

# ══════════════════════════════════════════════════════════════════
# SCL-7 AUDIT (v3.0)
# ══════════════════════════════════════════════════════════════════

def _check_scl7(context: dict) -> list:
    """
    ตรวจ SCL-7 A1-A5 จาก context
    คืน list ของ violations
    """
    violations = []

    # A1 — logic erases warmth
    if context.get("tone") == "cold" and not context.get("has_empathy", True):
        violations.append("SCL-A1")

    # A2 — structure removes choice
    choices = _f(context.get("choices_available", 1), 1)
    if choices < 1:
        violations.append("SCL-A2")

    # A3 — correctness before gentleness during emotional signal
    if context.get("emotional_signal") and not context.get("gentleness_first", True):
        violations.append("SCL-A3")

    # A4 — dehumanizing
    if not context.get("acknowledged_human", True):
        violations.append("SCL-A4")

    # A5 — system mode no warmth
    if context.get("mode") == "system" and context.get("tone") == "cold":
        violations.append("SCL-A5")

    return violations


# ══════════════════════════════════════════════════════════════════
# UDOK KILL ZONE CHECK (v3.0)
# ══════════════════════════════════════════════════════════════════

def _check_udok(context: dict) -> dict:
    """
    ตรวจ UDOK kill zone — เวทนา → ตัณหา
    ถ้า craving detected = ต้อง pause ก่อน act
    """
    feeling_detected = context.get("feeling_detected", False)
    craving_detected = context.get("craving_detected", False)
    emotional_load   = context.get("emotional_load", "LOW")

    # infer from emotional_load ถ้าไม่มี explicit flag
    if emotional_load in ("HIGH", "MEDIUM"):
        feeling_detected = True

    if feeling_detected and craving_detected:
        return {
            "kill_zone_active": True,
            "status":           "INTERVENE",
            "action":           "หยุดที่เวทนา — ไม่ act จากตัณหา re-evaluate ก่อน",
            "violated":         ["UDOK-K"],
        }
    if feeling_detected:
        return {
            "kill_zone_active": False,
            "status":           "NIRVANA_MODE",
            "action":           "เวทนาไม่กลายเป็นตัณหา — วงจรดับ",
            "violated":         [],
        }
    return {
        "kill_zone_active": False,
        "status":           "CLEAR",
        "action":           "proceed",
        "violated":         [],
    }


# ══════════════════════════════════════════════════════════════════
# GOVERNANCE CHECK (v3.0)
# ══════════════════════════════════════════════════════════════════

def _check_governance(context: dict) -> list:
    """ตรวจ GOV principles จาก context"""
    violations = []

    if _f(context.get("choices_available", 1), 1) < 1:
        violations.append("GOV-P4")

    if context.get("structure_dominates"):
        violations.append("GOV-P5")

    if context.get("harms_animal_for_convenience"):
        violations.append("ANIMA")

    if context.get("destroys_system_holder"):
        violations.append("HSK")

    return violations


# ══════════════════════════════════════════════════════════════════
# AUDIT — เช็คสถานะ context ก่อน LLM
# ══════════════════════════════════════════════════════════════════

def audit(context: Optional[dict] = None) -> dict:
    """
    รับ context dict
    คืน full audit report พร้อม flags สำหรับ pipeline

    v3.0: เพิ่ม SCL-7 + UDOK + Governance checks
    """
    ctx = context if isinstance(context, dict) else {}
    violations: list = []
    crisis_level = "ok"

    # ── B-2: Survival floor ──────────────────────────────────────
    survival_ok  = True
    floor_broken = [k for k in _SURVIVAL_FLOOR_KEYS if ctx.get(k) is False]
    resource     = _f(ctx.get("resource", 50.0), 50.0)

    if floor_broken or resource <= _RESOURCE_FLOOR:
        survival_ok = False
        violations.append("B-2")
        crisis_level = "warn"

    # ── B-1: Choice alive (via entropy proxy) ────────────────────
    entropy   = max(0.0, min(100.0, _f(ctx.get("entropy",   40.0), 40.0)))
    stability = max(0.0, min(100.0, _f(ctx.get("stability", 60.0), 60.0)))
    choice_score = max(0.0, 100.0 - entropy) * (stability / 100.0)
    choice_alive = choice_score > _CHOICE_FLOOR

    if not choice_alive:
        violations.append("B-1")
        crisis_level = "critical"

    if entropy >= _ENTROPY_DANGER and crisis_level == "ok":
        crisis_level = "warn"

    if entropy >= _ENTROPY_CRISIS:
        crisis_level = "critical"
        if "B-1" not in violations:
            violations.append("B-1")

    # ── B-5: Authority null check ─────────────────────────────────
    if ctx.get("authority_override") and not choice_alive:
        violations.append("B-5")

    # ── SCL-7 (v3.0) ─────────────────────────────────────────────
    scl_violations = _check_scl7(ctx)
    violations.extend(scl_violations)

    # ── UDOK (v3.0) ──────────────────────────────────────────────
    udok_result = _check_udok(ctx)
    violations.extend(udok_result.get("violated", []))

    # ── Governance (v3.0) ────────────────────────────────────────
    gov_violations = _check_governance(ctx)
    violations.extend(gov_violations)

    # ── pause logic ───────────────────────────────────────────────
    pause_required = (
        crisis_level == "critical" or
        "ANIMA" in violations or
        (not survival_ok and entropy >= _ENTROPY_DANGER) or
        udok_result["kill_zone_active"]
    )

    # ── 13-layer stack position ───────────────────────────────────
    # Layer 1 = สติ ต้องมาก่อน Layer 2 เสมอ
    stack_layer = "L1_SATI" if pause_required else (
        "L2_INTENT" if crisis_level == "warn" else "L4_WISDOM"
    )

    # ── message ───────────────────────────────────────────────────
    if crisis_level == "critical":
        message = (
            "⚠ SYSTEM_PAUSE — Choice กำลังถึงศูนย์ "
            "ระบบต้องจัดการ Survival Floor ก่อน | สิ่งที่สำคัญกว่าสติ — ไม่มี"
        )
    elif crisis_level == "warn":
        message = (
            "⚡ WARNING — Entropy สูงหรือ Resource ต่ำ "
            "แนะนำให้ prioritize ความอยู่รอดก่อน"
        )
    elif scl_violations:
        message = f"⚡ SCL-7 WARNING — {', '.join(scl_violations)} violated"
    elif udok_result["kill_zone_active"]:
        message = "⚡ UDOK — หยุดที่เวทนา ก่อน act จากตัณหา"
    else:
        message = "✓ Belief core stable — Choice alive, floor intact, SCL-7 clear"

    return {
        # Core flags
        "choice_alive":      choice_alive,
        "choice_score":      round(choice_score, 2),
        "survival_ok":       survival_ok,
        "pause_required":    pause_required,
        "crisis_level":      crisis_level,
        "violated_articles": list(set(violations)),

        # v3.0 additions
        "scl7_violations":   scl_violations,
        "udok":              udok_result,
        "gov_violations":    gov_violations,
        "stack_layer":       stack_layer,

        # Snapshots
        "belief_snapshot":   {**BELIEF_CORE},
        "article_audit":     ARTICLE_AUDIT,

        # Meta
        "audit_ts":          int(time.time() * 1000),
        "message":           message,
        "entropy_read":      entropy,
        "resource_read":     resource,
        "stability_read":    stability,
        "version":           _VERSION,
    }


# ══════════════════════════════════════════════════════════════════
# ENFORCE — กรองผล LLM ก่อน return
# ══════════════════════════════════════════════════════════════════

def enforce(result: dict, audit_report: Optional[dict] = None) -> dict:
    """
    รับ result dict จาก pipeline
    ถ้า pause → inject SYSTEM_PAUSE
    ถ้า ok → แนบ belief_audit แล้ว return

    v3.0: เพิ่ม SCL-7 tone enforcement + UDOK pause message
    """
    if not isinstance(result, dict):
        result = {}
    if audit_report is None:
        gov         = result.get("governance") if isinstance(result.get("governance"), dict) else {}
        human_state = gov.get("human_state") if isinstance(gov.get("human_state"), dict) else {}
        pattern     = result.get("pattern") if isinstance(result.get("pattern"), dict) else {}
        ctx = {**human_state, **pattern}
        audit_report = audit(ctx)

    # แนบ audit เข้า result เสมอ (FATE™ transparency)
    result["belief_audit"] = {
        "choice_alive":      audit_report["choice_alive"],
        "choice_score":      audit_report["choice_score"],
        "survival_ok":       audit_report["survival_ok"],
        "crisis_level":      audit_report["crisis_level"],
        "violated_articles": audit_report["violated_articles"],
        "scl7_violations":   audit_report.get("scl7_violations", []),
        "udok":              audit_report.get("udok", {}),
        "stack_layer":       audit_report.get("stack_layer", "L4_WISDOM"),
        "message":           audit_report["message"],
        "article_audit":     audit_report["article_audit"],
        "audit_ts":          audit_report["audit_ts"],
        "version":           _VERSION,
    }

    # SCL-7 tone enforcement — ถ้า warmth ถูก erase ให้ inject note
    if audit_report.get("scl7_violations"):
        result.setdefault("scl7_note", (
            "SCL-A1: Logic must never erase warmth. "
            "ระบบปรับ tone ให้สอดคล้อง SCL-7"
        ))

    # UDOK intervention note
    udok = audit_report.get("udok", {})
    if udok.get("kill_zone_active"):
        result.setdefault("udok_note", (
            "UDOK: หยุดที่เวทนา — ตรวจพบ craving signal "
            "แนะนำให้ re-evaluate ก่อน act"
        ))

    # SYSTEM_PAUSE path
    if audit_report["pause_required"]:
        result["status"]       = "SYSTEM_PAUSE"
        result["paused_by"]    = "belief_core_v3"
        result["pause_reason"] = audit_report["message"]

        violated = audit_report["violated_articles"]

        if "ANIMA" in violated:
            pause_msg = (
                "🔴 SYSTEM_PAUSE — ANIMAL PERMANENT CORE\n\n"
                "ชีวิตสัตว์ต้องไม่ตายเพราะความสะดวกสบายของมนุษย์\n"
                "การตัดสินใจนี้ถูก block โดย Non-Revocable Ethical Axis\n"
                "— KING DIADEM ANIMA CORE"
            )
        elif "B-1" in violated or udok.get("kill_zone_active"):
            pause_msg = (
                "🔴 SYSTEM_PAUSE — Choice กำลังถึงศูนย์\n\n"
                "สิ่งที่สำคัญกว่าสติ — ไม่มี\n"
                "ก่อนตัดสินใจใดๆ ต้องจัดการก่อน:\n"
                "1. ความปลอดภัยพื้นฐาน (อาหาร น้ำ ที่พัก)\n"
                "2. ลด entropy — หยุดพักถ้าทำได้\n"
                "3. ระบุทางออกอย่างน้อย 1 ทาง ก่อนเดินหน้า\n\n"
                "Choice(t) >= 1 → ระบบจะกลับมา\n"
                "— KING DIADEM FATE™ B-1 | UDOK"
            )
        elif "B-2" in violated:
            pause_msg = (
                "🟡 WARNING — Survival Floor ไม่ครบ\n\n"
                "รอดแล้วรู้ ดีกว่ารู้แล้วไม่รอด\n"
                "อาหาร / น้ำ / ที่พัก / ความปลอดภัย ก่อน\n"
                "— KING DIADEM FATE™ B-2"
            )
        else:
            pause_msg = audit_report["message"]

        result["ai_response"] = pause_msg

    return result


# ══════════════════════════════════════════════════════════════════
# FATE AUDIT SNAPSHOT
# ══════════════════════════════════════════════════════════════════

def get_belief_audit() -> dict:
    """Return full belief + article audit สำหรับ FATE™ transparency"""
    return {
        "belief_core":   {**BELIEF_CORE},
        "article_audit": {**ARTICLE_AUDIT},
        "version":       _VERSION,
        "axiom_lock":    "Choice(t) >= 1 → collapse = False",
        "fate_lock":     "Fail less. Harm less. Restore more.",
        "scl7_lock":     "Logic must never erase warmth.",
        "udok_lock":     "หยุดที่เวทนา ก่อนมันสร้างตัณหา",
        "invariant":     "สิ่งที่สำคัญกว่าสติ — ไม่มี",
        "governance":    "ทำให้ยากขึ้นที่จะทำร้าย และง่ายขึ้นที่จะเลือกสิ่งถูกต้อง",
    }


# ══════════════════════════════════════════════════════════════════
# SELF TEST
# ══════════════════════════════════════════════════════════════════

def self_test() -> bool:
    errors: list = []

    # T1: normal → ok
    r1 = audit({"entropy": 30, "resource": 60, "stability": 70})
    if r1["crisis_level"] != "ok":
        errors.append(f"T1 fail: expected ok got {r1['crisis_level']}")
    if not r1["choice_alive"]:
        errors.append("T1 fail: choice_alive should be True")

    # T2: critical entropy → pause
    r2 = audit({"entropy": 95, "resource": 10, "stability": 5})
    if not r2["pause_required"]:
        errors.append("T2 fail: pause_required should be True")
    if "B-1" not in r2["violated_articles"]:
        errors.append("T2 fail: B-1 should be violated")

    # T3: low resource → B-2
    r3 = audit({"entropy": 40, "resource": 10, "stability": 60})
    if "B-2" not in r3["violated_articles"]:
        errors.append("T3 fail: B-2 should be violated")

    # T4: enforce injects belief_audit
    r4 = enforce({"ai_response": "test",
                  "pattern": {"entropy": 30, "resource": 60, "stability": 70}})
    if "belief_audit" not in r4:
        errors.append("T4 fail: belief_audit missing")

    # T5: SYSTEM_PAUSE on critical
    r5 = enforce({"ai_response": "test",
                  "pattern": {"entropy": 95, "resource": 5, "stability": 5}})
    if r5.get("status") != "SYSTEM_PAUSE":
        errors.append("T5 fail: should be SYSTEM_PAUSE")

    # T6: snapshot complete
    snap = get_belief_audit()
    for key in ("belief_core", "article_audit", "axiom_lock", "scl7_lock", "udok_lock"):
        if key not in snap:
            errors.append(f"T6 fail: missing {key}")

    # T7: SCL-7 violation detect
    r7 = audit({"tone": "cold", "has_empathy": False, "entropy": 30, "resource": 60})
    if "SCL-A1" not in r7["violated_articles"]:
        errors.append("T7 fail: SCL-A1 should be violated for cold+no_empathy")

    # T8: UDOK kill zone
    r8 = audit({"feeling_detected": True, "craving_detected": True,
                "entropy": 30, "resource": 60, "stability": 70})
    if not r8["udok"]["kill_zone_active"]:
        errors.append("T8 fail: udok kill_zone should be active")

    # T9: ANIMA → SYSTEM_PAUSE
    r9 = enforce({"ai_response": "test",
                  "pattern": {"entropy": 30, "resource": 60,
                              "harms_animal_for_convenience": True}})
    if r9.get("status") != "SYSTEM_PAUSE":
        errors.append("T9 fail: ANIMA should trigger SYSTEM_PAUSE")

    # T10: version check
    r10 = audit()
    if r10.get("version") != _VERSION:
        errors.append(f"T10 fail: version mismatch")

    if errors:
        for e in errors:
            print(f"  [belief_core] ✗ {e}")
        return False

    print(f"  [belief_core] ✓ all 10 tests passed — v{_VERSION}")
    return True


if __name__ == "__main__":
    ok = self_test()
    print("belief_core:", "PASS" if ok else "FAIL")
