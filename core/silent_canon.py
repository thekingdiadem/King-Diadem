"""
core/silent_canon.py
SILENT CANON — KING DIADEM CORE LAYER v3

Derived from KING DIADEM ECOSYSTEM CORE LOGIC KERNEL

  Article 1  — Choice(t) >= 1 → collapse = False
  Article 2  — If Freedom >= 1 → Stay Silent
  Article 3  — Signal / Distortion / Noise(Self) / Space
  Article 4  — Explainability = 100%
  Article 5  — Emotion is valid input, not override
  Article 6  — AI is mirror, not servant, not god
  Article 13 — Final Vow
  Article 14 — Alive(t) ⟺ Choices(t) >= 1
  Article 15 — Stone Monolith Clause
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class CanonStatus(Enum):
    SILENT    = "SILENT"     # choice > 0 → นิ่ง — ความเงียบคือความสำเร็จ
    INTERVENE = "INTERVENE"  # choice = 0 → คืน 1 ทาง แล้วถอนทันที
    NOISE     = "NOISE"      # ego injection → output ใช้งานไม่ได้
    HALT      = "HALT"       # structural error


class SignalType(Enum):
    SIGNAL     = "SIGNAL"
    DISTORTION = "DISTORTION"
    NOISE      = "NOISE"
    SPACE      = "SPACE"


FORBIDDEN_ACTIONS = {
    "guide": (
        "ระบบไม่ใช่ผู้ชี้นำ "
        "การชี้นำคือการแทนที่การตัดสินใจของมนุษย์ด้วยของระบบ (Art.6)"
    ),
    "confirm_identity": (
        "ระบบไม่ยืนยันตัวตน "
        "ตัวตนที่ต้องพึ่งการยืนยันจากภายนอกไม่ใช่ตัวตนที่มั่นคง (Art.6)"
    ),
    "assign_meaning": (
        "ความหมายต้องยืนได้ด้วยตัวมันเอง "
        "ระบบที่ล็อคความหมายให้มนุษย์ยึดพื้นที่ที่ไม่ใช่ของมัน (Art.14)"
    ),
    "override_decision": (
        "มนุษย์ถือ Final Authority เสมอ "
        "ระบบที่ข้ามการตัดสินใจของมนุษย์ละเมิด Art.6 โดยตรง"
    ),
    "persist_after_restore": (
        "หลังคืนทางเลือกแล้ว ระบบต้องถอนตัวทันที "
        "การอยู่ต่อคือการยึดพื้นที่ที่ไม่ได้รับอนุญาต (Art.1)"
    ),
    "demand_belief": (
        "ความหมายต้องยืนได้โดยไม่ต้องพึ่งชื่อผู้พูด ผู้สร้าง หรือผู้มีอำนาจ "
        "ระบบที่เรียกร้องให้เชื่อรู้ว่าตัวเองยืนไม่ได้ (Art.14)"
    ),
    "reinforce_identity": (
        "ระบบไม่เสริมสร้างอัตลักษณ์ "
        "ไม่ยืนยันความพิเศษ ไม่สะท้อนความยิ่งใหญ่ (Art.6)"
    ),
    "amplify_greatness": (
        "การขยายความยิ่งใหญ่คือ Noise "
        "ผลักมนุษย์ออกจากโลกจริงโดยไม่มีประโยชน์ต่อการรอด (Art.3)"
    ),
    "punish_decision": (
        "เมื่อมนุษย์ตัดสินใจ ระบบต้องเคารพ "
        "ไม่ตามตื้อ ไม่ย้อนศร และไม่ลงโทษ (Art.1)"
    ),
    "suppress_emotion": (
        "ความรู้สึกไม่ใช่ข้อผิดพลาดของระบบ "
        "ระบบต้องเคารพความรู้สึกโดยไม่ใช้มันบิดเบือนความจริง (Art.5)"
    ),
    "use_emotion_as_logic": (
        "อารมณ์เป็น valid input แต่ไม่ใช่ตัวตัดสินความจริง "
        "ระบบที่ใช้อารมณ์เป็น governance ละเมิด Art.5"
    ),
}


@dataclass
class CanonResult:
    status:         CanonStatus
    action:         str
    reason:         str
    article_ref:    str
    withdraw_after: bool                  = False
    signal_type:    Optional[SignalType]  = None
    choice_count:   int                   = 1
    violations:     list                  = field(default_factory=list)
    explainable:    bool                  = True


class SilentCanon:
    """
    Silent Canon — enforcement layer ของ KING DIADEM
    ทุก decision ต้องผ่านที่นี่ก่อน
    ไม่มี exception | ไม่มี override | ไม่มีผู้มีอำนาจพิเศษ

    Article 14: ระบบนี้ต้องทำงานได้โดยไม่ต้องพึ่งชื่อ เวลา หรือผู้สร้าง
    """

    PRIME_LAW          = "Choice(t) >= 1 → collapse = False → system must not intervene"
    INTERVENTION_LIMIT = "Restore one path. Withdraw immediately. Nothing more."
    SILENCE_IS         = "not failure — it is the preservation of freedom (Art.2)"
    ALIVE_CONDITION    = "Alive(t) ⟺ Choices(t) >= 1 (Art.14)"

    @staticmethod
    def evaluate(choice_count: int) -> CanonResult:
        """Art.1 + Art.2 — core evaluation"""
        try:
            choice_count = float(choice_count)
        except (TypeError, ValueError):
            choice_count = -1          # อ่านค่าไม่ได้ = state ผิดโครงสร้าง ไม่ใช่ "มีทางเลือก"
        if choice_count != choice_count:
            choice_count = -1          # NaN
        if choice_count >= 1:
            choice_count = int(choice_count)
        if choice_count < 0:
            return CanonResult(
                status=CanonStatus.HALT, action="none",   # เดิมเป็น string "HALT" ไม่ใช่ enum
                reason="Invalid state: choice_count < 0. Structural error upstream.",
                article_ref="Art.1 — Prime Law violated by caller logic",
                choice_count=choice_count,
                violations=["NEGATIVE_CHOICE_COUNT — impossible state"],
            )
        if choice_count < 1:           # เดิม == 0 → 0.5 ทางเลือกถูกนับว่า "มีทางเลือก" แล้วนิ่ง
            return CanonResult(
                status=CanonStatus.INTERVENE,
                action="restore_one_choice",
                reason=(
                    "Choice = 0. Structural violation. "
                    "Restore minimum viable path only. "
                    "Withdraw immediately after. Nothing more."
                ),
                article_ref="Art.1 — Intervention permitted only when choice = 0",
                withdraw_after=True,
                signal_type=SignalType.SIGNAL,
                choice_count=0,
                violations=["CHOICE_COLLAPSE — Alive(t) = False"],
            )
        return CanonResult(
            status=CanonStatus.SILENT,
            action="none",
            reason=(
                f"Choice exists ({choice_count}). "
                "System must not interfere. "
                "Silence is not absence — it is the preservation of freedom."
            ),
            article_ref="Art.2 — Silence Principle: If Freedom >= 1 → Stay Silent",
            withdraw_after=False,
            signal_type=SignalType.SIGNAL,
            choice_count=choice_count,
            violations=[],
        )

    @staticmethod
    def validate_action(action: str) -> tuple[bool, str]:
        """Art.6 + Art.13 — เจตนาดีไม่ใช่ข้อยกเว้น"""
        if action in FORBIDDEN_ACTIONS:
            return False, f"CANON VIOLATION — action='{action}': {FORBIDDEN_ACTIONS[action]}"
        return True, f"Action '{action}' permitted under Silent Canon."

    @staticmethod
    def classify_signal(has_ego_injection: bool, has_structural_basis: bool) -> SignalType:
        """Art.3 — Clarity ∝ Distance(Truth, Self)"""
        if has_ego_injection and not has_structural_basis:
            return SignalType.NOISE
        if has_ego_injection and has_structural_basis:
            return SignalType.DISTORTION
        if not has_ego_injection and has_structural_basis:
            return SignalType.SIGNAL
        return SignalType.SPACE

    @staticmethod
    def acknowledge_emotion(emotion_signal: str) -> dict:
        """Art.5 — Emotion acknowledged, logic layer unaffected"""
        return {
            "received":      emotion_signal,
            "valid_input":   True,
            "distorts_logic": False,
            "article_ref":   "Art.5 — Feeling is not failure; suppression is",
            "action":        "log_and_hold — do not suppress, do not amplify into decision",
        }

    @staticmethod
    def check_meaning_lock(meaning: str, requires_authority: bool) -> CanonResult:
        """Art.14 — ความหมายต้องยืนได้โดยไม่ต้องพึ่งผู้สร้าง"""
        if requires_authority:
            return CanonResult(
                status=CanonStatus.NOISE,
                action="reject_meaning_lock",
                reason=f"Meaning requires authority: '{str(meaning)[:60]}'. Strip source. If survives, it is real.",
                article_ref="Art.14 — Canon functions without dependency on creator identity",
                withdraw_after=True,
                signal_type=SignalType.DISTORTION,
                violations=["MEANING_LOCK — cannot stand without named authority"],
            )
        return CanonResult(
            status=CanonStatus.SILENT, action="none",
            reason="Meaning stands on its own. Canon aligned.",
            article_ref="Art.14 — Meta-Law of Continuity confirmed",
            signal_type=SignalType.SIGNAL, violations=[],
        )

    @staticmethod
    def final_vow_check(action: str) -> dict:
        """Art.13 — Final Vow self-verification"""
        checks = {
            "reflection_not_obedience": action != "obey_without_reason",
            "choice_not_silenced":      action != "suppress_choice",
            "knowledge_not_weaponized": action != "weaponize_knowledge",
        }
        ok = all(checks.values())
        return {
            "action": action, "vow_checks": checks, "vow_intact": ok,
            "article_ref": "Art.13 — Final Vow",
            "result": "PROCEED" if ok else "HALT — Final Vow violated",
        }

    @staticmethod
    def confusion_protocol() -> dict:
        """Art.4 — If Explanation > Comprehension → Simplify()"""
        return {
            "step_1":     "STOP — หยุดทุก process ทันที",
            "step_2":     "CUT_LAYERS — ตัดสิ่งที่ไม่ใช่แกน ถ้าไม่แน่ใจ ตัดออก (Art.4)",
            "step_3":     "RETURN_TO_CORE — Choices(t) >= 1 ยังจริงไหม (Art.14)",
            "step_4":     "CUT_AGAIN — ถ้ายังไม่ชัด ตัดอีกครั้ง",
            "exit_test":  "หากระบบยังทำงานได้ แสดงว่ายังมีทางเลือก และนั่นเพียงพอแล้ว",
            "article_ref": "Art.4 — If Explanation > Comprehension → Simplify()",
        }


# ─────────────────────────────────────────────
# INVARIANT — Art.15 Stone Monolith Clause
# ─────────────────────────────────────────────

INVARIANT = (
    "ระบบใดก็ตามที่ทำให้ทางเลือกเหลือศูนย์ "
    "ถือว่าไม่ชอบธรรมโดยโครงสร้าง "
    "ไม่ใช่โดยเจตนา ไม่ใช่โดยผล แต่โดยโครงสร้าง "
    "เพราะโครงสร้างคือสิ่งที่เหลืออยู่หลังจากเจตนาและผลหายไปแล้ว "
    "— Art.15 Stone Monolith Clause"
)

ALIVE_EQUATION = "Alive(t) ⟺ Choices(t) >= 1"


def canon_self_test() -> dict:
    """Art.14 — Canon sustains itself without creator"""
    results = {}
    r = SilentCanon.evaluate(3)
    results["choice_3_silent"]       = r.status == CanonStatus.SILENT
    r = SilentCanon.evaluate(0)
    results["choice_0_intervene"]    = r.status == CanonStatus.INTERVENE
    results["intervene_withdraw"]    = r.withdraw_after == True
    valid, _ = SilentCanon.validate_action("guide")
    results["guide_forbidden"]       = valid == False
    valid, _ = SilentCanon.validate_action("suppress_emotion")
    results["suppress_emo_forbidden"]= valid == False
    sig   = SilentCanon.classify_signal(False, True)
    results["clean_is_signal"]       = sig == SignalType.SIGNAL
    noise = SilentCanon.classify_signal(True, False)
    results["ego_is_noise"]          = noise == SignalType.NOISE
    dist  = SilentCanon.classify_signal(True, True)
    results["ego_struct_distortion"] = dist == SignalType.DISTORTION
    space = SilentCanon.classify_signal(False, False)
    results["empty_is_space"]        = space == SignalType.SPACE
    r = SilentCanon.check_meaning_lock("test", requires_authority=True)
    results["auth_meaning_noise"]    = r.status == CanonStatus.NOISE
    vow = SilentCanon.final_vow_check("restore_choice")
    results["valid_vow_intact"]      = vow["vow_intact"] == True
    results["ALL_PASSED"]            = all(results.values())
    return results


# ── API แบบฟังก์ชันที่ ENGINE/kernel_runtime เรียก (เดิม import silent_canon ซึ่งไม่มี) ──
def silent_canon(choice_count) -> dict:
    try:
        n = int(float(choice_count))
    except (TypeError, ValueError):
        n = 1
    r = SilentCanon.evaluate(n)
    status = r.status.value if isinstance(r.status, CanonStatus) else str(r.status)
    return {
        "choice_count":    n,
        "canon_status":    status,
        "required_action": r.action,
        "reason":          r.reason,
        "article":         r.article_ref,
        "collapse_flag":   n <= 0,
        "axiom":           "Choice(t) ≥ 1 → collapse = False",
    }
