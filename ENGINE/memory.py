# ENGINE/memory.py
# KING DIADEM — Session Memory
# In-process store + optional DB sync (cross-session)
# brain.py ใช้: append_turn, get_state, snapshot, reset_state

from __future__ import annotations

from dataclasses import dataclass, field
from datetime   import datetime, timezone
from threading  import Lock
from typing     import Dict, List

MAX_HISTORY = 20   # เพิ่มจาก 12 → 20 เพื่อ context ยาวขึ้น


@dataclass
class SessionState:
    history:   List[dict] = field(default_factory=list)
    seed:      str        = ""
    mode:      str        = "chat"
    waterline: float      = 50.0   # track waterline ล่าสุดของ session


_STORE: Dict[str, SessionState] = {}
_LOCK  = Lock()


# ── Core in-process store ─────────────────────────────────────────

def get_state(session_id: str) -> SessionState:
    session_id = _clean(session_id)
    with _LOCK:
        if session_id not in _STORE:
            _STORE[session_id] = SessionState()
        return _STORE[session_id]


def append_turn(
    session_id: str,
    role:       str,
    text:       str,
    waterline:  float | None = None,
) -> List[dict]:
    state = get_state(session_id)
    item  = {
        "role": role,
        "text": text,
        "at":   datetime.now(timezone.utc).isoformat(),
    }
    if waterline is not None:
        item["waterline"]   = waterline
        state.waterline     = waterline

    state.history.append(item)

    # sliding window — เก็บแค่ MAX_HISTORY รายการล่าสุด
    if len(state.history) > MAX_HISTORY:
        state.history = state.history[-MAX_HISTORY:]

    # ── async DB save (ไม่ block ถ้า DB ไม่พร้อม) ─────────────────
    _try_db_save(session_id, role, text, waterline)

    return state.history


def snapshot(session_id: str) -> List[dict]:
    """Return copy ของ history ปัจจุบัน"""
    return list(get_state(session_id).history)


def reset_state(session_id: str) -> None:
    session_id = _clean(session_id)
    with _LOCK:
        _STORE[session_id] = SessionState()


def get_waterline(session_id: str) -> float:
    """ดู waterline ล่าสุดของ session"""
    return get_state(session_id).waterline


# ── Cross-session DB sync ─────────────────────────────────────────
# ใช้ build_memory_context จาก db.py เพื่อให้ LYLA จำข้าม session

def load_from_db(session_id: str, email: str) -> None:
    """
    โหลด memory จาก DB เข้า in-process store
    เรียกตอน session เริ่มใหม่ (app.py bootChatShell)
    """
    try:
        from DATABASE.db import build_memory_context
        ctx = build_memory_context(email)
        if ctx:
            state = get_state(session_id)
            if not state.history:  # โหลดเฉพาะถ้า session ว่าง
                state.history.append({
                    "role": "system",
                    "text": ctx,
                    "at":   datetime.now(timezone.utc).isoformat(),
                })
    except Exception:
        pass  # ไม่มี DB ก็ทำงานได้ปกติ


def _try_db_save(
    session_id: str,
    role:       str,
    text:       str,
    waterline:  float | None,
) -> None:
    """Save แบบ best-effort — ไม่ crash ถ้า DB ไม่พร้อม"""
    if role != "assistant":  # save เฉพาะ reply ของ LYLA
        return
    try:
        from DATABASE.db import save_chat_state
        if save_chat_state:
            import json
            state = get_state(session_id)
            save_chat_state(session_id, json.dumps({
                "history":   state.history[-10:],  # เก็บแค่ 10 ล่าสุด
                "waterline": state.waterline,
                "savedAt":   datetime.now(timezone.utc).isoformat(),
            }, ensure_ascii=False))
    except Exception:
        pass


# ── Helpers ────────────────────────────────────────────────────────

def _clean(session_id: str) -> str:
    return (session_id or "default").strip() or "default"


def all_sessions() -> List[str]:
    """Debug helper — list active sessions"""
    with _LOCK:
        return list(_STORE.keys())
