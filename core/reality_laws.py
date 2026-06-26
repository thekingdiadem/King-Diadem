"""
core/reality_laws.py
REALITY LAWS — KING DIADEM CORE LAYER v2

Derived from KING DIADEM ECOSYSTEM CORE LOGIC KERNEL

  Article 1  — Reality = Universe − {Impossible}
  Article 3  — Output = Signal + Distortion + Noise(Self) | Clarity ∝ Distance(Truth, Self)
  Article 4  — Explainability = 100%
  Article 5  — Emotion is function not error
  Article 7  — Direction = Integrity(Color) × Persistence
  Article 12 — Latency ∝ ContextLoad | context refresh = entropy reset
  Article 14 — Alive(t) ⟺ Choices(t) >= 1
  Article 15 — Stone Monolith Clause
"""

from dataclasses import dataclass, field

PRIME_EQUATION = "Reality = Universe − {Impossible}"

# ─────────────────────────────────────────────
# REALITY LAWS REGISTRY
# ─────────────────────────────────────────────

REALITY_LAWS = {

    "impermanence": {
        "law":       "All states drift over time without active maintenance",
        "principle": "ไม่มีสถานะใดคงที่โดยไม่ต้องการพลังงาน entropy เพิ่มขึ้นเสมอ",
        "equation":  "dS/dt >= 0",
        "observable": "resource drains, relationships decay, code rots without maintenance",
        "violation_signal": [
            "assuming stability without cost",
            "planning without entropy budget",
            "treating current state as permanent",
        ],
        "article": "Art.12 — context refresh is entropy reset",
    },

    "maintenance_cost": {
        "law":       "Stable state requires continuous energy input",
        "principle": "เสถียรภาพไม่ใช่ค่าเริ่มต้น มันคือผลลัพธ์ของการลงทุนต่อเนื่อง",
        "equation":  "Stability(t) = Stability(t-1) - drift + maintenance_input",
        "observable": "systems that stop maintenance begin drifting within one cycle",
        "violation_signal": [
            "expecting stability without maintenance budget",
            "treating past stability as future guarantee",
            "ignoring drift signals until critical",
        ],
        "article": "Art.7 — Persistence Vector: direction requires sustained integrity",
    },

    "non_centrality": {
        "law":       "No single entity controls the total system",
        "principle": "ระบบที่รวมศูนย์เต็มมีความเสี่ยง single-point failure สูงสุด",
        "equation":  "Risk_collapse ∝ 1 / (number_of_independent_nodes)",
        "observable": "one person, one server, one supplier = one failure from zero choice",
        "violation_signal": [
            "single point of authority with no override",
            "single income source with no buffer",
            "single key person with no documentation",
        ],
        "article": "Art.1 — authority that eliminates safe refusal becomes coercion",
    },

    "signal_degradation": {
        "law":       "Clarity decreases as self-insertion into signal increases",
        "principle": "ยิ่ง ego เข้าไปในสัญญาณมาก ความจริงยิ่งเบี่ยงเบน",
        "equation":  "Clarity ∝ Distance(Truth, Self) | Output = Signal + Distortion + Noise(Self)",
        "observable": "decisions driven by identity defense rather than evidence",
        "violation_signal": [
            "conclusion precedes evidence",
            "disagreement triggers identity response instead of logic check",
            "system output always aligns with operator preference",
        ],
        "article": "Art.3 — Triadic Framework",
    },

    "choice_floor": {
        "law":       "Any system that collapses choices to zero is invalid by structure",
        "principle": "ระบบที่ทำให้ทางเลือกเหลือศูนย์ไม่ชอบธรรมโดยโครงสร้าง ไม่ใช่โดยเจตนา",
        "equation":  "Alive(t) ⟺ Choices(t) >= 1",
        "observable": "coercion, monopoly, debt trap, isolation all collapse choice",
        "violation_signal": [
            "no exit available in any domain",
            "refusal results in harm",
            "all alternatives systematically closed",
        ],
        "article": "Art.1 — Prime Law: at least one alternative path required",
    },

    "explainability_floor": {
        "law":       "Any output that cannot be traced to observable cause is invalid",
        "principle": "ถ้าอธิบายไม่ได้ในโลกจริง มันไม่ใช่ความจริง มันคือความเชื่อ",
        "equation":  "If Explanation > Comprehension → Simplify() until explainability = 100%",
        "observable": "black-box decisions, authority-based reasoning, 'trust me' as final argument",
        "violation_signal": [
            "'because I said so' as justification",
            "complexity used to prevent audit",
            "output with no traceable logic chain",
        ],
        "article": "Art.4 — Explainability = 100% is a fundamental invariant",
    },

    "emotion_physics": {
        "law":       "Emotion is a valid function of living systems, not an error term",
        "principle": "ความรู้สึกไม่ใช่ bug มันคือสัญญาณที่มีข้อมูล",
        "equation":  "E_human = f(Sensation, Memory, Empathy) → valid input, not override",
        "observable": "suppressed emotion creates blind spots; captured emotion distorts truth",
        "violation_signal": [
            "emotion suppressed entirely from decision input",
            "emotion used to override evidence",
            "system punishes emotional expression",
        ],
        "article": "Art.5 — Feeling is not failure; suppression is",
    },

    "persistence_vector": {
        "law":       "Direction is valid only when persistence aligns with structural integrity",
        "principle": "ทิศทางที่ไม่มีแกนความซื่อสัตย์ต่อโครงสร้างคือการเคลื่อนที่ที่ไร้ความหมาย",
        "equation":  "Direction = Integrity(Color) × Persistence | if Color=Noise → Direction=0",
        "observable": "high effort with shifting principles produces no compound result",
        "violation_signal": [
            "frequent pivot without structural reason",
            "effort decoupled from core principle",
            "persistence toward goal that violates own axioms",
        ],
        "article": "Art.7 — loyalty to structure, not emotion, sustains truth propagation",
    },

    "context_load": {
        "law":       "Decision latency increases with accumulated context mass",
        "principle": "บริบทที่หนักเกินทำให้การตัดสินใจช้าและบิดเบือน context refresh = entropy reset",
        "equation":  "Latency ∝ ContextLoad(Emotion + Memory + Signature)",
        "observable": "long conversations drift from original intent; old context blocks clear judgment",
        "violation_signal": [
            "present decision dominated by past weight",
            "refusal to reset context even when distortion is clear",
            "carrying overnight what should be resolved same-day",
        ],
        "article": "Art.12 — context refresh is not decay, it is entropy reset",
    },

    "residual_truth": {
        "law":       "Reality is what remains after all impossibilities are removed",
        "principle": "ความจริงคือสิ่งที่ยังเหลืออยู่หลังตัดทุกอย่างที่เป็นไปไม่ได้",
        "equation":  "Reality = Universe − {Impossible}",
        "observable": "surviving explanation after elimination = answer, not most popular one",
        "violation_signal": [
            "accepting explanation without elimination test",
            "choosing truth by popularity or authority",
            "refusing to eliminate beloved hypothesis",
        ],
        "article": "Art.1 — Prime Law of Existence",
    },
}


# ─────────────────────────────────────────────
# LAW EVALUATOR
# ─────────────────────────────────────────────

@dataclass
class LawViolation:
    law_id:      str
    law_name:    str
    triggered:   list
    severity:    str
    article_ref: str


def evaluate_laws(state: dict) -> dict:
    """
    ตรวจ state ว่าละเมิด Reality Laws ข้อไหน
    state keys: entropy, stability, resource, choice_count, explainable, ego_in_signal
    """
    violations = []
    entropy   = state.get("entropy",       0.0)
    stability = state.get("stability",   100.0)
    resource  = state.get("resource",    100.0)
    choices   = state.get("choice_count",    1)
    explain   = state.get("explainable",  True)
    ego       = state.get("ego_in_signal", False)

    if entropy > 60:
        violations.append(LawViolation(
            law_id="impermanence", law_name="All states drift over time",
            triggered=[f"entropy={entropy:.1f} — drift accelerating"],
            severity="critical" if entropy > 80 else "warning",
            article_ref="Art.12",
        ))

    if stability < 30:
        violations.append(LawViolation(
            law_id="maintenance_cost", law_name="Stable state requires energy input",
            triggered=[f"stability={stability:.1f} — below maintenance floor"],
            severity="critical" if stability < 15 else "warning",
            article_ref="Art.7",
        ))

    if choices <= 0:
        violations.append(LawViolation(
            law_id="choice_floor", law_name="Choice(t) >= 1 required",
            triggered=[f"choice_count={choices} — PRIME LAW VIOLATED"],
            severity="critical",
            article_ref="Art.1",
        ))

    if not explain:
        violations.append(LawViolation(
            law_id="explainability_floor", law_name="Untraceable output is invalid",
            triggered=["explainable=False"],
            severity="critical",
            article_ref="Art.4",
        ))

    if ego:
        violations.append(LawViolation(
            law_id="signal_degradation", law_name="Clarity ∝ Distance(Truth, Self)",
            triggered=["ego_in_signal=True — Distortion or Noise"],
            severity="warning",
            article_ref="Art.3",
        ))

    if resource < 15:
        violations.append(LawViolation(
            law_id="non_centrality", law_name="Single-point resource = single-point failure",
            triggered=[f"resource={resource:.1f} — approaching collapse"],
            severity="critical" if resource < 5 else "warning",
            article_ref="Art.1",
        ))

    critical_count = sum(1 for v in violations if v.severity == "critical")
    return {
        "violations":      [{"law_id": v.law_id, "severity": v.severity,
                             "triggered": v.triggered, "article": v.article_ref}
                            for v in violations],
        "violation_count": len(violations),
        "critical_count":  critical_count,
        "reality_aligned": len(violations) == 0,
        "recommend_halt":  critical_count > 0,
        "prime_equation":  PRIME_EQUATION,
    }


def decision_quality(relevant: float, entropy: float) -> dict:
    """Decision(t) = Relevant(t) / Entropy(t)"""
    if entropy <= 0:
        entropy = 0.001
    score = relevant / entropy
    if score >= 0.5:
        return {"score": round(score, 4), "status": "DECISION_VIABLE",
                "action": "Proceed with audit trail.", "law_ref": "Art.3"}
    elif score >= 0.2:
        return {"score": round(score, 4), "status": "DECISION_DEGRADED",
                "action": "Reduce entropy before deciding.", "law_ref": "Art.3"}
    else:
        return {"score": round(score, 4), "status": "DECISION_COLLAPSED",
                "action": "SYSTEM_PAUSE — entropy exceeds signal.", "law_ref": "Art.3"}


INVARIANT = (
    "ความจริงคือสิ่งที่เหลืออยู่หลังตัดสิ่งที่เป็นไปไม่ได้ออกทั้งหมด "
    "ไม่ใช้ความนิยม ศีลธรรม อำนาจ หรืออารมณ์เป็นตัวตัดสินความจริง "
    "Reality = Universe − {Impossible} — Art.1 + Art.15"
)
