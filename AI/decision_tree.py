# AI/decision_tree.py
# KING DIADEM™ — Deterministic Decision Tree
# Article 1: Reality is measured, not assumed.
# Article 3: Every decision leaves a traceable record.
# FATE™: "ถ้าอธิบายไม่ได้ = ใช้ไม่ได้"
#
# ❌ REMOVED: random.choice / random.uniform
# ✅ REPLACED: weighted registry anchored to entropy + stability + route

from typing import Optional

# ── Strategy registry — deterministic, not random ─────────────────
# key = (entropy_band, stability_band)
# entropy_band  : "low"(<40) / "mid"(40-70) / "high"(>70)
# stability_band: "high"(>60) / "mid"(40-60) / "low"(<40)

_STRATEGY_REGISTRY: dict[tuple, list[dict]] = {
    ("low",  "high"): [
        {"strategy": "advance",          "risk": 0.15, "confidence": 0.88},
        {"strategy": "scale_up",         "risk": 0.20, "confidence": 0.82},
        {"strategy": "collect_signal",   "risk": 0.10, "confidence": 0.90},
    ],
    ("low",  "mid"): [
        {"strategy": "advance",          "risk": 0.25, "confidence": 0.75},
        {"strategy": "wait_and_observe", "risk": 0.15, "confidence": 0.80},
        {"strategy": "collect_signal",   "risk": 0.12, "confidence": 0.78},
    ],
    ("low",  "low"): [
        {"strategy": "reduce_exposure",  "risk": 0.30, "confidence": 0.70},
        {"strategy": "wait_and_observe", "risk": 0.20, "confidence": 0.72},
        {"strategy": "pivot_direction",  "risk": 0.35, "confidence": 0.65},
    ],
    ("mid",  "high"): [
        {"strategy": "wait_and_observe", "risk": 0.35, "confidence": 0.70},
        {"strategy": "collect_signal",   "risk": 0.25, "confidence": 0.75},
        {"strategy": "reduce_exposure",  "risk": 0.28, "confidence": 0.68},
    ],
    ("mid",  "mid"): [
        {"strategy": "wait_and_observe", "risk": 0.45, "confidence": 0.60},
        {"strategy": "reduce_exposure",  "risk": 0.40, "confidence": 0.62},
        {"strategy": "collect_signal",   "risk": 0.35, "confidence": 0.65},
    ],
    ("mid",  "low"): [
        {"strategy": "reduce_exposure",  "risk": 0.55, "confidence": 0.55},
        {"strategy": "pivot_direction",  "risk": 0.50, "confidence": 0.52},
        {"strategy": "wait_and_observe", "risk": 0.48, "confidence": 0.58},
    ],
    ("high", "high"): [
        {"strategy": "reduce_exposure",  "risk": 0.60, "confidence": 0.50},
        {"strategy": "pivot_direction",  "risk": 0.65, "confidence": 0.48},
        {"strategy": "wait_and_observe", "risk": 0.58, "confidence": 0.52},
    ],
    ("high", "mid"): [
        {"strategy": "reduce_exposure",  "risk": 0.70, "confidence": 0.42},
        {"strategy": "pivot_direction",  "risk": 0.72, "confidence": 0.40},
        {"strategy": "survival_mode",    "risk": 0.65, "confidence": 0.45},
    ],
    ("high", "low"): [
        {"strategy": "survival_mode",    "risk": 0.85, "confidence": 0.35},
        {"strategy": "reduce_exposure",  "risk": 0.80, "confidence": 0.38},
        {"strategy": "pivot_direction",  "risk": 0.82, "confidence": 0.36},
    ],
}


def _entropy_band(entropy: float) -> str:
    if entropy < 40:  return "low"
    if entropy < 70:  return "mid"
    return "high"


def _stability_band(stability: float) -> str:
    if stability > 60: return "high"
    if stability > 40: return "mid"
    return "low"


class DecisionTree:
    """
    Deterministic path generator — ผลลัพธ์ขึ้นกับ state จริง
    input เดิม → output เดิมเสมอ (reproducible)
    """

    def generate_paths(
        self,
        problem: str,
        entropy:   float = 50.0,
        stability: float = 50.0,
        route:     Optional[str] = None,
        context:   Optional[dict] = None,
    ) -> dict:
        """
        คืน 3 paths ที่ถูก rank ตาม entropy + stability
        ไม่มี random — input เดิมได้ผลเดิมเสมอ

        Article 1 — ค่า risk/confidence มาจาก state จริง
        Article 3 — trace ได้ผ่าน entropy_band + stability_band
        """
        def _n(v, d):
            try:
                x = float(v)
            except (TypeError, ValueError):
                return d
            return x if x == x else d
        entropy, stability = _n(entropy, 50.0), _n(stability, 50.0)
        eb = _entropy_band(entropy)
        sb = _stability_band(stability)

        raw_paths = _STRATEGY_REGISTRY.get((eb, sb), _STRATEGY_REGISTRY[("mid", "mid")])

        paths = []
        for i, p in enumerate(raw_paths[:3]):
            paths.append({
                "option":     f"Path {i + 1}",
                "strategy":   p["strategy"],
                "risk":       p["risk"],
                "confidence": p["confidence"],
                "rank":       i + 1,
            })

        return {
            "problem":        problem,
            "entropy":        entropy,
            "stability":      stability,
            "entropy_band":   eb,
            "stability_band": sb,
            "route":          route or "GENERAL",
            "paths":          paths,
            "axiom":          "Choice(t) ≥ 1 → collapse = False",
        }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    dt = DecisionTree()

    # determinism check — same input must yield same output
    r1 = dt.generate_paths("test", entropy=80, stability=30)
    r2 = dt.generate_paths("test", entropy=80, stability=30)
    assert r1["paths"] == r2["paths"], "non-deterministic!"

    # high entropy → survival / reduce
    r3 = dt.generate_paths("crisis", entropy=85, stability=25)
    assert r3["paths"][0]["strategy"] in ("survival_mode", "reduce_exposure")

    # low entropy → advance
    r4 = dt.generate_paths("growth", entropy=20, stability=80)
    assert r4["paths"][0]["strategy"] in ("advance", "scale_up", "collect_signal")

    return {"status": "OK", "module": "decision_tree"}


if __name__ == "__main__":
    import json
    dt = DecisionTree()
    result = dt.generate_paths("expand business", entropy=55, stability=45)
    print(json.dumps(result, indent=2))
    print(_self_test())
