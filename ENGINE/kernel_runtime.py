# ENGINE/kernel_runtime.py
"""
KING DIADEM — Kernel Runtime
Connects all core philosophy modules into a live system
Safe imports — ไม่ crash ถ้า module ยังไม่พร้อม
"""

from __future__ import annotations
from typing import Optional
import time

# ── Safe imports ──────────────────────────────────────────────────
try:
    from core.axioms import AXIOMS
except ImportError:
    AXIOMS = {
        "A1": "Logic over Persona",
        "A2": "Rule over Authority",
        "A3": "Determinism — same input, same output",
        "A4": "Downside before Upside",
        "A5": "Explainability = 100%",
        "A6": "Human Final Authority",
        "lock": "Fail less, not win more",
    }

try:
    from core.reality_laws import REALITY_LAWS
except ImportError:
    REALITY_LAWS = {
        "R1": "Every action has a cost",
        "R2": "Resources are finite",
        "R3": "Time moves in one direction",
        "R4": "Collapse is irreversible — avoid it first",
    }

try:
    from core.dependency_cycle import dependent_cycle
    _DC_LOADED = True
except ImportError:
    _DC_LOADED = False

try:
    from core.silent_canon import silent_canon
    _SC_LOADED = True
except ImportError:
    _SC_LOADED = False

try:
    from core.vigilance_protocol import vigilance_check
    _VP_LOADED = True
except ImportError:
    _VP_LOADED = False

try:
    from core.entropy_guard import entropy_check
    _EG_LOADED = True
except ImportError:
    _EG_LOADED = False


# ── Fallback implementations ──────────────────────────────────────
def _dependent_cycle_fallback(state: dict) -> dict:
    """
    ปฏิจสมุปบาท — dependent origination
    แต่ละ field ส่งผลต่อกันตาม weighted logic
    """
    stability  = float(state.get("stability", 50))
    entropy    = float(state.get("entropy",   40))
    choices    = int(state.get("choices",      1))
    resources  = float(state.get("resources", 50))

    # entropy ลด stability
    new_stability = max(0, stability - (entropy * 0.15))
    # resources หนุน stability
    new_stability = min(100, new_stability + (resources * 0.08))
    # ถ้า choices = 0 → collapse imminent
    if choices <= 0:
        new_stability = max(0, new_stability - 30)

    new_entropy = entropy
    # stability สูง → entropy ลดช้าๆ
    if new_stability > 60:
        new_entropy = max(0, entropy - 5)
    # resources ต่ำ → entropy เพิ่ม
    if resources < 30:
        new_entropy = min(100, entropy + 10)

    return {
        **state,
        "stability":  round(new_stability, 2),
        "entropy":    round(new_entropy,   2),
        "choices":    max(0, choices),
        "resources":  resources,
        "_cycle":     "paticcasamuppada_fallback",
    }

def _entropy_check_fallback(state: dict) -> dict:
    entropy   = float(state.get("entropy",   40))
    stability = float(state.get("stability", 50))
    resources = float(state.get("resources", 50))

    if entropy > 75 or stability < 20:
        level = "critical"
    elif entropy > 55 or stability < 40:
        level = "high"
    elif entropy > 35:
        level = "moderate"
    else:
        level = "low"

    return {
        "entropy_value": entropy,
        "level":         level,
        "drift_risk":    entropy > 60,
        "stop_line":     entropy > 75 or stability < 20,
        "note":          "entropy_guard_fallback",
    }

def _vigilance_check_fallback(state: dict) -> dict:
    choices   = int(state.get("choices",     1))
    entropy   = float(state.get("entropy",  40))
    stability = float(state.get("stability",50))

    alerts = []
    if choices <= 0:
        alerts.append("COLLAPSE_IMMINENT — Choice(t) = 0")
    if choices == 1:
        alerts.append("SINGLE_CHOICE — ต้องหา option เพิ่มทันที")
    if entropy > 70:
        alerts.append("ENTROPY_HIGH — ห้ามตัดสินใจใหม่จนกว่าจะลด")
    if stability < 25:
        alerts.append("STABILITY_CRITICAL — Stabilize ก่อน Optimize")

    return {
        "alert_count": len(alerts),
        "alerts":      alerts,
        "safe":        len(alerts) == 0,
        "note":        "vigilance_fallback",
    }

def _silent_canon_fallback(choice_count: int) -> dict:
    """
    SILENT CANON: existence must never collapse to zero choice
    """
    if choice_count <= 0:
        status  = "VIOLATED"
        action  = "SYSTEM_PAUSE — restore at least 1 real option before proceeding"
        collapse = True
    elif choice_count == 1:
        status  = "MINIMUM"
        action  = "Intervene to restore options — do not let this drop to 0"
        collapse = False
    else:
        status  = "PRESERVED"
        action  = "Monitor — maintain choice_count > 0"
        collapse = False

    return {
        "choice_count":     choice_count,
        "canon_status":     status,
        "required_action":  action,
        "collapse_flag":    collapse,
        "axiom":            "Choice(t) ≥ 1 → collapse = False",
    }


# ── Kernel status resolver ────────────────────────────────────────
def _resolve_kernel_status(entropy_status: dict, canon_state: dict, vigilance: dict) -> str:
    if canon_state.get("collapse_flag"):
        return "COLLAPSE"
    if entropy_status.get("stop_line"):
        return "HALTED"
    if vigilance.get("alert_count", 0) > 0:
        return "WARNING"
    return "ACTIVE"


# ── Main entry point ──────────────────────────────────────────────
def run_kernel(system_state: dict) -> dict:
    """
    Args:
        system_state: {
            stability:  float  0-100
            entropy:    float  0-100
            choices:    int    >= 0
            resources:  float  0-100
        }

    Returns full kernel report dict
    """
    report = {"timestamp": time.time()}

    # Step 1 — Reality Drift (paticcasamuppada)
    if _DC_LOADED:
        next_state = dependent_cycle(system_state)
    else:
        next_state = _dependent_cycle_fallback(system_state)
    report["next_state"] = next_state

    # Step 2 — Entropy Detection
    if _EG_LOADED:
        entropy_status = entropy_check(next_state)
    else:
        entropy_status = _entropy_check_fallback(next_state)
    report["entropy_status"] = entropy_status

    # Step 3 — Vigilance Protocol
    if _VP_LOADED:
        vigilance = vigilance_check(next_state)
    else:
        vigilance = _vigilance_check_fallback(next_state)
    report["vigilance"] = vigilance

    # Step 4 — Choice Preservation (Silent Canon)
    choice_count = next_state.get("choices", 1)
    if _SC_LOADED:
        canon_state = silent_canon(choice_count)
    else:
        canon_state = _silent_canon_fallback(choice_count)
    report["silent_canon"] = canon_state

    # Step 5 — System Axioms
    report["axioms"] = AXIOMS

    # Step 6 — Reality Laws
    report["reality_laws"] = REALITY_LAWS

    # Kernel Status
    report["kernel_status"] = _resolve_kernel_status(entropy_status, canon_state, vigilance)

    # Module load status (debug info)
    report["_modules"] = {
        "dependency_cycle":  _DC_LOADED,
        "entropy_guard":     _EG_LOADED,
        "vigilance_protocol":_VP_LOADED,
        "silent_canon":      _SC_LOADED,
    }

    return report


# ── Demo ──────────────────────────────────────────────────────────
def kernel_demo():
    system_state = {
        "stability": 60,
        "entropy":   45,
        "choices":   3,
        "resources": 70,
    }
    result = run_kernel(system_state)
    print("\n=== KING DIADEM Kernel Runtime ===\n")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    kernel_demo()
