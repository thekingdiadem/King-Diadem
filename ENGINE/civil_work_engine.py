# ENGINE/civil_work_engine.py
"""
CIVIL WORK ENGINE
Connects CIVIL_WORK_CORE to the decision routing layer.
"""

from __future__ import annotations

try:
    from core.civil_work_core import evaluate_work_plan
    _CORE_LOADED = True
except ImportError:
    _CORE_LOADED = False

def assess(pattern: dict) -> dict:
    pattern = pattern if isinstance(pattern, dict) else {"input": str(pattern or "")}
    user_input = pattern.get("input") or pattern.get("description") or ""
    tasks = pattern.get("tasks")

    if not tasks:
        tasks = [{"description": user_input}]
    if isinstance(tasks, str):
        tasks = [{"description": tasks}]

    if not _CORE_LOADED:
        # Fallback — ไม่ crash แต่บอกว่า core ยังไม่พร้อม
        return {
            "status":  "CORE_NOT_LOADED",
            "tasks":   tasks,
            "note":    "civil_work_core ยังไม่ได้ implement — assess() รับ input ได้แต่ evaluate ไม่ได้",
            "choice":  1,
        }

    return evaluate_work_plan(tasks)
