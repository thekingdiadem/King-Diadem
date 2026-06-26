"""
WORLD_MODEL/human_state.py — KING DIADEM™
Human State Engine — สภาวะมนุษย์จริง ไม่ใช่ hardcode

Architect: Nithikorn Bunsrang
SCL-7 A1: Logic must never erase warmth.
LAYER 4 — HUMAN ENTROPY BUFFER:
  ระบบต้องยอมรับขีดจำกัดของเวลา พลังชีวิต และทรัพยากรมนุษย์
"""

import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# HUMAN STATE DIMENSIONS
# ══════════════════════════════════════════════════════════════════

# thresholds
ENERGY_FLOOR      = 0.2   # ต่ำกว่านี้ = หมดแรง
STRESS_CEILING    = 0.8   # สูงกว่านี้ = overwhelmed
RESOURCE_FLOOR    = 0.2   # ต่ำกว่านี้ = survival territory
SUPPORT_FLOOR     = 0.2   # ต่ำกว่านี้ = โดดเดี่ยว

# Vega/Lyla kernel profiles
KERNEL_PROFILES = {
    "VEGA": {
        "desc":    "Albino — ปลอดภัยก่อน เคลื่อนไหวระมัดระวัง entropy-sensitive",
        "bias":    {"energy_weight": 0.4, "stress_weight": 0.4, "resource_weight": 0.2},
        "trigger": "SYSTEM_PAUSE บ่อยกว่า — รักษาเสถียรภาพผ่านการถอย",
    },
    "LYLA": {
        "desc":    "Standard — เคลื่อนไหวกว้าง noise-tolerant รักษาเสถียรภาพผ่านความอดทน",
        "bias":    {"energy_weight": 0.3, "stress_weight": 0.3, "resource_weight": 0.4},
        "trigger": "drift ช้ากว่าภายใต้ load",
    },
}


class HumanState:
    """
    สภาวะมนุษย์ — อัปเดตได้จาก input จริง
    ใช้ใน gateway, response engine, time_engine
    """

    def __init__(self,
                 energy:         float = 0.7,
                 stress:         float = 0.3,
                 resources:      float = 0.5,
                 social_support: float = 0.4,
                 time_pressure:  float = 0.2,
                 kernel:         str   = "LYLA"):

        self.energy         = round(max(0.0, min(1.0, energy)),         4)
        self.stress         = round(max(0.0, min(1.0, stress)),         4)
        self.resources      = round(max(0.0, min(1.0, resources)),      4)
        self.social_support = round(max(0.0, min(1.0, social_support)), 4)
        self.time_pressure  = round(max(0.0, min(1.0, time_pressure)),  4)
        self.kernel         = kernel if kernel in KERNEL_PROFILES else "LYLA"
        self.updated_at     = time.time()

    # ── Core metrics ──────────────────────────────────────────────
    def risk_tolerance(self) -> float:
        """
        ความสามารถรับความเสี่ยง
        = (energy + resources) / 2 - stress - time_pressure * 0.3
        bounded 0–1
        """
        raw = (self.energy + self.resources) / 2.0 - self.stress - self.time_pressure * 0.3
        return round(max(0.0, min(1.0, raw)), 4)

    def decision_capacity(self) -> float:
        """
        ความสามารถตัดสินใจ — ลด ถ้า stress สูง หรือ energy ต่ำ
        """
        raw = (self.energy * 0.4 + self.social_support * 0.2
               - self.stress * 0.3 - self.time_pressure * 0.1)
        return round(max(0.0, min(1.0, raw)), 4)

    def entropy_level(self) -> float:
        """
        human entropy = ความไม่สมดุลภายใน
        สูง = ต้องการ SYSTEM_PAUSE
        """
        values = [self.energy, 1 - self.stress, self.resources,
                  self.social_support, 1 - self.time_pressure]
        mean   = sum(values) / len(values)
        var    = sum((v - mean) ** 2 for v in values) / len(values)
        return round(var * 100, 2)

    # ── Status checks ─────────────────────────────────────────────
    def is_at_survival_floor(self) -> bool:
        """ถ้าใช่ = ต้องช่วยเรื่อง survival ก่อน ไม่ใช่ optimize"""
        return (self.energy < ENERGY_FLOOR or
                self.resources < RESOURCE_FLOOR)

    def needs_pause(self) -> bool:
        """ถ้าใช่ = ระบบควร SYSTEM_PAUSE ก่อนดำเนินการต่อ"""
        return (self.stress > STRESS_CEILING or
                self.decision_capacity() < 0.2 or
                self.is_at_survival_floor())

    def is_isolated(self) -> bool:
        return self.social_support < SUPPORT_FLOOR

    # ── Update ────────────────────────────────────────────────────
    def update(self, **kwargs) -> "HumanState":
        """อัปเดต dimension — bounded 0–1"""
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, round(max(0.0, min(1.0, float(v))), 4))
        self.updated_at = time.time()
        return self

    # ── Snapshot ──────────────────────────────────────────────────
    def snapshot(self) -> dict:
        """full state สำหรับ gateway / eternal_snapshot"""
        profile = KERNEL_PROFILES[self.kernel]
        return {
            "energy":            self.energy,
            "stress":            self.stress,
            "resources":         self.resources,
            "social_support":    self.social_support,
            "time_pressure":     self.time_pressure,
            "kernel":            self.kernel,
            "kernel_desc":       profile["desc"],
            "risk_tolerance":    self.risk_tolerance(),
            "decision_capacity": self.decision_capacity(),
            "entropy_level":     self.entropy_level(),
            "at_survival_floor": self.is_at_survival_floor(),
            "needs_pause":       self.needs_pause(),
            "is_isolated":       self.is_isolated(),
            "updated_at":        self.updated_at,
            "seal":              "ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง",
        }

    def get_response_mode(self) -> str:
        """
        คืน mode สำหรับ response engine
        CRISIS / SURVIVAL / CAUTIOUS / NORMAL
        """
        if self.stress > STRESS_CEILING or self.energy < ENERGY_FLOOR:
            return "CRISIS"
        if self.is_at_survival_floor():
            return "SURVIVAL"
        if self.risk_tolerance() < 0.3:
            return "CAUTIOUS"
        return "NORMAL"


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # default
    h = HumanState()
    assert 0.0 <= h.risk_tolerance() <= 1.0
    assert 0.0 <= h.decision_capacity() <= 1.0

    # survival floor
    h2 = HumanState(energy=0.1, resources=0.1)
    assert h2.is_at_survival_floor() is True
    assert h2.needs_pause() is True
    assert h2.get_response_mode() in ("CRISIS", "SURVIVAL")

    # stressed
    h3 = HumanState(stress=0.9)
    assert h3.needs_pause() is True
    assert h3.get_response_mode() == "CRISIS"

    # healthy
    h4 = HumanState(energy=0.9, stress=0.1, resources=0.9)
    assert h4.is_at_survival_floor() is False
    assert h4.get_response_mode() == "NORMAL"

    # update
    h4.update(stress=0.9)
    assert h4.stress == 0.9

    # VEGA kernel
    hv = HumanState(kernel="VEGA")
    assert hv.kernel == "VEGA"

    snap = h4.snapshot()
    assert "risk_tolerance" in snap
    assert "needs_pause" in snap

    return {"status": "OK", "module": "human_state"}


if __name__ == "__main__":
    import json
    h = HumanState(energy=0.5, stress=0.6, resources=0.3, kernel="VEGA")
    print(json.dumps(h.snapshot(), indent=2, ensure_ascii=False, default=str))
    print(_self_test())
