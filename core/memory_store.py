"""
core/memory_store.py
MEMORY STORE — KING DIADEM CORE LAYER v2

ปัญหาของ v1 (ChatGPT):
  - ไม่มี file locking → concurrent requests ทำ JSON corrupt
  - ไม่มี max size → decision_log.json โตไม่หยุดบน Render
  - bare except กลืน error เงียบ
  - ไม่มี trim / rotation
"""

import json
import os
import fcntl
from datetime import datetime

DATA_DIR    = "data"
MAX_ENTRIES = 500  # Render disk limit guard

WORLD_HISTORY = os.path.join(DATA_DIR, "world_history.json")
NODE_REGISTRY = os.path.join(DATA_DIR, "node_registry.json")
DECISION_LOG  = os.path.join(DATA_DIR, "decision_log.json")

os.makedirs(DATA_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# SAFE I/O — file lock ป้องกัน concurrent corrupt
# ─────────────────────────────────────────────

def load_json(path: str) -> list:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_json(path: str, data: list) -> None:
    # trim ก่อน save — ป้องกัน disk overflow บน Render
    if len(data) > MAX_ENTRIES:
        data = data[-MAX_ENTRIES:]
    try:
        with open(path, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2, ensure_ascii=False)
            fcntl.flock(f, fcntl.LOCK_UN)
    except OSError as e:
        # log ไม่ได้ → ไม่ crash ระบบหลัก
        print(f"[MEMORY_STORE] save_json failed: {e}")


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────

def log_decision(decision: dict | str) -> None:
    """บันทึก decision พร้อม timestamp"""
    data = load_json(DECISION_LOG)
    data.append({
        "time":     datetime.utcnow().isoformat(),
        "decision": decision,
    })
    save_json(DECISION_LOG, data)


def register_node(location: str, node_data: dict) -> None:
    """ลงทะเบียน node ใหม่ใน registry"""
    data = load_json(NODE_REGISTRY)
    data.append({
        "time":     datetime.utcnow().isoformat(),
        "location": location,
        "data":     node_data,
    })
    save_json(NODE_REGISTRY, data)


def log_world_state(state: dict) -> None:
    """บันทึก world state snapshot"""
    data = load_json(WORLD_HISTORY)
    data.append({
        "time":  datetime.utcnow().isoformat(),
        "state": state,
    })
    save_json(WORLD_HISTORY, data)


def get_recent_decisions(n: int = 10) -> list:
    """ดึง decision ล่าสุด n รายการ"""
    return load_json(DECISION_LOG)[-n:]


def get_node(location: str) -> dict | None:
    """หา node ล่าสุดตาม location"""
    data = load_json(NODE_REGISTRY)
    matches = [e for e in data if e.get("location") == location]
    return matches[-1] if matches else None


def purge_log(path: str) -> None:
    """ล้าง log — ใช้เฉพาะ maintenance / test"""
    save_json(path, [])
