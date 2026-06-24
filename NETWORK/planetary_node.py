# NETWORK/planetary_node.py
# KING DIADEM — Planetary Node
# node ที่ persistent ใน DB + รายงาน waterline จริง

from __future__ import annotations
import uuid
import socket
import time

from NETWORK.node_registry import register_node, heartbeat

_NODE_ID: str | None = None


def start_node(waterline: float = 50.0) -> dict:
    """
    เริ่ม node ของ instance นี้
    เรียกตอน app.py startup
    """
    global _NODE_ID
    if _NODE_ID is None:
        _NODE_ID = str(uuid.uuid4())

    host = "unknown"
    try:
        host = socket.gethostname()
    except Exception:
        pass

    data = {
        "host":      host,
        "started":   time.time(),
        "status":    "active",
        "waterline": waterline,
    }
    register_node(_NODE_ID, data)

    return {
        "node_id":  _NODE_ID,
        "host":     host,
        "waterline": waterline,
        "status":   "active",
    }


def node_heartbeat(waterline: float | None = None) -> bool:
    """
    ส่ง heartbeat + อัปเดต waterline ถ้ามี
    เรียกจาก galaxy_scene_api.js polling loop หรือ app.py
    """
    if not _NODE_ID:
        return False

    if waterline is not None:
        try:
            from NETWORK.node_sync import sync_node_waterline
            return sync_node_waterline(_NODE_ID, waterline)
        except Exception:
            pass

    return heartbeat(_NODE_ID)


def get_node_id() -> str | None:
    """Return node ID ของ instance นี้"""
    return _NODE_ID


def stop_node() -> bool:
    """Mark node ว่า offline ก่อน shutdown"""
    if not _NODE_ID:
        return False
    try:
        from NETWORK.node_registry import _conn, _lock
        with _lock:
            conn = _conn()
            try:
                conn.execute(
                    "UPDATE network_nodes SET status = 'offline' WHERE node_id = ?",
                    (_NODE_ID,),
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception:
        return False
