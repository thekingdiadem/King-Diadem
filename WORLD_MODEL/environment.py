"""
WORLD_MODEL/environment.py — KING DIADEM™
Environment State Engine
ตรวจสภาพแวดล้อมจริง — ไม่ใช่แค่ dict ว่างๆ

Architect: Nithikorn Bunsrang
FATE™: Reality + Evidence − Drift = Governance
P2: ระบบใดที่ลืม entropy ระบบนั้นล้มเหลว
"""

import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# ENVIRONMENT STATE — ค่าจริงจาก world signal
# ══════════════════════════════════════════════════════════════════

DEFAULT_STATE = {
    "economic_pressure":    0.5,   # 0=ไม่มีแรงกดดัน / 1=วิกฤต
    "social_instability":   0.3,   # 0=เสถียร / 1=ไม่เสถียร
    "technology_change":    0.7,   # 0=ไม่เปลี่ยน / 1=เปลี่ยนเร็วมาก
    "resource_scarcity":    0.4,   # 0=ทรัพยากรพอ / 1=ขาดแคลน
    "climate_pressure":     0.5,   # 0=ปกติ / 1=วิกฤต
    "information_noise":    0.6,   # 0=ชัดเจน / 1=สับสน
    "political_instability":0.3,   # 0=เสถียร / 1=ไม่เสถียร
    "food_security":        0.6,   # 0=ขาดแคลน / 1=มั่นคง
    "water_security":       0.7,   # 0=ขาดแคลน / 1=มั่นคง
}

# thresholds
PRESSURE_HIGH   = 0.7
PRESSURE_MEDIUM = 0.4
SCARCITY_FLOOR  = 0.3   # ต่ำกว่านี้ = SURVIVAL territory

# ══════════════════════════════════════════════════════════════════
# ENVIRONMENT STATE ENGINE
# ══════════════════════════════════════════════════════════════════

class EnvironmentState:
    """
    World environment state — อัปเดตได้จาก real-world signals
    ใช้ใน world_intel, eternal_snapshot, collapse_predictor
    """

    def __init__(self, initial: Optional[dict] = None):
        self.state      = dict(DEFAULT_STATE)
        self.history    = []
        self.updated_at = time.time()
        if initial:
            self.update(initial)

    def update(self, delta: dict) -> dict:
        """อัปเดต state จาก signal ใหม่ — บันทึก history"""
        if not isinstance(delta, dict):
            delta = {}
        for k, v in delta.items():
            if k in self.state:
                try:
                    x = float(v)
                except (TypeError, ValueError):
                    continue
                if x != x:  # NaN
                    continue
                old = self.state[k]
                self.state[k] = round(max(0.0, min(1.0, x)), 4)
                self.history.append({
                    "key": k, "from": old, "to": self.state[k],
                    "at": time.time()
                })
        if len(self.history) > 500:  # instance ระดับโมดูลอยู่ตลอดอายุ process
            del self.history[:-500]
        self.updated_at = time.time()
        return self.state

    def get_pressure_level(self) -> dict:
        """คำนวณ overall pressure จากทุก dimension"""
        econ    = self.state["economic_pressure"]
        social  = self.state["social_instability"]
        tech    = self.state["technology_change"]
        resource= self.state["resource_scarcity"]

        # weighted average
        overall = round(
            econ * 0.35 + social * 0.25 + resource * 0.25 + tech * 0.15, 4
        )

        if overall >= PRESSURE_HIGH:
            level = "CRITICAL"
        elif overall >= PRESSURE_MEDIUM:
            level = "WARNING"
        else:
            level = "STABLE"

        return {
            "overall_pressure": overall,
            "level":            level,
            "economic":         econ,
            "social":           social,
            "resource":         resource,
            "technology":       tech,
        }

    def check_survival_floor(self) -> dict:
        """ตรวจว่า food/water security ยังอยู่เหนือ survival floor ไหม"""
        food  = self.state["food_security"]
        water = self.state["water_security"]

        food_ok  = food  >= SCARCITY_FLOOR
        water_ok = water >= SCARCITY_FLOOR

        return {
            "food_secure":   food_ok,
            "water_secure":  water_ok,
            "survival_ok":   food_ok and water_ok,
            "food_level":    food,
            "water_level":   water,
            "floor":         SCARCITY_FLOOR,
            "halt":          not (food_ok and water_ok),
        }

    def compute_entropy(self) -> float:
        """
        entropy = variance ของ state values × 100
        สูง = ระบบไม่สมดุล ต้อง stabilize ก่อน optimize
        """
        values = list(self.state.values())
        mean   = sum(values) / len(values)
        var    = sum((v - mean) ** 2 for v in values) / len(values)
        return round(var * 100, 2)

    def snapshot(self) -> dict:
        """full snapshot สำหรับ eternal_snapshot"""
        pressure = self.get_pressure_level()
        survival = self.check_survival_floor()
        entropy  = self.compute_entropy()

        return {
            "state":        self.state,
            "pressure":     pressure,
            "survival":     survival,
            "entropy":      entropy,
            "updated_at":   self.updated_at,
            "equation":     "Reality + Evidence − Drift = Governance",
        }


# module-level instance สำหรับ import
_env = EnvironmentState()

def get_environment_state() -> dict:
    return _env.snapshot()

def update_environment(delta: dict) -> dict:
    return _env.update(delta)

def get_entropy() -> float:
    return _env.compute_entropy()


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    env = EnvironmentState()

    # default state exists
    snap = env.snapshot()
    assert "economic_pressure" in snap["state"]
    assert "entropy" in snap

    # update
    env.update({"economic_pressure": 0.9})
    assert env.state["economic_pressure"] == 0.9

    # pressure level
    env.update({"economic_pressure": 0.8, "social_instability": 0.8, "resource_scarcity": 0.8})
    p = env.get_pressure_level()
    assert p["level"] == "CRITICAL"

    # survival floor
    env.update({"food_security": 0.1, "water_security": 0.1})
    s = env.check_survival_floor()
    assert s["halt"] is True

    return {"status": "OK", "module": "environment"}


if __name__ == "__main__":
    import json
    env = EnvironmentState()
    print(json.dumps(env.snapshot(), indent=2, ensure_ascii=False, default=str))
    print(_self_test())
