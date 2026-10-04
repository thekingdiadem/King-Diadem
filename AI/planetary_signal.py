# AI/planetary_signal.py
# KING DIADEM — Planetary Signal Engine
# FATE™ Axiom compliance: Determinism · Downside First · Explainability=100%
# Fail less. Harm less. Restore more.

import time

# ── DEFAULT BASELINES ─────────────────────────────────────────────
# ค่า baseline ที่ calibrate จากข้อมูล global (2024–2026 approximation)
_DEFAULT = {
    "human_pressure":     52.0,   # สูง = กดดันมาก
    "economic_stress":    48.0,   # สูง = เครียดมาก
    "environment_damage": 58.0,   # สูง = เสียหายมาก
    "conflict_risk":      35.0,   # สูง = เสี่ยงขัดแย้งมาก
    "freedom_signal":     55.0,   # สูง = เสรีภาพมาก
}

_STRESS_DOMAINS = ["human_pressure", "economic_stress", "environment_damage", "conflict_risk"]
_FREEDOM_DOMAIN = "freedom_signal"

_STABILITY_WEIGHT = {
    "human_pressure":     -0.22,   # negative = สูง → stability ลด
    "economic_stress":    -0.25,
    "environment_damage": -0.18,
    "conflict_risk":      -0.15,
    "freedom_signal":     +0.20,   # positive = สูง → stability เพิ่ม
}


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return round(min(max(value, lo), hi), 2)


def _compute_stability(values: dict[str, float]) -> float:
    """
    Weighted sum — replaces กูเกิลเอามา `(sum of 100-each + freedom)/5`
    สูตรเดิมเป็น non-weighted average ที่บิดเบือนเมื่อค่าต่างกันมาก
    """
    base   = 50.0
    delta  = sum(
        values.get(domain, _DEFAULT[domain]) * weight
        for domain, weight in _STABILITY_WEIGHT.items()
    )
    return _clamp(base + delta)


def _fate_note(values: dict[str, float], stability: float) -> str:
    """สร้าง FATE audit note จาก signal"""
    high_stress = [d for d in _STRESS_DOMAINS if values.get(d, 0) > 65.0]
    low_freedom = values.get(_FREEDOM_DOMAIN, 50) < 40.0

    parts = []
    if stability < 35.0:
        parts.append("🔴 CRITICAL: planetary_stability ต่ำมาก")
    elif stability < 50.0:
        parts.append("🟠 DRIFT: stability ต่ำกว่า safe floor")

    if high_stress:
        parts.append(f"⚠ stress สูง: {', '.join(high_stress)}")
    if low_freedom:
        parts.append("⚠ freedom_signal ต่ำ — ความเสี่ยงด้านการเลือก")

    return " | ".join(parts) if parts else "✅ ทุก signal อยู่ใน acceptable range"


def planetary_signal(context: dict | None = None) -> dict:
    """
    คำนวณ planetary signal แบบ deterministic
    context: inject real values ได้ — ถ้าไม่มีใช้ baseline

    Returns:
        ทุก signal + planetary_stability + fate_note + computed_at
    """
    values: dict[str, float] = {}

    for key, default_val in _DEFAULT.items():
        raw = context.get(key) if isinstance(context, dict) else None
        try:
            v = float(raw) if raw is not None else None
        except (TypeError, ValueError):
            v = None
        values[key] = _clamp(v) if v is not None and v == v else default_val

    stability = _compute_stability(values)

    return {
        **values,
        "planetary_stability": stability,
        "fate_note":           _fate_note(values, stability),
        "computed_at":         int(time.time()),
        # baseline = ค่าประมาณที่เขียนในโค้ด ไม่ใช่ข้อมูลโลกจริง
        "source":              "injected" if isinstance(context, dict) and context else "static_baseline",
    }
