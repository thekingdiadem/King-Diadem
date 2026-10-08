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
import tempfile
import threading
from datetime import datetime, timezone
from core.paths import data_dir

DATA_DIR    = data_dir()   # ข้าง DB_PATH (ดิสก์ถาวร) — ดู core/paths.py
MAX_ENTRIES = 500  # Render disk limit guard

WORLD_HISTORY = os.path.join(DATA_DIR, "world_history.json")
NODE_REGISTRY = os.path.join(DATA_DIR, "node_registry.json")
DECISION_LOG  = os.path.join(DATA_DIR, "decision_log.json")

_LOCK = threading.Lock()   # read-modify-write ทั้งก้อนต้องอยู่ใต้ lock เดียว ไม่งั้น append หาย


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────
# SAFE I/O — file lock ป้องกัน concurrent corrupt
# ─────────────────────────────────────────────

def load_json(path: str) -> list:
    if not isinstance(path, (str, os.PathLike)) or not os.path.exists(path):
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
    if not isinstance(path, (str, os.PathLike)):
        return
    data = data if isinstance(data, list) else []
    # trim ก่อน save — ป้องกัน disk overflow บน Render
    if len(data) > MAX_ENTRIES:
        data = data[-MAX_ENTRIES:]
    # เดิมเปิด "w" (ล้างไฟล์ทันทีก่อนได้ lock) → คนอ่านพร้อมกันเห็นไฟล์ว่าง/ครึ่งไฟล์
    # ตอนนี้เขียนไฟล์ชั่วคราวแล้ว os.replace (atomic)
    try:
        d = os.path.dirname(path) or "."
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            os.replace(tmp, path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except (OSError, TypeError, ValueError) as e:
        # log ไม่ได้ → ไม่ crash ระบบหลัก
        print(f"[MEMORY_STORE] save_json failed: {type(e).__name__}")


def _append(path: str, entry: dict) -> None:
    with _LOCK:
        data = load_json(path)
        data.append(entry)
        save_json(path, data)


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────

def log_decision(decision: dict | str) -> None:
    """บันทึก decision พร้อม timestamp"""
    _append(DECISION_LOG, {"time": _now(), "decision": decision})


def register_node(location: str, node_data: dict) -> None:
    """ลงทะเบียน node ใหม่ใน registry"""
    _append(NODE_REGISTRY, {"time": _now(), "location": location, "data": node_data})


def log_world_state(state: dict) -> None:
    """บันทึก world state snapshot"""
    _append(WORLD_HISTORY, {"time": _now(), "state": state})


def get_recent_decisions(n: int = 10) -> list:
    """ดึง decision ล่าสุด n รายการ"""
    try:
        n = max(0, int(n))
    except (TypeError, ValueError):
        n = 10
    return load_json(DECISION_LOG)[-n:] if n else []


def get_node(location: str) -> dict | None:
    """หา node ล่าสุดตาม location"""
    data = load_json(NODE_REGISTRY)
    matches = [e for e in data if isinstance(e, dict) and e.get("location") == location]
    return matches[-1] if matches else None


def purge_log(path: str) -> None:
    """ล้าง log — ใช้เฉพาะ maintenance / test (เฉพาะไฟล์ของ store นี้)"""
    if path in (WORLD_HISTORY, NODE_REGISTRY, DECISION_LOG):
        with _LOCK:
            save_json(path, [])
