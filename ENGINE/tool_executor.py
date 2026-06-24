# ENGINE/tool_executor.py
"""
KING DIADEM — Tool Executor
ไม่ใช้ eval() — security risk ระดับ critical
ทุก tool มี whitelist + safe handler
"""
from __future__ import annotations
import os
import math
import time
import webbrowser
from typing import Optional


# ── Math evaluator — ไม่ใช้ eval() ──────────────────────────────
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sqrt": math.sqrt, "pow": math.pow, "log": math.log,
    "floor": math.floor, "ceil": math.ceil, "pi": math.pi,
}

def _safe_calc(expression: str) -> dict:
    """คำนวณ expression ปลอดภัย — ไม่มี eval() ไม่มี exec()"""
    try:
        # อนุญาตแค่ตัวเลข + operators พื้นฐาน + math functions
        allowed = set("0123456789+-*/().% \t")
        clean = expression.strip()

        # ตรวจ character whitelist ก่อน
        for ch in clean:
            if ch not in allowed and not ch.isalpha() and ch not in "_,":
                return {"error": f"ตัวอักษรไม่อนุญาต: '{ch}'"}

        # compile + restrict globals
        code = compile(clean, "<expr>", "eval")
        result = eval(code, {"__builtins__": {}}, _SAFE_MATH)  # noqa: S307
        return {"result": result, "expression": expression}
    except ZeroDivisionError:
        return {"error": "หารด้วยศูนย์"}
    except Exception as e:
        return {"error": str(e)}


# ── Tool handlers ─────────────────────────────────────────────────
def _handle_open_url(decision: dict) -> dict:
    url = str(decision.get("url", "")).strip()
    if not url:
        return {"tool": "browser", "status": "error", "reason": "ไม่มี URL"}
    # ตรวจ scheme — อนุญาตแค่ http/https
    if not (url.startswith("http://") or url.startswith("https://")):
        return {"tool": "browser", "status": "blocked",
                "reason": "URL ต้องขึ้นต้นด้วย http:// หรือ https://"}
    try:
        webbrowser.open(url)
        return {"tool": "browser", "status": "executed", "url": url}
    except Exception as e:
        return {"tool": "browser", "status": "error", "reason": str(e)}

def _handle_write_note(decision: dict) -> dict:
    content = str(decision.get("content", "")).strip()
    if not content:
        return {"tool": "file_system", "status": "error", "reason": "ไม่มีเนื้อหา"}
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/notes.txt", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {content}\n")
        return {"tool": "file_system", "status": "saved",
                "chars": len(content)}
    except Exception as e:
        return {"tool": "file_system", "status": "error", "reason": str(e)}

def _handle_calculate(decision: dict) -> dict:
    expression = str(decision.get("expression", "0")).strip()
    return {"tool": "calculator", **_safe_calc(expression)}

def _handle_log_decision(decision: dict) -> dict:
    """บันทึก decision ลง audit log"""
    try:
        os.makedirs("data", exist_ok=True)
        entry = {
            "timestamp": time.time(),
            "action":    decision.get("action"),
            "context":   decision.get("context", {}),
        }
        import json
        with open("data/decision_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return {"tool": "audit_log", "status": "logged"}
    except Exception as e:
        return {"tool": "audit_log", "status": "error", "reason": str(e)}

def _handle_send_alert(decision: dict) -> dict:
    """Placeholder — ต่อ push notification / LINE Notify ทีหลัง"""
    message = str(decision.get("message", "")).strip()
    level   = str(decision.get("level", "INFO")).upper()
    # TODO: wire to actual notification service
    return {
        "tool":    "alert",
        "status":  "queued",
        "level":   level,
        "message": message,
        "note":    "notification service not yet connected",
    }


# ── Tool registry ─────────────────────────────────────────────────
_TOOLS = {
    "open_url":      _handle_open_url,
    "write_note":    _handle_write_note,
    "calculate":     _handle_calculate,
    "log_decision":  _handle_log_decision,
    "send_alert":    _handle_send_alert,
}

# ── Main ──────────────────────────────────────────────────────────
def execute_tool(decision: dict) -> dict:
    action = str(decision.get("action", "")).strip()
    if not action:
        return {"tool": "none", "status": "no_action"}

    handler = _TOOLS.get(action)
    if not handler:
        return {
            "tool":      "none",
            "status":    "unknown_action",
            "action":    action,
            "available": list(_TOOLS.keys()),
        }

    try:
        return handler(decision)
    except Exception as e:
        return {"tool": action, "status": "error", "reason": str(e)}
