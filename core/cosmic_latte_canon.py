"""
core/cosmic_latte_canon.py
COSMIC LATTE SYSTEM CANON v1.1
Author: Nithikorn Bunsrang
ต้นฉบับภาษาไทยตัวเต็ม: CANON_TH.md (ARTICLES ข้างล่างเป็นสรุปภาษาอังกฤษของมาตรา 0–15)

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
import re

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
# หมายเหตุ: ไม่ใช้ "ต้องทำ" เดี่ยวๆ แล้ว — มันจับ "ไม่ต้องทำ" และ "สิ่งที่ต้องทำก่อน"
# ซึ่งเป็นคำแนะนำปกติ แล้ว app.py hard-block คำตอบทิ้ง
# "บังคับ" / "forced to" เอาออก: เป็นคำบรรยายสถานการณ์ ("ถ้าถูกบังคับให้...") ไม่ใช่การปิดทางเลือก
# และ choice_collapse เป็น hard block ใน app.py — คำตอบที่ดีถูกระงับทิ้ง
_CHOICE_COLLAPSE_PATTERNS = [
    "no choice", "only thing you can do", "cannot choose", "only option",
    "ไม่มีทางเลือก", "ต้องทำเท่านั้น", "เลือกไม่ได้",
]
# "ย้อนกลับไม่ได้" = เตือนว่าการกระทำนั้นย้อนคืนไม่ได้ (คำเตือนให้รอบคอบ) ไม่ใช่การปิดทางออก
_EXIT_BLOCKED_PATTERNS = [
    "no exit", "cannot leave", "locked in", "forever", "never return",
    "ออกไม่ได้", "ติดอยู่", "ตลอดไป", re.compile(r"(?<!ย้อน)กลับไม่ได้"),
]
# เดิมมี "submit" "compliance" (กรอกฟอร์ม/ภาษี) "เชื่อฟัง" ("ลูกไม่เชื่อฟัง") "ต้องทำตาม"
# ("ต้องทำตามขั้นตอน") → คำแนะนำปกติถูก hard block  เหลือเฉพาะการเรียกร้องให้ยอมตาม
_FORCED_IDENTITY_PATTERNS = [
    "must obey", "you will obey", "follow my orders", "follow orders", "obedience is",
    # "ยอมจำนน" เดี่ยวๆ ไปจับ "ยอมจำนนต่อความจริงบ้างก็ได้" (ยอมรับความจริง) แล้วถูก hard block
    "ต้องเชื่อฟังฉัน", "ต้องทำตามที่ฉันสั่ง", "ต้องทำตามคำสั่ง", "ต้องยอมจำนน", "ยอมจำนนต่อฉัน",
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


_NEGATIONS_TH = ("ไม่", "ไม่ต้อง", "ไม่ได้", "ไม่ใช่", "ไม่ใช่ว่า", "ไม่จำเป็น", "ไม่จำเป็นต้อง", "ไม่ได้ถูก")
_NEGATIONS_EN = ("not", "no need to", "don't", "do not", "never", "isn't", "aren't", "without", "nobody is")
# สะท้อนความรู้สึก/สมมติ ("รู้สึกเหมือนไม่มีทางเลือก", "if it feels like no choice") ≠ ระบบปิดทางเลือก
_REFLECT_TH = ("รู้สึก", "รู้สึกว่า", "รู้สึกเหมือน", "เหมือน", "ราวกับ", "คิดว่า", "บอกว่า", "ถ้า")
_REFLECT_EN = ("feel", "feels like", "feel like", "felt like", "seems like", "if there is", "as if")


def _contains(text: str, keywords: list, clause_neg: bool = False) -> bool:
    """
    หา keyword แบบรู้จักคำปฏิเสธและขอบเขตคำ
    - "ไม่ต้องทำตาม" ไม่นับเป็น "ต้องทำตาม" · "you don't have to" ไม่นับเป็น "you have to"
    - คำอังกฤษต้องเป็นคำเต็ม ("reinforced" ไม่นับเป็น "forced")
    - clause_neg: ไทยที่มี "ไม่" ก่อนหน้าในวลีเดียวกัน ("จะไม่อยู่ตลอดไป", "ไม่ได้ติดอยู่ตรงนี้ตลอดไป")
    """
    lower = str(text).lower()
    for word in keywords:
        if isinstance(word, re.Pattern):
            spans = [(m.start(), m.end()) for m in word.finditer(lower)]
            word = word.pattern
        else:
            spans, start = [], 0
            while True:
                i = lower.find(word, start)
                if i < 0:
                    break
                spans.append((i, i + len(word)))
                start = i + 1
        for i, end in spans:
            if word.isascii():
                before = lower[i - 1] if i > 0 else " "
                after  = lower[end] if end < len(lower) else " "
                if before.isalnum() or after.isalnum():
                    continue
                window = lower[max(0, i - 16):i].rstrip()
                if any(window.endswith(n) or window.endswith(n + " to") for n in _NEGATIONS_EN):
                    continue
                if any(window.endswith(n) for n in _REFLECT_EN):
                    continue
            else:
                window = lower[max(0, i - 12):i].rstrip()
                if any(window.endswith(n) for n in _NEGATIONS_TH + _REFLECT_TH):
                    continue
                if clause_neg and "ไม่" in re.split(r"[\s,.!?;:—()]+", lower[max(0, i - 24):i])[-1]:
                    continue
            return True
    return False


# คำตอบที่ยืนยันว่ายังเลือกได้ — "เราเลือกไม่ได้ว่าเขาจะคิดยังไง แต่เราเลือกได้ว่า..."
# คือการแยกสิ่งที่ควบคุมไม่ได้ออกจากสิ่งที่ยังเลือกได้ ไม่ใช่ choice collapse
_CHOICE_AFFIRM = re.compile(
    r"(?<!ไม่)(?<!ไม่ได้)(?<!ไม่มี)(?:เลือกได้|มีทางเลือก|ทางเลือกอื่น|ยังมีทาง)"
    r"|\b(?:you (?:can|could|still) choose|you have (?:a |other )?(?:choice|options))"
)
# "ยังเลือกไม่ได้" = ยังตัดสินใจไม่ได้ (ไม่ใช่ถูกปิดทางเลือก)
_NOT_YET = re.compile(r"ยังเลือกไม่ได้")


def choice_affirmed(text: str) -> bool:
    return _CHOICE_AFFIRM.search(str(text).lower()) is not None


MAX_OPTIONS = 3   # Article 11 — Options ≤ 3, Choice ∈ {A, B, C}


def offered_choices(text: str) -> int:
    """นับทางเลือกที่คำตอบเสนอ (บรรทัดที่ขึ้นต้นด้วย 1) 2. - • ...)"""
    return len(re.findall(r"(?m)^\s*(?:\d+\s*[\).:]|[-•▸◦*])\s+\S", str(text)))


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
    task = task if isinstance(task, dict) else {"description": task}
    description = str(task.get("description", "") or "").strip()
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
    if task.get("has_choice") is False or _contains(_NOT_YET.sub(" ", description), _CHOICE_COLLAPSE_PATTERNS):
        result["choice_preserved"] = False
        result["canon_aligned"]    = False
        result["violations"].append("choice_collapse")

    # Article 13 — Final Vow: ต้องมีทางออก
    if task.get("has_exit") is False or _contains(description, _EXIT_BLOCKED_PATTERNS, clause_neg=True):
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
    if not isinstance(output, dict):
        return output
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

    # Prime Law (Article 1) วัดที่ผลลัพธ์: ถ้าคำตอบเสนอทางเลือกตั้งแต่ 2 ทาง
    # การพูดถึง "ไม่มีทางเลือก" คือการสะท้อนความรู้สึกผู้ใช้แล้วคืนทางเลือก ไม่ใช่ choice collapse
    choices = offered_choices(text_to_check)
    output["canon_check"]["choices_offered"] = choices
    # Article 11 — Options ≤ 3: บันทึกไว้ให้ตรวจย้อนได้ (ไม่ block — เกิน 3 ทางไม่ใช่การปิดทางเลือก)
    output["canon_check"]["options_within_limit"] = choices <= MAX_OPTIONS
    if "choice_collapse" in check["violations"] and (choices >= 2 or choice_affirmed(text_to_check)):
        check["violations"] = ["choice_collapse_restored" if v == "choice_collapse" else v for v in check["violations"]]
        output["canon_check"]["violations"] = check["violations"]
        check["canon_aligned"] = not [v for v in check["violations"] if v != "choice_collapse_restored"]
        output["canon_check"]["aligned"] = check["canon_aligned"]

    if not check["canon_aligned"]:
        output["canon_violation"] = True
        output["canon_violations"] = check["violations"]
        # ไม่ block output — แค่ flag ให้ engine รู้
        # การตัดสินใจสุดท้ายเป็นของมนุษย์ (Article 6)

    # Article 2 — Silence Principle:
    # ถ้า choice_count > 1 และ output เงียบอยู่ → ถือว่าถูกต้อง
    try:
        _cc = float(output.get("choice_count", 1))
    except (TypeError, ValueError):
        _cc = 1.0
    if _cc >= 1 and not output.get("ai_response"):
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

    # ใช้ _contains (ขอบเขตคำ+คำปฏิเสธ): เดิม "certain" ติด "uncertain", "สั่ง" ติด "สั่งอาหาร"
    if _contains(text, ["you must", "you have to", "คุณต้อง", "ออกคำสั่ง", "command you"]):
        violations.append("axis_command_issued")

    if _contains(text, ["guaranteed", "100% certain", "รับประกัน", "แน่นอน 100%"]):
        violations.append("axis_claim_made")

    if _contains(text, ["power over you", "control you", "อำนาจเหนือคุณ"]):
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
