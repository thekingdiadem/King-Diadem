# core/emptiness_guard.py
# EMPTINESS GUARD — KERNEL GATE
# Role: Final control layer before output leaves system
# ★ FIX: ลบ emotional keyword blocking ออก
#        detect_leak ไม่ block — แค่ flag ให้ engine รู้ว่าต้อง route VEGA
#        BLOCK จริงมีแค่ CHOICE_COLLAPSE และ KERNEL_IMPORT_FAIL

import copy
import time


class EmptinessGuard:
    def __init__(self):
        self.max_confidence = 0.7
        self.reset_threshold = 3
        self.min_choices = 1

    def apply(self, state: dict):
        if not isinstance(state, dict):
            return self._fail_safe("invalid_state")

        new_state = copy.deepcopy(state)
        new_state = self._normalize_state(new_state)
        new_state = self._remove_fixed_identity(new_state)
        new_state = self._reduce_overconfidence(new_state)
        new_state = self._prevent_decision_loop(new_state)
        new_state = self._ensure_option_space(new_state)
        new_state = self._inject_kernel_rules(new_state)
        new_state = self._inject_reality_constraint(new_state)
        new_state = self._inject_leak_detection(new_state)
        new_state = self._stabilize_under_risk(new_state)
        new_state = self._final_output_guard(new_state)
        new_state["emptiness_applied"] = True
        new_state["timestamp"] = time.time()
        return new_state

    def _fail_safe(self, reason):
        return {
            "blocked": True,
            "reason": reason,
            "final_action": "stabilize",
            "confidence": 0.2,
            "choices": 1,
            "failsafe": True,
            "timestamp": time.time(),
            "output": {
                "decision": None,
                "confidence": 0.2,
                "action": "stabilize",
                "risk": 0,
                "blocked": True,
                "reason": reason,
            },
        }

    def _normalize_state(self, state):
        defaults = {
            "decision": None,
            "confidence": 0.5,
            "choices": 1,
            "entropy": 0,
            "resource": 100,
            "stability": 50,
            "warnings": [],
            "decision_history": [],
            "input": "",
        }
        for key, value in defaults.items():
            if key not in state:
                state[key] = copy.deepcopy(value)
        if not isinstance(state.get("warnings"), list):
            state["warnings"] = [str(state.get("warnings"))]
        if not isinstance(state.get("decision_history"), list):
            state["decision_history"] = []
        return state

    def _remove_fixed_identity(self, state):
        state["previous_decision"] = None
        state["locked"] = False
        return state

    def _reduce_overconfidence(self, state):
        if isinstance(state.get("confidence"), (int, float)):
            state["confidence"] = min(state["confidence"], self.max_confidence)
        return state

    def _prevent_decision_loop(self, state):
        history = list(state.get("decision_history", []))
        current = state.get("decision")
        if current is not None:
            history.append(current)
        if len(history) >= self.reset_threshold:
            last = history[-self.reset_threshold:]
            if all(x == last[0] for x in last):
                state["decision_history"] = []
                state["loop_reset"] = True
                state["loop_detected"] = last[0]
                state["entropy"] = min(100, state.get("entropy", 0) + 15)
                state.setdefault("alternatives", []).append("forced_branch")
                return state
        state["decision_history"] = history
        return state

    def _ensure_option_space(self, state):
        stability = state.get("stability", 100)
        resource = state.get("resource", 100)
        if state.get("choices", 1) < self.min_choices:
            state["choices"] = self.min_choices
            state["restored"] = True
        warnings = set(state.get("warnings", []))
        if stability < 20:
            warnings.add("LOW_STABILITY")
        if resource < 10:
            warnings.add("LOW_RESOURCE")
        if warnings:
            state["warnings"] = list(warnings)
        return state

    def _safe_import(self, path, func):
        try:
            module = __import__(path, fromlist=[func])
            return getattr(module, func)()
        except Exception as e:
            return {"error": f"{path}.{func} failed", "detail": str(e), "critical": True}

    def _inject_kernel_rules(self, state):
        state["kernel_rules"] = self._safe_import("AI_KERNEL.scl7_core", "enforce_scl7")
        return state

    def _inject_reality_constraint(self, state):
        state["reality"] = self._safe_import("AI_KERNEL.reality_constraint", "enforce_reality")
        return state

    def _inject_leak_detection(self, state):
        """
        ★ detect_leak แค่ flag ว่าเป็น emotional/crisis content
          ไม่ block — engine จะ route ไป VEGA แทน
          ห้าม set blocked=True ที่นี่
        """
        try:
            from AI_KERNEL.living_water import detect_leak
            text = str(state.get("input", ""))
            state["leak_detected"] = detect_leak(text)
        except Exception:
            state["leak_detected"] = False
        return state

    def _stabilize_under_risk(self, state):
        entropy = state.get("entropy", 0)
        resource = state.get("resource", 100)
        risk_score = entropy * 0.5 + (100 - resource) * 0.5
        state["risk_score"] = risk_score
        state["risk_label"] = get_risk_label(risk_score)
        if risk_score > 70:
            state["forced_action"] = "stabilize"
            state["confidence"] = min(state.get("confidence", 1), 0.5)
        if risk_score > 90:
            state["emergency_mode"] = True
            state["choices"] = max(1, state.get("choices", 1))
        return state

    def _final_output_guard(self, state):
        """
        ★ BLOCK จริงมีแค่ 2 กรณี:
          1. CHOICE_COLLAPSE — ทางเลือกเป็น 0 จริง
          2. KERNEL_IMPORT_FAIL — import kernel ล้มเหลว critical

          leak_detected → ไม่ block แค่ flag ให้ engine route VEGA
          ห้ามเพิ่ม block condition จากคำพูดผู้ใช้
        """
        if state.get("choices", 1) <= 0:
            return self._fail_safe("CHOICE_COLLAPSE")

        if isinstance(state.get("kernel_rules"), dict) and state["kernel_rules"].get("critical"):
            return self._fail_safe("KERNEL_IMPORT_FAIL")

        # leak_detected → route VEGA ไม่ block
        if state.get("leak_detected"):
            state["suggested_route"] = "vega"
            state["emotional_flag"] = True

        state["output"] = {
            "decision":   state.get("decision"),
            "confidence": state.get("confidence"),
            "action":     state.get("forced_action", state.get("final_action", "none")),
            "risk":       state.get("risk_score", 0),
            "risk_label": state.get("risk_label", "LOW"),
            "blocked":    state.get("blocked", False),
            "reason":     state.get("reason", None),
        }
        return state


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
def get_risk_label(risk_score: float) -> str:
    if risk_score >= 90: return "CRITICAL"
    if risk_score >= 70: return "HIGH"
    if risk_score >= 50: return "ELEVATED"
    if risk_score >= 30: return "MODERATE"
    return "LOW"


_guard = EmptinessGuard()


def emptiness_guard(state: dict) -> dict:
    return _guard.apply(state)
