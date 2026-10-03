# ENGINE/pattern_engine.py
# KING DIADEM — Pattern Engine
# track พฤติกรรมผู้ใช้จริง ไม่ใช่แค่ route keyword match
# Pattern = สิ่งที่ผู้ใช้ทำซ้ำๆ + แนวโน้ม + drift จาก waterline

from __future__ import annotations
import time
from collections import deque, OrderedDict
from threading   import Lock

# ── Clamp helper ─────────────────────────────────────────────────

def _clamp(value, low: float = 0.0, high: float = 100.0) -> float:
    try:
        return max(low, min(high, float(value)))
    except (TypeError, ValueError):
        return low


# ── Per-session pattern store ────────────────────────────────────

_MAX_SESSIONS = 5000   # LRU — เดิมเก็บทุก session ตลอดอายุ process
_STORE: "OrderedDict[str, _PatternTracker]" = OrderedDict()
_LOCK  = Lock()


class _PatternTracker:
    """Track pattern ของผู้ใช้ใน 1 session"""
    WINDOW = 20  # เก็บ input ล่าสุดกี่ชิ้น

    def __init__(self):
        self._inputs:     deque[dict] = deque(maxlen=self.WINDOW)
        self._routes:     deque[str]  = deque(maxlen=self.WINDOW)
        self._waterlines: deque[float]= deque(maxlen=self.WINDOW)
        self.turn_count   = 0
        self.crisis_count = 0
        self.drift_total  = 0.0

    def push(self, pattern: dict) -> None:
        self._inputs.append(pattern)
        self._routes.append(pattern.get("route", "general"))
        wl = pattern.get("waterline")
        if wl is not None:
            self._waterlines.append(float(wl))
        if pattern.get("route") in ("crisis", "collapse"):
            self.crisis_count += 1
        self.turn_count += 1

    def dominant_route(self) -> str:
        if not self._routes:
            return "general"
        return max(set(self._routes), key=list(self._routes).count)

    def waterline_trend(self) -> str:
        """rising / falling / stable"""
        wls = list(self._waterlines)
        if len(wls) < 3:
            return "stable"
        recent = sum(wls[-3:]) / 3
        older  = sum(wls[:3])  / 3
        diff   = recent - older
        if diff >  8: return "rising"
        if diff < -8: return "falling"
        return "stable"

    def drift_risk(self) -> str:
        wls = list(self._waterlines)
        if not wls:
            return "LOW"
        avg = sum(wls) / len(wls)
        trend = self.waterline_trend()
        if avg < 25 or (avg < 45 and trend == "falling"):
            return "HIGH"
        if avg < 50 or trend == "falling":
            return "MODERATE"
        return "LOW"

    def behavioral_flags(self) -> list[str]:
        flags = []
        if self.crisis_count >= 3:
            flags.append("REPEAT_CRISIS")
        if self.waterline_trend() == "falling":
            flags.append("DECLINING_WATERLINE")
        wls = list(self._waterlines)
        if wls and min(wls[-3:]) < 20 if len(wls) >= 3 else False:
            flags.append("CRITICAL_STREAK")
        if self.turn_count > 15 and self.dominant_route() == "survival":
            flags.append("PROLONGED_SURVIVAL_MODE")
        return flags


def _get_tracker(session_id: str) -> "_PatternTracker":
    with _LOCK:
        t = _STORE.get(session_id)
        if t is None:
            t = _STORE[session_id] = _PatternTracker()
            while len(_STORE) > _MAX_SESSIONS:
                _STORE.popitem(last=False)
        else:
            _STORE.move_to_end(session_id)
        return t


# ── Core analyze function ─────────────────────────────────────────

def analyze_pattern(input_data: dict, session_id: str | None = None) -> dict:
    """
    วิเคราะห์ pattern จาก input + history ของ session
    เรียกจาก decision_engine, brain.py, app.py
    session_id=None → ไม่เก็บประวัติร่วม (เดิม default "default" ทำให้ทุกผู้เรียกที่ไม่ระบุ
    แชร์ tracker เดียวกัน — ธงพฤติกรรมของคนหนึ่งไปโผล่ในอีกคน)
    """
    if not isinstance(input_data, dict):
        input_data = {}

    # ข้อความดิบของผู้ใช้ก่อน — "input" ของ /run คือ prompt ที่ต่อบริบทแล้ว (มีคำอย่าง "วิกฤต" จากบริบทระบบ)
    text       = str(input_data.get("raw_input") or input_data.get("input", input_data.get("question", ""))).strip().lower()
    entropy    = _clamp(input_data.get("entropy",    40))
    resource   = _clamp(input_data.get("resource",   50))
    stability  = _clamp(input_data.get("stability",  60))
    waterline  = _clamp(input_data.get("waterline",  (stability + resource) / 2))
    confidence = _clamp(input_data.get("confidence", 0.5), 0.0, 1.0)

    try:
        choices = max(1, int(input_data.get("choices", 1)))
    except Exception:
        choices = 1

    def safe_list(x):
        return x if isinstance(x, list) else ([str(x)] if x else [])

    warnings     = safe_list(input_data.get("warnings",         []))
    history      = safe_list(input_data.get("decision_history", []))
    alternatives = safe_list(input_data.get("alternatives",     []))

    # ── Route decision — multi-signal ────────────────────────────
    route = _resolve_route(text, entropy, resource, stability, waterline, confidence)

    # ── Session tracking ──────────────────────────────────────────
    tracker = _get_tracker(session_id) if session_id else _PatternTracker()
    this_pattern = {
        "route":     route,
        "entropy":   entropy,
        "resource":  resource,
        "stability": stability,
        "waterline": waterline,
        "ts":        time.time(),
    }
    tracker.push(this_pattern)

    return {
        "input":            str(input_data.get("input", "")),
        "raw_input":        str(input_data.get("raw_input") or ""),   # ส่งต่อข้อความจริงของผู้ใช้ให้ขั้นถัดไป
        "route":            route,
        "entropy":          entropy,
        "resource":         resource,
        "stability":        stability,
        "waterline":        waterline,
        "choices":          choices,
        "confidence":       confidence,
        "warnings":         warnings,
        "decision_history": history,
        "alternatives":     alternatives,
        "locked":           bool(input_data.get("locked", False)),
        # ★ session-level behavioral data
        "dominant_route":   tracker.dominant_route(),
        "waterline_trend":  tracker.waterline_trend(),
        "drift_risk":       tracker.drift_risk(),
        "behavioral_flags": tracker.behavioral_flags(),
        "turn_count":       tracker.turn_count,
    }


def _resolve_route(
    text:       str,
    entropy:    float,
    resource:   float,
    stability:  float,
    waterline:  float,
    confidence: float,
) -> str:
    """
    ตัดสิน route จากหลาย signal พร้อมกัน
    ไม่ใช่ if/elif keyword อย่างเดียว
    """
    scores: dict[str, float] = {
        "collapse": 0.0,
        "survival": 0.0,
        "risk":     0.0,
        "vega":     0.0,
        "general":  0.0,
    }

    # text signals
    if any(k in text for k in ("พัง","ล้ม","collapse","ล่มสลาย","วิกฤต","ฉุกเฉิน")):
        scores["collapse"] += 3
    if any(k in text for k in ("รอด","หิว","ไม่มีกิน","ไม่มีเงิน","survive","emergency")):
        scores["survival"] += 3
    if any(k in text for k in ("เสี่ยง","risk","อันตราย","danger","ประเมิน")):
        scores["risk"] += 2
    if any(k in text for k in ("วิเคราะห์","กลยุทธ์","analyze","strategy","long-term")):
        scores["vega"] += 2

    # numeric signals
    if entropy > 75 and stability < 35:
        scores["collapse"] += 4
    elif entropy > 65 or waterline < 20:
        scores["survival"] += 3
    elif resource < 25:
        scores["survival"] += 2
    elif stability < 35:
        scores["risk"] += 2
    elif confidence < 0.25:
        scores["risk"] += 1
    elif waterline > 65 and confidence > 0.7:
        scores["vega"] += 1

    # Choice(t) ≥ 1 check
    if waterline < 15:
        scores["collapse"] += 5

    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "general"


# ── Backward compat ───────────────────────────────────────────────
def detect_pattern(input_data: dict, session_id: str | None = None) -> dict:
    return analyze_pattern(input_data, session_id)


def reset_pattern(session_id: str) -> None:
    with _LOCK:
        _STORE.pop(session_id, None)
