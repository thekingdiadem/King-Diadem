# ENGINE/tool_executor.py
"""
KING DIADEM — Tool Executor
ไม่ใช้ eval() — security risk ระดับ critical (v2: เอา eval ที่เหลืออยู่ออกจริงแล้ว)
ทุก tool มี whitelist + safe handler
"""
from __future__ import annotations
import os
import math
import time
from typing import Optional


# ── Math evaluator — ไม่ใช้ eval() ──────────────────────────────
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sqrt": math.sqrt, "pow": math.pow, "log": math.log,
    "floor": math.floor, "ceil": math.ceil, "pi": math.pi,
}

import ast
import operator as _op

_BIN = {ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul, ast.Div: _op.truediv,
        ast.FloorDiv: _op.floordiv, ast.Mod: _op.mod, ast.Pow: _op.pow}
_UNARY = {ast.UAdd: _op.pos, ast.USub: _op.neg}
_MAX_ABS = 1e15


def _eval_node(n):
    if isinstance(n, ast.Expression):
        return _eval_node(n.body)
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return n.value
    if isinstance(n, ast.Name) and n.id in _SAFE_MATH and not callable(_SAFE_MATH[n.id]):
        return _SAFE_MATH[n.id]
    if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
        l, r = _eval_node(n.left), _eval_node(n.right)
        if isinstance(n.op, ast.Pow) and (abs(r) > 64 or abs(l) > 1e6):
            raise ValueError("เลขยกกำลังใหญ่เกินไป")      # กัน 9**9**9 ทำเซิร์ฟเวอร์ค้าง
        v = _BIN[type(n.op)](l, r)
        if abs(v) > _MAX_ABS:
            raise ValueError("ผลลัพธ์ใหญ่เกินไป")
        return v
    if isinstance(n, ast.UnaryOp) and type(n.op) in _UNARY:
        return _UNARY[type(n.op)](_eval_node(n.operand))
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _SAFE_MATH
            and callable(_SAFE_MATH[n.func.id]) and not n.keywords and len(n.args) <= 4):
        args = [_eval_node(a) for a in n.args]
        if n.func.id == "pow" and len(args) == 2 and (abs(args[1]) > 64 or abs(args[0]) > 1e6):
            raise ValueError("เลขยกกำลังใหญ่เกินไป")
        return _SAFE_MATH[n.func.id](*args)
    raise ValueError("รูปแบบไม่อนุญาต")


def _safe_calc(expression: str) -> dict:
    """คำนวณ expression ปลอดภัย — ประเมินจาก AST ที่อนุญาตเท่านั้น (ไม่มี eval/exec)

    เดิมใช้ eval() กับ whitelist ตัวอักษรที่ยอมรับตัวอักษร . _ ( ) → เดินแอตทริบิวต์
    อย่าง ().__class__.__base__ ออกนอก sandbox ได้ และ 9**9**9 ทำเซิร์ฟเวอร์ค้าง
    """
    expr = str(expression or "").strip()
    if not expr or len(expr) > 200:
        return {"error": "นิพจน์ว่างหรือยาวเกินไป"}
    try:
        tree = ast.parse(expr, mode="eval")
        return {"result": _eval_node(tree), "expression": expr}
    except ZeroDivisionError:
        return {"error": "หารด้วยศูนย์"}
    except Exception as e:
        return {"error": str(e) if isinstance(e, ValueError) else "นิพจน์ไม่ถูกต้อง"}


# ── Tool handlers ─────────────────────────────────────────────────
def _handle_open_url(decision: dict) -> dict:
    url = str(decision.get("url", "")).strip()
    if not url:
        return {"tool": "browser", "status": "error", "reason": "ไม่มี URL"}
    # ตรวจ scheme — อนุญาตแค่ http/https
    if not (url.startswith("http://") or url.startswith("https://")):
        return {"tool": "browser", "status": "blocked",
                "reason": "URL ต้องขึ้นต้นด้วย http:// หรือ https://"}
    # เดิม webbrowser.open() — บนเซิร์ฟเวอร์จะไปเปิดเบราว์เซอร์ของเครื่อง server ไม่ใช่ของผู้ใช้
    # คืน URL ให้หน้าเว็บเปิดเองแทน
    return {"tool": "browser", "status": "ready", "url": url[:2000]}

def _handle_write_note(decision: dict) -> dict:
    content = str(decision.get("content", "")).strip()[:2000]   # จำกัดขนาด กันไฟล์โตไม่หยุด
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
    decision = decision if isinstance(decision, dict) else {"action": str(decision or "")}
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
