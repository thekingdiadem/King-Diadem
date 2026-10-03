# AI/planetary_reality.py
# KING DIADEM — Planetary Reality Engine
# FATE™ Axiom compliance: Determinism · Explainability=100%
# Fail less. Harm less. Restore more.

import time

# ── BASE SIGNAL WEIGHTS ────────────────────────────────────────────
# ค่า baseline สำหรับแต่ละ domain — ปรับได้ผ่าน inject_context()
_BASE_SIGNALS: dict[str, float] = {
    "economic":      55.0,   # 0–100, สูง = เสถียร
    "social":        60.0,
    "environment":   45.0,   # environment มักต่ำกว่า baseline
    "technological": 65.0,
}

_DOMAIN_WEIGHTS: dict[str, float] = {
    "economic":      0.35,
    "social":        0.25,
    "environment":   0.20,
    "technological": 0.20,
}

_STATUS_THRESHOLDS = {
    "expansion":   70.0,
    "stable":      45.0,
    # ต่ำกว่า 45 = compression
}


def _compute_freedom(signals: dict[str, float]) -> float:
    """Weighted average of all domain signals"""
    total = sum(
        signals.get(domain, 50.0) * weight
        for domain, weight in _DOMAIN_WEIGHTS.items()
    )
    return round(total, 2)


def _status_label(freedom: float) -> str:
    if freedom >= _STATUS_THRESHOLDS["expansion"]:
        return "expansion"
    if freedom >= _STATUS_THRESHOLDS["stable"]:
        return "stable"
    return "compression"


def planetary_status(context: dict | None = None) -> dict:
    """
    คำนวณ planetary reality แบบ deterministic
    context: dict ที่ inject real signal values ได้
             e.g. {"economic": 40.0, "social": 55.0}

    Returns:
        freedom_index, planetary_status, signals (per domain), fate_note
    """
    signals = dict(_BASE_SIGNALS)

    # Inject context ถ้ามี — ค่าจาก context override baseline
    if context and isinstance(context, dict):
        for domain in _BASE_SIGNALS:
            if domain in context:
                try:
                    raw = float(context[domain])
                except (TypeError, ValueError):
                    continue
                if raw != raw:      # NaN
                    continue
                signals[domain] = round(min(max(raw, 0.0), 100.0), 2)

    freedom = _compute_freedom(signals)
    status  = _status_label(freedom)

    # FATE™ drift warning
    low_domains = [d for d, v in signals.items() if v < 40.0]
    fate_note   = (
        f"DRIFT_WARNING: {', '.join(low_domains)} ต่ำกว่า threshold"
        if low_domains else "STABLE: ทุก domain อยู่ใน acceptable range"
    )

    return {
        "freedom_index":    freedom,
        "planetary_status": status,
        "signals":          signals,
        "signal_domains":   list(signals.keys()),
        "computed_at":      int(time.time()),
        "fate_note":        fate_note,
        # baseline เป็นค่าตั้งต้นในโค้ด ไม่ได้วัดจากโลกจริง เว้นแต่ส่ง context เข้ามา
        "source":           "injected" if context else "static_baseline",
    }
