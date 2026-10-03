# NETWORK/node_sync.py
# KING DIADEM — Network Sync & Health
# health จาก waterline data จริง ไม่ใช่แค่นับ node

from __future__ import annotations
import time

from NETWORK.node_registry import get_nodes, remove_dead_nodes


def network_status() -> dict:
    """
    สถานะ network จริง — รวม node health + waterline + drift
    เรียกจาก /health endpoint หรือ galaxy API
    """
    nodes = get_nodes()
    n     = len(nodes)
    now   = time.time()

    # ── Node health ───────────────────────────────────────────────
    active_nodes   = []
    stale_nodes    = []
    waterlines     = []

    for node_id, data in nodes.items():
        try:
            age = now - float(data.get("last_seen", now))
        except (TypeError, ValueError):
            age = float("inf")       # อ่านเวลาไม่ได้ = ถือว่า stale
        wl  = data.get("waterline")

        if age < 30:
            active_nodes.append(node_id)
        else:
            stale_nodes.append(node_id)

        if wl is not None:
            try:
                waterlines.append(float(wl))
            except Exception:
                pass

    # ── Network waterline ─────────────────────────────────────────
    avg_waterline = sum(waterlines) / len(waterlines) if waterlines else 50.0

    # ── Health label — ใช้ waterline + active ratio ──────────────
    active_ratio = (len(active_nodes) / n) if n > 0 else 0.0

    if n == 0:
        health = "offline"
    elif avg_waterline < 25 or active_ratio < 0.3:
        health = "critical"
    elif avg_waterline < 50 or active_ratio < 0.6:
        health = "degraded"
    elif n >= 100:
        health = "planetary"
    elif n >= 10:
        health = "expanding"
    else:
        health = "stable"

    # ── Drift risk ────────────────────────────────────────────────
    drift_risk = (
        "HIGH"     if avg_waterline < 30 else
        "MODERATE" if avg_waterline < 55 else
        "LOW"
    )

    return {
        "active_nodes":    n,
        "active_recently": len(active_nodes),
        "stale_nodes":     len(stale_nodes),
        "network_health":  health,
        "avg_waterline":   round(avg_waterline, 1),
        "drift_risk":      drift_risk,
        "axiom":           f"Choice(t) = {max(1, n)} → collapse = False",
        "ts":              now,
    }


def sync_node_waterline(node_id: str, waterline: float) -> bool:
    """
    อัปเดต waterline ของ node — เรียกจาก app.py หลัง /run
    ทำให้ galaxy API แสดง waterline จริงของแต่ละ node
    """
    try:
        from NETWORK.node_registry import heartbeat, _conn, _lock
        import time

        with _lock:
            conn = _conn()
            try:
                conn.execute("""
                    UPDATE network_nodes
                    SET last_seen = ?,
                        meta = json_set(COALESCE(meta, '{}'), '$.waterline', ?)
                    WHERE node_id = ?
                """, (time.time(), max(0.0, min(100.0, float(waterline))), str(node_id)))
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception:
        # fallback: แค่ heartbeat ถ้า json_set ไม่รองรับ SQLite version นั้น
        try:
            from NETWORK.node_registry import heartbeat
            return heartbeat(node_id)
        except Exception:
            return False
