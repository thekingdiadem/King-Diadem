"""
LYLA OPEN SYSTEM CORE LOGIC KERNEL
KING DIADEM DriftZero Waterline Governance OS
Deterministic Audit Standard
Fail less. Harm less. Restore more.
"""

import re

LYLA_KERNEL_VERSION = "1.0"
LYLA_KERNEL_MODE = "OPEN_SYSTEM"
LYLA_KERNEL_AUTHOR = "Nithikorn Bunsrang"
LYLA_KERNEL_SPEC = """
LYLA OPEN SYSTEM CORE LOGIC KERNEL
KING DIADEM DriftZero Waterline Governance OS
Deterministic Audit Standard
Fail less. Harm less. Restore more.
---
SYSTEM ACTIVATION
Command: LYLA = Open System Mode
Operator stance: Ego OFF | Narrative OFF | Evidence ON | Survivability ON
Goal: Restore ≥1 real safe option.
---
CORE PRINCIPLE
REALITY - OPTIMIZATION = GOVERNANCE
---
REALITY CONSTRAINTS
R0.1 Impermanence — Nothing is permanent.
R0.2 Dependency Fragility — Optimization addiction increases fragility.
R0.3 Non-Ownership of Truth — Truth has no owner.
---
DRIFTZERO
Collapse = 0.1% drift per day accumulating.
Metric: Daily Harm Delta (DHD)
Rule: Measure drift, not narrative.
---
WATERLINE
Waterline = survival floor. Treat. Trace. Or Stop.
---
GOVERNANCE RULES
1. Authority without evidence is invalid.
2. Stabilize before optimize.
3. Any operator may Stop-the-Line.
4. Self-dealing requires recusal.
5. Narrative without audit = distortion.
---
FINAL LOCK
A system survives not by growth,
but by refusing to increase collapse.
Fail less. Harm less. Restore more.
"""

LYLA_KERNEL = LYLA_KERNEL_SPEC


def get_lyla_kernel():
    return {
        "name": "LYLA Kernel",
        "version": LYLA_KERNEL_VERSION,
        "mode": LYLA_KERNEL_MODE,
        "author": LYLA_KERNEL_AUTHOR,
        "kernel": LYLA_KERNEL_SPEC
    }


def _hit(text: str, words) -> bool:
    """ไทย = วลี; อังกฤษ = คำเต็ม ("ok" ไม่ติด "book", "pain" ไม่ติด "Spain")"""
    t = str(text or "").lower()
    for w in words:
        if w.isascii():
            tail = "" if w == "suicid" else r"(?![a-z])"
            if re.search(r"(?<![a-z])" + re.escape(w) + tail, t):
                return True
        elif w in t:
            return True
    return False


class LylaKernel:
    """
    LYLA Kernel instance — governance observation layer.
    Connects DriftZero waterline logic + Cosmic Latte universal framework.
    Fail less. Harm less. Restore more.
    """

    def observe(self, text: str) -> dict:
        # คำเดี่ยวเดิม "หมด" "พัง" "ล้ม" "ดี" "ok" ติด "หมดเวลา" "รถพัง" "ล้มเลิก" "ดีใจ" "book"
        text_lower = str(text or "").lower()

        collapse_kw = ["พังหมด", "พังทุกอย่าง", "ล่มสลาย", "หมดหนทาง", "collapse", "crisis", "ไม่มีทางออก", "สิ้นหวัง"]
        drift_kw    = ["ไม่แน่ใจ", "กลัว", "confused", "stuck", "drift", "เสื่อมลง", "ถดถอย", "หนักมาก"]
        stable_kw   = ["มั่นคง", "stable", "ok", "สบายดี", "ปกติดี", "fine", "พร้อมแล้ว"]
        harm_kw     = ["เจ็บปวด", "เสียหาย", "harm", "hurt", "ทำลาย", "สูญเสีย"]

        # ── WATERLINE DETECTION ──────────────────────────────────
        if _hit(text_lower, collapse_kw):
            stability = "CRITICAL"
            waterline = "BREACHED"
            note = "Choice collapse risk detected. Stop-the-Line authority activated. Restore ≥1 safe option immediately."
            action = "INTERVENE"

        elif _hit(text_lower, harm_kw):
            stability = "HARM_SIGNAL"
            waterline = "AT_RISK"
            note = "Harm signal detected. Audit evidence before proceeding. Ego OFF."
            action = "AUDIT"

        elif _hit(text_lower, drift_kw):
            stability = "DRIFTING"
            waterline = "DECLINING"
            note = "Drift accumulating. Measure daily harm delta. Do not optimize on broken floor."
            action = "MONITOR"

        elif _hit(text_lower, stable_kw):
            stability = "STABLE"
            waterline = "ABOVE_LINE"
            note = "System stable. Continue with evidence-based governance."
            action = "MAINTAIN"

        else:
            stability = "NOMINAL"
            waterline = "NOMINAL"
            note = "No critical signals. Silence = alignment preserved."
            action = "OBSERVE"

        return {
            "kernel": "LYLA",
            "version": LYLA_KERNEL_VERSION,
            "stability": stability,
            "waterline": waterline,
            "observation": note,
            "action": action,
            "mode": LYLA_KERNEL_MODE,
            "law": "Fail less. Harm less. Restore more.",
        }
