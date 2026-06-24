# ENGINE/strategy_planner.py
"""
KING DIADEM — Strategy Planner
FATE™ Axiom E3: Stabilize before Optimize
DriftZero: ห้ามขยายระบบขณะ waterline ยังไม่นิ่ง
"""
from __future__ import annotations
from typing import Optional
import time


# ── Strategy tiers ────────────────────────────────────────────────
def plan(
    pattern:  dict,
    context:  Optional[dict] = None,
) -> dict:
    ctx       = context or {}
    entropy   = float(pattern.get("entropy",   40))
    resource  = float(pattern.get("resource",  50))
    stability = float(pattern.get("stability", 60))
    choices   = int(pattern.get("choices",      1))
    user_input= str(pattern.get("input",       ""))

    # ── COLLAPSE — choices = 0 ────────────────────────────────────
    if choices <= 0:
        return _make_plan(
            strategy  = "COLLAPSE_PREVENTION",
            priority  = "IMMEDIATE",
            stop_line = True,
            actions   = [
                {"step": 1, "action": "HALT ทุกอย่าง — Choice(t) = 0",
                 "reason": "ระบบต้องมีทางเลือกอย่างน้อย 1 ทางก่อนจะทำอะไรได้"},
                {"step": 2, "action": "ระบุทรัพยากรที่เหลืออยู่จริง",
                 "reason": "ต้องรู้ baseline ก่อนวางแผน"},
                {"step": 3, "action": "หา 1 ทางเลือกที่ยังเปิดอยู่ — ไม่ต้องดีที่สุด",
                 "reason": "restore choice ก่อน — นั่นคือ mission เดียวตอนนี้"},
            ],
            entropy=entropy, resource=resource, stability=stability,
            axiom="Choice(t) ≥ 1 → collapse = False",
        )

    # ── CRITICAL — entropy สูงมาก หรือ resource หมด ──────────────
    if entropy > 75 or resource < 20:
        return _make_plan(
            strategy  = "STABILIZE",
            priority  = "HIGH",
            stop_line = True,
            actions   = [
                {"step": 1, "action": "หยุดการขยายตัวทั้งหมด",
                 "reason": "entropy > 75 — ทุก action ใหม่เพิ่มความเสี่ยง"},
                {"step": 2, "action": "รักษาทรัพยากรที่มี — ห้ามใช้จ่ายที่ไม่จำเป็น",
                 "reason": "resource < 20 — survival threshold ต่ำกว่า 72h"},
                {"step": 3, "action": "ลด exposure ทันที — ออกจากสถานการณ์เสี่ยง",
                 "reason": "Axiom 4: Downside before Upside"},
                {"step": 4, "action": "ติดต่อคนที่ไว้ใจได้ 1 คน",
                 "reason": "อย่าแก้คนเดียวตอน entropy สูง"},
            ],
            entropy=entropy, resource=resource, stability=stability,
        )

    # ── RESTORE — stability ต่ำ ───────────────────────────────────
    if stability < 35:
        return _make_plan(
            strategy  = "RESTORE",
            priority  = "MEDIUM",
            stop_line = False,
            actions   = [
                {"step": 1, "action": "ประเมินจุดที่พังและสาเหตุจริง",
                 "reason": "stability < 35 — มีอะไรบางอย่างไหลออกอยู่"},
                {"step": 2, "action": "หาแหล่งสนับสนุนหรือ resource ใหม่",
                 "reason": "เติม resource ก่อน จะ optimize ทีหลัง"},
                {"step": 3, "action": "สร้าง fallback path ไว้ก่อน",
                 "reason": "DriftZero: ต้องมีเส้นทางถอยก่อนเดินหน้า"},
            ],
            entropy=entropy, resource=resource, stability=stability,
        )

    # ── OPTIMIZE — ระบบนิ่ง ──────────────────────────────────────
    if entropy <= 40 and resource >= 60 and stability >= 60:
        return _make_plan(
            strategy  = "OPTIMIZE",
            priority  = "LOW",
            stop_line = False,
            actions   = [
                {"step": 1, "action": "เดินหน้าอย่างระมัดระวัง — ไม่ over-extend",
                 "reason": "stable ไม่ได้แปลว่าปลอดภัย — แปลว่ายังมีเวลา"},
                {"step": 2, "action": "ติดตาม drift รายวัน — ตรวจ waterline",
                 "reason": "DriftZero: 0.1% drift prevention"},
                {"step": 3, "action": "รักษา waterline ให้อยู่เหนือ threshold",
                 "reason": "Fail less — ไม่ใช่ Win more"},
            ],
            entropy=entropy, resource=resource, stability=stability,
        )

    # ── DEFAULT — moderate ────────────────────────────────────────
    return _make_plan(
        strategy  = "MONITOR",
        priority  = "LOW",
        stop_line = False,
        actions   = [
            {"step": 1, "action": "Monitor waterline ทุกวัน",
             "reason": "สถานการณ์กลาง — ยังไม่ต้อง intervene แต่ต้องเฝ้าดู"},
            {"step": 2, "action": "ระบุ 1 จุดเสี่ยงที่สุดและวาง contingency",
             "reason": "DriftZero: prevent drift ก่อนถึง unstable"},
        ],
        entropy=entropy, resource=resource, stability=stability,
    )


def _make_plan(
    strategy:  str,
    priority:  str,
    stop_line: bool,
    actions:   list,
    entropy:   float,
    resource:  float,
    stability: float,
    axiom:     str = "Fail less. Harm less. Restore more.",
) -> dict:
    risk_score = round(max(0, min(100,
        entropy * 0.40 + (100 - resource) * 0.35 + (100 - stability) * 0.25
    )), 1)
    return {
        "strategy":   strategy,
        "priority":   priority,
        "stop_line":  stop_line,
        "actions":    actions,
        "risk_score": risk_score,
        "entropy":    entropy,
        "resource":   resource,
        "stability":  stability,
        "axiom":      axiom,
        "timestamp":  time.time(),
    }
