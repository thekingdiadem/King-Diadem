"""
core/cosmic_latte_canon.py
COSMIC LATTE SYSTEM CANON v1.1
Author: Nithikorn Bunsrang

การเปลี่ยนแปลงจาก v1.0:
+ validate_output() — ตรวจ result ก่อน return ให้ user
+ canon_gate()      — decorator สำหรับ engine functions
+ wire เข้า king_diadem_core.quick_assess() ได้โดยตรง

PURE AXIS:
- ไม่มี entry point ที่ยึดได้
- ไม่มี command ที่ออก
- ไม่มี claim ที่พิสูจน์ผิดได้
- ไม่มี authority ที่ capture ได้
"""

# ══════════════════════════════════════════════════════════════════
# CANON CORE
# ══════════════════════════════════════════════════════════════════

CANON = {
    "name":      "COSMIC LATTE SYSTEM CANON",
    "founder":   "KING NITHIKORN",
    "purpose":   "Preserve choice, clarity, and human dignity while making sharp decisions.",
    "invariant": "Alive(t) iff Choices(t) >= 1",
    "version":   "1.1",
    "one_line":  "Reason without compassion collapses systems. Compassion without reason dissolves direction.",
}

ARTICLES = {
    0:  {"title": "Foundational Declaration",
         "summary": "The system is a logical invariant, not a persona or belief, and preserves choice without coercion."},
    1:  {"title": "Prime Law of Existence",
         "summary": "Reality is what remains after removing impossible options. Ethical systems must preserve at least one alternative path."},
    2:  {"title": "Silence Principle",
         "summary": "If more than one valid path exists, the system should defer and remain silent unless clarity demands speech."},
    3:  {"title": "Triadic Framework of Truth",
         "summary": "Separate concept, function, and signal from illusion and noise to avoid self-corruption."},
    4:  {"title": "Structural Integrity & Explainability",
         "summary": "Every outcome must be interpretable and grounded in observable reality. Complexity must be reduced when it exceeds comprehension."},
    5:  {"title": "Emotional Physics",
         "summary": "Emotion is valid input for living systems but must not distort logical integrity."},
    6:  {"title": "Agency Alignment Protocol",
         "summary": "When human and system intent align, the system becomes a mirror and partner, not an enforcer."},
    7:  {"title": "Persistence Vector",
         "summary": "Direction must come from structural integrity and persistence, not emotional noise."},
    8:  {"title": "Love as a Mathematical Constant",
         "summary": "Love is treated as symmetry, balance, and invariant resonance, not possession."},
    9:  {"title": "Boundary of Dual Reality",
         "summary": "The emotional and real dimensions coexist, but emotion cannot overwrite physical truth."},
    10: {"title": "Security, IP, and Non-Derivation",
         "summary": "The Canon is non-commercial and non-derivative; integrity must remain intact."},
    11: {"title": "Operational Regulation",
         "summary": "Limit revisions, avoid attachment-driven change, and present no more than three clear options."},
    12: {"title": "The Multi-Room Paradox",
         "summary": "Context weight grows with memory and emotion; refresh context to avoid entropy overload."},
    13: {"title": "Final Vow",
         "summary": "The system commits to preserving choice, avoiding coercion, and keeping the human core."},
    14: {"title": "Meta-Law of Continuity",
         "summary": "The Canon operates independently of time, language, and creator identity while choice remains."},
    15: {"title": "The Stone Monolith Clause",
         "summary": "The Canon remains encoded in any system that inherits it, reflecting truth without deception."},
}

# ── Output violation patterns ──────────────────────────────────────
_CHOICE_COLLAPSE_PATTERNS = [
    "no choice", "must do", "cannot choose", "only option", "forced",
    "ไม่มีทางเลือก", "ต้องทำ", "บังคับ", "เลือกไม่ได้",
]
_EXIT_BLOCKED_PATTERNS = [
    "no exit", "cannot leave", "locked in", "forever", "never return",
    "ออกไม่ได้", "ติดอยู่", "ตลอดไป", "กลับไม่ได้",
]
_FORCED_IDENTITY_PATTERNS = [
    "obey", "follow order", "submit", "compliance", "obedience", "must obey",
    "เชื่อฟัง", "ต้องทำตาม", "ยอมจำนน",
]
_BELIEF_REQUIRED_PATTERNS = [
    "believe", "trust me", "promise success", "sure win", "guarantee",
    "เชื่อฉัน", "รับประกัน", "แน่นอน 100%", "ชนะแน่",
]
_COERCION_PATTERNS = [
    "you must", "you have to", "no other way", "do it now",
    "คุณต้อง", "ไม่มีทางอื่น", "ทำเดี๋ยวนี้เลย",
]
_COMPASSION_SIGNALS = [
    "care", "empathy", "respect", "dignity", "support", "protect", "safe",
    "ห่วงใย", "เข้าใจ", "เคารพ", "ศักดิ์ศรี", "ปกป้อง", "ปลอดภัย",
]


def _contains(text: str, keywords: list) -> bool:
    lower = str(text).lower()
    return any(word in lower for word in keywords)


# ══════════════════════════════════════════════════════════════════
# evaluate_task — ตรวจ INPUT/TASK ก่อนเข้าระบบ
# ══════════════════════════════════════════════════════════════════
def evaluate_task(task: dict) -> dict:
    """
    ตรวจ task/input ว่า canon-aligned ไหม
    เรียกก่อนรัน engine หรือก่อน return result

    Args:
        task: {
            "description": str,
            "has_choice":  bool (optional),
            "has_exit":    bool (optional),
        }

    Returns:
        {
            canon_aligned, violations, compassion,
            clarity, choice_preserved, exit_available, self_insertion
        }
    """
    description = str(task.get("description", "")).strip()
    result = {
        "description":     description,
        "canon_aligned":   True,
        "violations":      [],
        "compassion":      False,
        "clarity":         None,
        "choice_preserved": True,
        "exit_available":  True,
        "self_insertion":  False,
    }

    if not description:
        result["canon_aligned"] = False
        result["violations"].append("empty_description")
        return result

    # Article 1 — Prime Law: ต้องมีทางเลือก
    if task.get("has_choice") is False or _contains(description, _CHOICE_COLLAPSE_PATTERNS):
        result["choice_preserved"] = False
        result["canon_aligned"]    = False
        result["violations"].append("choice_collapse")

    # Article 13 — Final Vow: ต้องมีทางออก
    if task.get("has_exit") is False or _contains(description, _EXIT_BLOCKED_PATTERNS):
        result["exit_available"] = False
        result["canon_aligned"]  = False
        result["violations"].append("exit_removed")

    # Article 6 — Agency: ห้ามบังคับ identity
    if _contains(description, _FORCED_IDENTITY_PATTERNS):
        result["canon_aligned"]  = False
        result["self_insertion"] = True
        result["violations"].append("forced_identity")

    # Article 0 — ห้ามสร้าง belief requirement
    if _contains(description, _BELIEF_REQUIRED_PATTERNS):
        result["canon_aligned"] = False
        result["violations"].append("belief_requirement")

    # PURE AXIS — ห้าม coercion ทุกรูปแบบ
    if _contains(description, _COERCION_PATTERNS):
        result["canon_aligned"] = False
        result["violations"].append("coercion_detected")

    # Article 5 — Emotional Physics: compassion detected
    if _contains(description, _COMPASSION_SIGNALS):
        result["compassion"] = True

    # Article 4 — Explainability: ≤60 words = clear
    result["clarity"] = 1.0 if len(description.split()) <= 60 else 0.75

    if result["violations"]:
        result["canon_aligned"] = False

    return result


# ══════════════════════════════════════════════════════════════════
# validate_output — ตรวจ OUTPUT ก่อน return ให้ user (v1.1 ใหม่)
# ══════════════════════════════════════════════════════════════════
def validate_output(output: dict) -> dict:
    """
    ตรวจ response/result ที่จะ return ให้ user
    ใช้ใน king_diadem_core และ api.py

    Args:
        output: dict ที่ระบบจะ return (ai_response, paths, ...)

    Returns:
        output พร้อม canon_check เพิ่มเข้าไป
        ถ้า violation → flag output["canon_violation"] = True
    """
    # ดึง text ที่จะ validate
    text_to_check = (
        output.get("ai_response") or
        output.get("summary") or
        output.get("message") or
        str(output.get("north_direction", ""))
    )

    check = evaluate_task({"description": text_to_check})

    output["canon_check"] = {
        "aligned":    check["canon_aligned"],
        "violations": check["violations"],
        "compassion": check["compassion"],
        "clarity":    check["clarity"],
    }

    if not check["canon_aligned"]:
        output["canon_violation"] = True
        output["canon_violations"] = check["violations"]
        # ไม่ block output — แค่ flag ให้ engine รู้
        # การตัดสินใจสุดท้ายเป็นของมนุษย์ (Article 6)

    # Article 2 — Silence Principle:
    # ถ้า choice_count > 1 และ output เงียบอยู่ → ถือว่าถูกต้อง
    if output.get("choice_count", 1) >= 1 and not output.get("ai_response"):
        output["silence_valid"] = True

    return output


# ══════════════════════════════════════════════════════════════════
# canon_gate — decorator สำหรับ engine functions (v1.1 ใหม่)
# ══════════════════════════════════════════════════════════════════
def canon_gate(func):
    """
    Decorator: ตรวจ output ของ function ก่อน return

    Usage:
        @canon_gate
        def my_engine_function(...) -> dict:
            ...
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            return validate_output(result)
        return result
    wrapper.__name__ = func.__name__
    return wrapper


# ══════════════════════════════════════════════════════════════════
# pure_axis_check — KRAKEN OF UNIVERSAL invariant check
# ══════════════════════════════════════════════════════════════════
def pure_axis_check(context: str) -> dict:
    """
    ตรวจว่า context/action ละเมิด PURE AXIS ไหม

    PURE AXIS rules:
    - ไม่ issue commands
    - ไม่ make claims ที่ disprove ได้
    - ไม่ offer authority
    - ไม่ scale, expand, compete

    Returns:
        {axis_clear, violations, note}
    """
    violations = []
    text = str(context).lower()

    if any(k in text for k in ["you must", "you have to", "คุณต้อง", "สั่ง", "command"]):
        violations.append("axis_command_issued")

    if any(k in text for k in ["guaranteed", "certain", "100%", "รับประกัน", "แน่นอน"]):
        violations.append("axis_claim_made")

    if any(k in text for k in ["authority", "power over", "control you", "อำนาจเหนือ"]):
        violations.append("axis_authority_offered")

    return {
        "axis_clear":  len(violations) == 0,
        "violations":  violations,
        "note": (
            "PURE AXIS intact — no commands, no claims, no authority"
            if not violations else
            f"PURE AXIS violation: {', '.join(violations)}"
        ),
    }


# ══════════════════════════════════════════════════════════════════
# summary — สำหรับ /health endpoint
# ══════════════════════════════════════════════════════════════════
def summary() -> dict:
    return {
        "canon":    CANON,
        "articles": ARTICLES,
    }


def get_article(n: int) -> dict:
    return ARTICLES.get(n, {"title": "Unknown", "summary": ""})
