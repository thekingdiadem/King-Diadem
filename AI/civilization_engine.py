# AI/civilization_engine.py — KING DIADEM
# FATE™ Axiom compliance: Explainability=100% · Downside First
# Fail less. Harm less. Restore more.

import json
import os
import tempfile
import threading
import time
from collections import deque

from core.paths import data_path

# กราฟอารยธรรม: ทุกการตัดสินใจเป็น 1 node — ไม่มีข้อความ/อีเมลของผู้ใช้ มีแค่เส้นทาง ตัวเลข หัวข้อ
# เก็บบนดิสก์ถาวรข้าง DB_PATH (เดิมอยู่ในหน่วยความจำอย่างเดียว รีสตาร์ทแล้วหายหมด)
_STORE = data_path("civilization_nodes.json")
_lock  = threading.Lock()
_nodes: deque[dict] = deque(maxlen=500)


def _load():
    try:
        with open(_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for n in data if isinstance(data, list) else []:
            if isinstance(n, dict) and isinstance(n.get("id"), int):
                _nodes.append(n)
    except (OSError, ValueError):
        pass


def _save():
    d = os.path.dirname(_STORE) or "."
    try:
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(list(_nodes), f, ensure_ascii=False)
        os.replace(tmp, _STORE)
    except OSError as e:
        print(f"⚠ civilization save: {type(e).__name__}")


_load()

_VALID_TYPES = {"decision", "signal", "learning", "feedback", "event", "council"}


def add_node(node: dict) -> dict:
    """
    เพิ่ม node เข้า civilization graph
    validate ก่อน — ไม่รับ node ว่าง

    Returns: node ที่เพิ่ม (พร้อม id + timestamp)
    """
    if not isinstance(node, dict) or not node:
        return {"error": "FATE_VIOLATION: node must be non-empty dict"}

    # id/recorded_at ต้องมาจากระบบ — เดิม **node อยู่ท้ายจึงเขียนทับได้ (ปลอม id/เวลา)
    # และ len()+1 ซ้ำกันเมื่อ deque เต็ม (maxlen 500)
    enriched = {
        **node,
        "id":          (_nodes[-1]["id"] + 1) if _nodes else 1,
        "recorded_at": int(time.time()),
        "node_type":   node.get("node_type", node.get("type", "event")),
    }

    if enriched["node_type"] not in _VALID_TYPES:
        enriched["node_type"] = "event"

    with _lock:
        enriched["id"] = (_nodes[-1]["id"] + 1) if _nodes else 1
        _nodes.append(enriched)
        _save()
    return enriched


def get_nodes(limit: int = 100) -> list[dict]:
    """คืน nodes ล่าสุด N รายการ"""
    try:
        limit = max(0, int(limit))
    except (TypeError, ValueError):
        limit = 100
    return list(_nodes)[-limit:] if limit else []


def node_summary() -> dict:
    """สรุปภาพรวม civilization graph"""
    all_nodes = list(_nodes)
    total     = len(all_nodes)
    if total == 0:
        return {"total": 0, "by_type": {}, "fate_note": "NO_DATA"}

    by_type: dict[str, int] = {}
    by_route: dict[str, int] = {}
    by_topic: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for n in all_nodes:
        t = n.get("node_type", "event")
        by_type[t] = by_type.get(t, 0) + 1
        for key, bucket in (("route", by_route), ("source", by_source)):
            v = n.get(key)
            if isinstance(v, str):
                bucket[v] = bucket.get(v, 0) + 1
        for tp in n.get("topics") or []:
            if isinstance(tp, str):
                by_topic[tp] = by_topic.get(tp, 0) + 1
    ws = [n["W"] for n in all_nodes if isinstance(n.get("W"), (int, float))]

    return {
        "total":      total,
        "by_type":    by_type,
        "by_route":   by_route,          # อารยธรรมกำลังเจออะไร: survival/collapse/vega/...
        "by_topic":   by_topic,          # หนี้ งาน อาหาร ความสัมพันธ์ ...
        "by_source":  by_source,         # llm / kernel — ระบบตอบได้แม้ไม่มี AI
        "mean_W":     round(sum(ws) / len(ws), 1) if ws else None,
        "latest_id":  all_nodes[-1]["id"] if all_nodes else 0,
        "fate_note":  "ACTIVE" if total > 0 else "EMPTY",
        "computed_at": int(time.time()),
    }
