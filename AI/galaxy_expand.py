# AI/galaxy_expand.py
# KING DIADEM™ — Galaxy Expansion Engine
# Article 1: Reality is measured, not assumed.
# Article 5: Collapse probability must be computed, not guessed.
#
# ❌ REMOVED: random.randint / random.choice
# ✅ REPLACED: expansion depth driven by route + entropy + stability

from typing import Optional

# ── Expansion registry ────────────────────────────────────────────
# Each route has ordered expansion options — Downside First (FATE™ principle)
# highest risk route → fewest/safer options first

_ROUTE_EXPANSIONS: dict = {
    "SURVIVAL": [
        "reduce_exposure",
        "secure_minimum_resource",
        "exit_non_essential",
    ],
    "COLLAPSE": [
        "emergency_exit",
        "reduce_exposure",
        "secure_minimum_resource",
    ],
    "RISK": [
        "reduce_exposure",
        "wait_for_signal",
        "collect_market_signal",
        "build_defensive_alliance",
    ],
    "GENERAL": [
        "collect_market_signal",
        "test_prototype",
        "build_alliance",
        "increase_investment",
    ],
    "CIVIL": [
        "build_alliance",
        "collect_market_signal",
        "test_prototype",
        "increase_investment",
    ],
    "VEGA": [
        "collect_market_signal",
        "test_prototype",
        "build_alliance",
        "increase_investment",
        "scale_up",
    ],
}

# expansion depth = how many options to return, based on entropy
def _expansion_depth(entropy: float, stability: float) -> int:
    """
    สูง entropy / ต่ำ stability → ลดทางเลือก (Downside First)
    ต่ำ entropy / สูง stability → เพิ่มทางเลือก
    """
    if entropy > 70 or stability < 30:
        return 2
    if entropy > 50 or stability < 50:
        return 3
    return 4


class GalaxyExpansion:
    """
    Deterministic expansion engine
    ผลลัพธ์ขึ้นกับ route + entropy + stability — ไม่ใช่ random
    """

    def expand(
        self,
        option: str,
        route:     Optional[str] = None,
        entropy:   float = 50.0,
        stability: float = 50.0,
    ) -> dict:
        """
        คืน expansion options สำหรับ option/route ที่กำหนด
        Downside First — options ที่ปลอดภัยกว่าอยู่ต้นลิสต์เสมอ

        Article 1 — depth มาจาก entropy/stability จริง
        Article 5 — COLLAPSE/SURVIVAL route ได้ options น้อยลงโดยอัตโนมัติ
        """
        r = (route or "GENERAL").upper()
        base = _ROUTE_EXPANSIONS.get(r, _ROUTE_EXPANSIONS["GENERAL"])
        depth = _expansion_depth(float(entropy), float(stability))

        selected = base[:depth]

        return {
            "option":    option,
            "route":     r,
            "entropy":   entropy,
            "stability": stability,
            "depth":     depth,
            "expansions": selected,
            "axiom":     "Downside First — protect choice before growth",
        }

    def expand_all_routes(
        self,
        option:    str,
        entropy:   float = 50.0,
        stability: float = 50.0,
    ) -> dict:
        """คืน expansion สำหรับทุก route — ใช้ใน /api/galaxy_expand"""
        return {
            route: self.expand(option, route=route, entropy=entropy, stability=stability)
            for route in _ROUTE_EXPANSIONS
        }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    ge = GalaxyExpansion()

    # determinism
    r1 = ge.expand("test", route="RISK", entropy=60, stability=45)
    r2 = ge.expand("test", route="RISK", entropy=60, stability=45)
    assert r1["expansions"] == r2["expansions"], "non-deterministic!"

    # collapse → minimal options
    rc = ge.expand("crisis", route="COLLAPSE", entropy=85, stability=20)
    assert len(rc["expansions"]) == 2
    assert rc["expansions"][0] == "emergency_exit"

    # vega → max options when stable
    rv = ge.expand("grow", route="VEGA", entropy=20, stability=80)
    assert len(rv["expansions"]) == 4

    return {"status": "OK", "module": "galaxy_expand"}


if __name__ == "__main__":
    import json
    ge = GalaxyExpansion()
    print(json.dumps(ge.expand("pivot", route="RISK", entropy=65, stability=40), indent=2))
    print(_self_test())
