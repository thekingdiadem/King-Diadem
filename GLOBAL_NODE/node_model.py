# GLOBAL_NODE/node_model.py
# KING DIADEM™ — Global Node Model
# Article 1: Reality is measured, not assumed.
# Article 5: Collapse probability must be computed, not guessed.

import threading
import time
from typing import Optional


def _num(v, d: float) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d


MAX_NODES = 5000   # node ที่ stale ไม่เคยถูกลบ → dict โตไม่หยุด

# ── Constants ────────────────────────────────────────────────────
DEFAULT_FOOD_SCORE     = 50.0
DEFAULT_RISK_SCORE     = 50.0
DEFAULT_RESOURCE_SCORE = 50.0

RISK_DANGER_THRESHOLD  = 70.0
RISK_STABLE_THRESHOLD  = 40.0

NODE_STALE_SECONDS     = 300   # node ที่ไม่ได้ update > 5 นาที ถือว่า stale


class GlobalNode:
    """
    World state aggregator — รวบรวม node จากทุก location
    แล้วคำนวณ world_state ที่ใช้ใน eternal_snapshot

    Article 1 — ค่าทุกตัวมาจาก node จริง ไม่ hardcode
    Article 5 — collapse_probability คำนวณจาก risk + resource จริง
    """

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.world_state: dict = self._blank_world_state()
        self._lock = threading.Lock()

    # ── Node registration ─────────────────────────────────────────
    def register_node(self, location: str, data: dict) -> None:
        """
        บันทึก / update node
        data ควรมี: food_score, risk_score, resource_score (ถ้าไม่มีใช้ default)
        """
        if not isinstance(data, dict):
            data = {}
        location = str(location)[:120]

        with self._lock:
            if location not in self.nodes and len(self.nodes) >= MAX_NODES:
                now = time.time()
                for loc in [l for l, n in self.nodes.items() if now - n["time"] > NODE_STALE_SECONDS]:
                    self.nodes.pop(loc, None)
                if len(self.nodes) >= MAX_NODES:
                    self.nodes.pop(min(self.nodes, key=lambda l: self.nodes[l]["time"]))
            self.nodes[location] = {
                "data":      data,
                "time":      time.time(),
                "location":  location,
            }

    def remove_node(self, location: str) -> bool:
        if location in self.nodes:
            del self.nodes[location]
            return True
        return False

    # ── World state computation ───────────────────────────────────
    def update_world_state(self) -> dict:
        """
        คำนวณ world_state จาก active nodes
        ถ้าไม่มี node — คืน blank state (ไม่ crash)

        Article 1 — ค่าเฉลี่ยมาจาก node จริง
        Article 5 — collapse_probability = f(risk, resource)
        """
        active = self._active_nodes()

        if not active:
            self.world_state = self._blank_world_state()
            self.world_state["source"] = "no_nodes"
            return self.world_state

        food_sum     = 0.0
        risk_sum     = 0.0
        resource_sum = 0.0
        count        = len(active)

        for node in active.values():
            d = node["data"]
            food_sum     += _num(d.get("food_score"),     DEFAULT_FOOD_SCORE)
            risk_sum     += _num(d.get("risk_score"),     DEFAULT_RISK_SCORE)
            resource_sum += _num(d.get("resource_score"), DEFAULT_RESOURCE_SCORE)

        food_index     = round(food_sum     / count, 2)
        risk_index     = round(risk_sum     / count, 2)
        resource_index = round(resource_sum / count, 2)

        # trend
        if risk_index > RISK_DANGER_THRESHOLD:
            trend = "danger"
        elif risk_index < RISK_STABLE_THRESHOLD:
            trend = "stable"
        else:
            trend = "warning"

        # collapse_probability — weighted: risk 60%, resource inverse 40%
        resource_deficit = max(0.0, (50.0 - resource_index) / 50.0)
        collapse_prob    = round(
            min(1.0, (risk_index / 100.0) * 0.6 + resource_deficit * 0.4), 4
        )

        self.world_state = {
            "food_index":           food_index,
            "risk_index":           risk_index,
            "resource_index":       resource_index,
            "trend":                trend,
            "collapse_probability": collapse_prob,
            "active_nodes":         count,
            "stale_nodes":          len(self.nodes) - count,
            "source":               "computed",
            "updated_at":           time.time(),
        }

        return self.world_state

    # ── Helpers ───────────────────────────────────────────────────
    def _active_nodes(self) -> dict:
        """คืนเฉพาะ node ที่ยังไม่ stale"""
        now = time.time()
        with self._lock:
            items = list(self.nodes.items())
        return {
            loc: n for loc, n in items
            if (now - n["time"]) <= NODE_STALE_SECONDS
        }

    def node_count(self) -> int:
        return len(self.nodes)

    def active_node_count(self) -> int:
        return len(self._active_nodes())

    @staticmethod
    def _blank_world_state() -> dict:
        return {
            "food_index":           DEFAULT_FOOD_SCORE,
            "risk_index":           DEFAULT_RISK_SCORE,
            "resource_index":       DEFAULT_RESOURCE_SCORE,
            "trend":                "stable",
            "collapse_probability": 0.0,
            "active_nodes":         0,
            "stale_nodes":          0,
            "source":               "blank",
            "updated_at":           time.time(),
        }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    node = GlobalNode()
    assert node.active_node_count() == 0

    node.register_node("bangkok", {"food_score": 60, "risk_score": 80, "resource_score": 30})
    node.register_node("chonburi", {"food_score": 55, "risk_score": 75, "resource_score": 40})

    ws = node.update_world_state()
    assert ws["trend"] == "danger", f"expected danger got {ws['trend']}"
    assert ws["collapse_probability"] > 0.5
    assert ws["active_nodes"] == 2
    assert ws["source"] == "computed"

    node.remove_node("bangkok")
    ws2 = node.update_world_state()
    assert ws2["active_nodes"] == 1

    return {"status": "OK", "module": "node_model", "sample_world": ws}


if __name__ == "__main__":
    import json
    print(json.dumps(_self_test(), indent=2, default=str))
