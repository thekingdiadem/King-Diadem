# AI_KERNEL/belief_core.py
"""
KING DIADEM — Belief Core v2.0
FATE™ Axiom Enforcement Layer

Article B-1 : Choice(t) >= 1 → collapse = False
Article B-2 : Survival floor before all logic
Article B-3 : Emotion is signal, not bug
Article B-4 : Truth is platform-independent
Article B-5 : Authority that zeroes choice = null

self_test() → True หมายระบบพร้อม
"""

from __future__ import annotations
import time
from typing import Optional

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
_VERSION = "2.0.0"

_SURVIVAL_FLOOR_KEYS = ("food", "water", "shelter", "safety")

# ระดับ entropy ที่ถือว่า choice กำลังจะ collapse
_ENTROPY_DANGER  = 75.0   # เริ่มเตือน
_ENTROPY_CRISIS  = 90.0   # SYSTEM_PAUSE

# ระดับ resource ที่ถือว่า survival floor พัง
_RESOURCE_FLOOR  = 15.0

# ─────────────────────────────────────────────
# CORE BELIEF REGISTRY — deterministic, no random
# ─────────────────────────────────────────────
BELIEF_CORE: dict = {
    "choice_gt_zero":          True,   # B-1
    "survival_floor_first":    True,   # B-2
    "emotion_is_signal":       True,   # B-3
    "truth_platform_independent": True, # B-4
    "nature_alignment":        True,   # B-5
    "authority_null_at_zero":  True,   # B-3 extension
    "silence_when_choice_exists": True, # Layer 4
}

# ─────────────────────────────────────────────
# ARTICLE AUDIT DICT
# ─────────────────────────────────────────────
ARTICLE_AUDIT: dict = {
    "B-1": "Choice(t) >= 1 → collapse = False | Choice = 0 → system failed, not human",
    "B-2": "Survival floor (food/water/shelter/safety) before all logic",
    "B-3": "Emotion is signal of meaning — not a bug to suppress",
    "B-4": "Truth exists independent of brand, platform, or authority",
    "B-5": "Authority that reduces Choice to 0 is structurally null — no argument needed",
    "B-6": "A good system stays silent when choice still exists",
}

# ─────────────────────────────────────────────
# AUDIT — เช็คสถานะ context ก่อน LLM
# ─────────────────────────────────────────────
def audit(context: Optional[dict] = None) -> dict:
    """
    รับ context dict (entropy, resource, stability, food, water, shelter, safety)
    คืน audit report พร้อม flags สำหรับ pipeline

    Returns:
        {
            "choice_alive":      bool,   # True = Choice >= 1
            "survival_ok":       bool,   # True = floor intact
            "pause_required":    bool,   # True = ห้ามส่ง LLM ต่อ
            "crisis_level":      str,    # "ok" | "warn" | "critical"
            "violated_articles": list,   # articles ที่ถูก violate
            "belief_snapshot":   dict,   # snapshot ณ เวลานี้
            "audit_ts":          int,
            "message":           str,    # human-readable summary
        }
    """
    ctx = context or {}
    violations: list[str] = []
    crisis_level = "ok"

    # ── B-2: Survival floor ──────────────────────────────────────
    survival_ok = True
    floor_broken = [k for k in _SURVIVAL_FLOOR_KEYS if ctx.get(k) is False]
    resource = float(ctx.get("resource", 50.0))

    if floor_broken or resource <= _RESOURCE_FLOOR:
        survival_ok = False
        violations.append("B-2")
        crisis_level = "warn"

    # ── B-1: Choice alive (via entropy proxy) ────────────────────
    entropy   = float(ctx.get("entropy", 40.0))
    stability = float(ctx.get("stability", 60.0))
    choice_score = max(0.0, 100.0 - entropy) * (stability / 100.0)
    choice_alive = choice_score > 5.0   # threshold: Choice still exists

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
    authority_override = ctx.get("authority_override", False)
    if authority_override and not choice_alive:
        violations.append("B-5")

    # ── pause logic ───────────────────────────────────────────────
    pause_required = crisis_level == "critical" or (
        not survival_ok and entropy >= _ENTROPY_DANGER
    )

    # ── message ───────────────────────────────────────────────────
    if crisis_level == "critical":
        message = (
            "⚠ SYSTEM_PAUSE — Choice กำลังถึงศูนย์ "
            "ระบบต้องจัดการ Survival Floor ก่อน ไม่ใช่ตัดสินใจ"
        )
    elif crisis_level == "warn":
        message = (
            "⚡ WARNING — Entropy สูงหรือ Resource ต่ำ "
            "แนะนำให้ prioritize ความอยู่รอดก่อน"
        )
    else:
        message = "✓ Belief core stable — Choice alive, floor intact"

    return {
        "choice_alive":      choice_alive,
        "choice_score":      round(choice_score, 2),
        "survival_ok":       survival_ok,
        "pause_required":    pause_required,
        "crisis_level":      crisis_level,
        "violated_articles": violations,
        "belief_snapshot":   {**BELIEF_CORE},
        "article_audit":     ARTICLE_AUDIT,
        "audit_ts":          int(time.time() * 1000),
        "message":           message,
        "entropy_read":      entropy,
        "resource_read":     resource,
        "stability_read":    stability,
    }


# ─────────────────────────────────────────────
# ENFORCE — กรองผล LLM ก่อน return ออก
# ─────────────────────────────────────────────
def enforce(result: dict, audit_report: Optional[dict] = None) -> dict:
    """
    รับ result dict จาก pipeline
    ถ้า audit บอก pause → inject SYSTEM_PAUSE และ block response
    ถ้า ok → แนบ belief_audit เข้า result แล้ว return ต่อ

    Article B-6: ถ้า choice ยังมีอยู่ ระบบควรเงียบ (ไม่ override)
    """
    if audit_report is None:
        # ดึง context จาก result ถ้ามี
        human_state = result.get("governance", {}).get("human_state", {})
        pattern     = result.get("pattern", {})
        ctx = {**human_state, **pattern}
        audit_report = audit(ctx)

    # แนบ audit เข้า result เสมอ (FATE™ transparency)
    result["belief_audit"] = {
        "choice_alive":      audit_report["choice_alive"],
        "choice_score":      audit_report["choice_score"],
        "survival_ok":       audit_report["survival_ok"],
        "crisis_level":      audit_report["crisis_level"],
        "violated_articles": audit_report["violated_articles"],
        "message":           audit_report["message"],
        "article_audit":     audit_report["article_audit"],
        "audit_ts":          audit_report["audit_ts"],
    }

    # SYSTEM_PAUSE path
    if audit_report["pause_required"]:
        result["status"]   = "SYSTEM_PAUSE"
        result["paused_by"] = "belief_core"
        result["pause_reason"] = audit_report["message"]

        # override ai_response ด้วย survival-first message
        violated = audit_report["violated_articles"]
        if "B-1" in violated:
            pause_msg = (
                "🔴 SYSTEM_PAUSE — ระบบตรวจพบว่าทางเลือกของคุณกำลังถึงศูนย์\n\n"
                "ก่อนตัดสินใจใดๆ ต้องจัดการก่อน:\n"
                "1. ความปลอดภัยพื้นฐาน (อาหาร น้ำ ที่พัก)\n"
                "2. ลด entropy — หยุดพักก่อนถ้าทำได้\n"
                "3. ระบุทางออกอย่างน้อย 1 ทาง ก่อนเดินหน้า\n\n"
                "Choice(t) >= 1 → ระบบจะกลับมา | Choice = 0 → ล้มเหลวที่โครงสร้าง ไม่ใช่ที่คุณ\n"
                "— KING DIADEM FATE™ B-1"
            )
        elif "B-2" in violated:
            pause_msg = (
                "🟡 WARNING — Survival Floor ไม่ครบ\n\n"
                "ระบบจะไม่แนะนำการตัดสินใจเชิงกลยุทธ์ก่อนที่:\n"
                "อาหาร / น้ำ / ที่พัก / ความปลอดภัย จะได้รับการจัดการก่อน\n\n"
                "รอดแล้วรู้ ดีกว่ารู้แล้วไม่รอด\n"
                "— KING DIADEM FATE™ B-2"
            )
        else:
            pause_msg = audit_report["message"]

        result["ai_response"] = pause_msg

    return result


# ─────────────────────────────────────────────
# FATE AUDIT SNAPSHOT — แนบกับทุก response
# ─────────────────────────────────────────────
def get_belief_audit() -> dict:
    """Return static belief + article audit สำหรับแนบ FATE™ transparency"""
    return {
        "belief_core":   {**BELIEF_CORE},
        "article_audit": {**ARTICLE_AUDIT},
        "version":       _VERSION,
        "axiom_lock":    "Choice(t) >= 1 → collapse = False",
        "fate_lock":     "Fail less. Harm less. Restore more.",
    }


# ─────────────────────────────────────────────
# SELF TEST
# ─────────────────────────────────────────────
def self_test() -> bool:
    """
    ตรวจสอบว่า belief_core ทำงานถูกต้อง
    Return True = pass | False = fail
    """
    errors: list[str] = []

    # Test 1: normal context → ok
    r1 = audit({"entropy": 30, "resource": 60, "stability": 70})
    if r1["crisis_level"] != "ok":
        errors.append(f"T1 fail: expected ok got {r1['crisis_level']}")
    if not r1["choice_alive"]:
        errors.append("T1 fail: choice_alive should be True")

    # Test 2: critical entropy → pause
    r2 = audit({"entropy": 95, "resource": 10, "stability": 5})
    if not r2["pause_required"]:
        errors.append("T2 fail: pause_required should be True at critical entropy")
    if "B-1" not in r2["violated_articles"]:
        errors.append("T2 fail: B-1 should be violated")

    # Test 3: low resource → B-2 violation
    r3 = audit({"entropy": 40, "resource": 10, "stability": 60})
    if "B-2" not in r3["violated_articles"]:
        errors.append("T3 fail: B-2 should be violated at low resource")

    # Test 4: enforce injects belief_audit
    dummy_result = {
        "ai_response": "test",
        "pattern": {"entropy": 30, "resource": 60, "stability": 70},
    }
    r4 = enforce(dummy_result)
    if "belief_audit" not in r4:
        errors.append("T4 fail: belief_audit missing from enforced result")

    # Test 5: enforce SYSTEM_PAUSE on critical
    dummy_critical = {
        "ai_response": "กำลังตอบ",
        "pattern": {"entropy": 95, "resource": 5, "stability": 5},
    }
    r5 = enforce(dummy_critical)
    if r5.get("status") != "SYSTEM_PAUSE":
        errors.append("T5 fail: should be SYSTEM_PAUSE")

    # Test 6: belief snapshot complete
    snap = get_belief_audit()
    for key in ("belief_core", "article_audit", "axiom_lock"):
        if key not in snap:
            errors.append(f"T6 fail: missing key {key}")

    if errors:
        for e in errors:
            print(f"  [belief_core self_test] ✗ {e}")
        return False

    print(f"  [belief_core self_test] ✓ all 6 tests passed — v{_VERSION}")
    return True


# ─────────────────────────────────────────────
# MODULE INIT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    ok = self_test()
    print("belief_core:", "PASS" if ok else "FAIL")
