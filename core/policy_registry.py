"""ทะเบียนการเปลี่ยนค่าที่กระทบผู้ใช้ — FATE™ หลักการ 4 "การยกเว้นต้องมีหลักฐาน"

ค่าอย่างโควตาฟรีต่อวัน ราคาต่อข้อความ ราคาต่อภาพ ตั้งผ่าน environment ของเซิร์ฟเวอร์ (เช่น Render)
แอปจึงห้ามคนแก้ไม่ได้ — แต่ทำให้ "ทุกการเปลี่ยนมองเห็นได้เสมอ" ได้:
  · ทุกครั้งที่เซิร์ฟเวอร์เปิด เทียบค่าปัจจุบันกับค่าล่าสุดในทะเบียน
  · เปลี่ยน = บันทึก ค่าเดิม → ค่าใหม่ + เหตุผล (POLICY_CHANGE_REASON) + เวลา
  · ไม่ใส่เหตุผลก็ยังบันทึก แต่ติดธง no_reason — ผู้ดูแลเห็นใน /api/admin/metrics
  · ผู้ใช้ทุกคนดูได้ที่ /api/policy — ราคา/โควตาเปลี่ยนเมื่อไหร่ เพราะอะไร

ฟังก์ชันในไฟล์นี้ไม่แตะฐานข้อมูล (ผู้เรียกส่งค่าล่าสุดเข้ามา) — ค่าเดิมได้ผลเดิมเสมอ เทสต์ได้ตรงๆ
"""
from __future__ import annotations

import hashlib

# key → (ชื่อไทย, ชื่ออังกฤษ, เปิดเผยค่าได้ไหม) · ค่าที่ไม่ใช่ตัวเลขสำหรับผู้ใช้ (price id) แสดงแค่ว่า "เปลี่ยน"
WATCHED = {
    "FREE_DAILY_RUNS":         ("ข้อความฟรีต่อวัน", "Free messages per day", True),
    "RUN_COST":                ("เครดิตต่อข้อความ", "Credits per message", True),
    "IMAGE_COST":              ("เครดิตต่อภาพ", "Credits per image", True),
    "IMAGE_FREE_DAILY":        ("ภาพฟรีต่อวัน", "Free images per day", True),
    "IMAGE_PREMIUM_DAILY":     ("ภาพต่อวันของ Premium", "Premium images per day", True),
    "STRIPE_PRICE_ID":         ("ราคาแพ็กเกจเครดิต", "Credit pack price", False),
    "STRIPE_PREMIUM_PRICE_ID": ("ราคา Premium", "Premium price", False),
}

NO_REASON = "ไม่ได้ระบุเหตุผล"
MAX_REASON = 300


def _norm(v) -> str:
    return "" if v is None else str(v).strip()


def diff(current: dict, last: dict) -> list[tuple[str, str, str]]:
    """[(key, เดิม, ใหม่)] เฉพาะค่าที่เปลี่ยน · ครั้งแรก (ยังไม่มีในทะเบียน) นับเป็นค่าตั้งต้น เดิม = "" """
    out = []
    for key in WATCHED:
        new, old = _norm(current.get(key)), last.get(key)
        if old is None or _norm(old) != new:
            out.append((key, "" if old is None else _norm(old), new))
    return out


def clean_reason(reason) -> str:
    r = " ".join(_norm(reason).split())[:MAX_REASON]
    return r or NO_REASON


def _shown(key: str, value: str) -> str:
    """ค่าที่ผู้ใช้เห็น — price id ไม่เปิดเผย แสดงเป็นรหัสสั้นที่บอกได้ว่าเปลี่ยนหรือไม่"""
    if WATCHED[key][2] or not value:
        return value
    return "#" + hashlib.sha256(value.encode()).hexdigest()[:6]


def public_row(row: dict) -> dict:
    """แถวในทะเบียน → รูปที่เปิดให้ทุกคนดู (ไม่มีข้อมูลผู้ใช้ ไม่มี price id จริง)"""
    key = row["key"]
    th, en, _ = WATCHED.get(key, (key, key, False))
    reason = row.get("reason") or NO_REASON
    return {"at": row["ts"], "key": key, "label": {"th": th, "en": en},
            "old": _shown(key, row.get("old") or ""), "new": _shown(key, row.get("new") or ""),
            "reason": reason, "no_reason": reason == NO_REASON, "initial": not row.get("old")}
