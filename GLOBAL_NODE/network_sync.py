# GLOBAL_NODE/network_sync.py
# KING DIADEM™ — Network Sync Bridge
# Article 4: State must flow through one canonical path.
# Article 6: No module-level singleton that breaks under multi-worker deploy.

import time
from typing import Optional
from GLOBAL_NODE.node_model import GlobalNode

# ── Process-local node instance ──────────────────────────────────
# NOTE: ถ้าใช้ Gunicorn multi-worker แต่ละ process จะมี instance แยก
# ซึ่งเป็น acceptable tradeoff สำหรับ Render free-tier (single worker)
# ถ้า scale ขึ้น → ย้าย world_state ไปเก็บใน SQLite / Redis แทน
_node: Optional[GlobalNode] = None


def _get_node() -> GlobalNode:
    """lazy init — สร้าง GlobalNode เมื่อมีการเรียกครั้งแรก ไม่ใช่ตอน import"""
    global _node
    if _node is None:
        _node = GlobalNode()
    return _node


# ── Public API ────────────────────────────────────────────────────
def sync_node(location: str, data: dict) -> dict:
    """
    register node แล้วคืน world_state ล่าสุด
    ใช้เมื่อต้องการ sync ข้อมูลจาก location เฉพาะ

    Article 4 — state ไหลผ่าน GlobalNode เดียว ไม่กระจายข้ามฟังก์ชัน
    """
    node = _get_node()
    node.register_node(location, data)
    return node.update_world_state()


def sync_state(system_state: dict) -> dict:
    """
    รองรับ eternal_snapshot — sync system_state เข้า global node
    คืน world_state merged กับ system_state

    Article 4 — เรียกจาก eternal_snapshot() เท่านั้น
    """
    if not isinstance(system_state, dict):
        return system_state

    try:
        world = sync_node("eternal", system_state)
        # merge world_state เข้า system_state โดยไม่ overwrite key หลัก
        merged = dict(system_state)
        merged["world_state"] = world
        merged["sync_at"]     = time.time()
        return merged
    except Exception:
        # ห้าม crash eternal_snapshot เพราะ sync ล้มเหลว (ไม่ส่งข้อความ exception ออกไป)
        system_state["world_state"] = {"error": "SYNC_FAILED", "source": "sync_failed"}
        return system_state


def get_world_state() -> dict:
    """
    คืน world_state ปัจจุบันโดยไม่ต้อง sync ใหม่
    ใช้ใน /api/kernel_snapshot
    """
    node = _get_node()
    return node.update_world_state()


def remove_node(location: str) -> bool:
    """ลบ node ออกจาก world model"""
    return _get_node().remove_node(location)


def node_stats() -> dict:
    """สถิติ node สำหรับ debug / monitoring"""
    node = _get_node()
    return {
        "total_nodes":  node.node_count(),
        "active_nodes": node.active_node_count(),
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    global _node
    _node = None  # reset สำหรับ test

    state = {"entropy": 45, "stability": 65, "food_score": 60, "risk_score": 55}
    result = sync_state(state)

    assert "world_state" in result, "world_state missing"
    assert "sync_at" in result
    assert result["world_state"]["source"] == "computed"

    ws = get_world_state()
    assert ws["active_nodes"] >= 1

    _node = None  # cleanup
    return {"status": "OK", "module": "network_sync"}


if __name__ == "__main__":
    print(_self_test())
