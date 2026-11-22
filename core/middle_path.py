"""
core/middle_path.py — ตัวตรวจทางสายกลาง (มัชฌิมาปฏิปทา) ของคำตอบก่อนส่งถึงผู้ใช้

ทางสุดโต่งสองทางที่คำตอบของ AI พลาดได้:
  1. upside-only (กามสุขัลลิกานุโยค) — เชียร์ให้ลงเงิน/ลาออก/กู้ โดยไม่พูดถึงด้านเสียเลย
     → เติม "ถ้าพลาด เสียได้มากสุดเท่าไหร่" (Downside before Upside)
  2. over-constraint (อัตตกิลมถานุโยค) — มีแต่ ห้าม/อย่า/ไม่ควร จนไม่เหลือทางไป
     → เติมทางที่ทำได้จริงอย่างน้อย 1 ทาง (Choice(t) ≥ 1 → collapse = False)

ทุกข้อเป็นกฎคำที่อธิบายย้อนได้ ไม่ใช้ AI ตัดสิน · เรื่องวิกฤตไม่ยุ่ง (ensure_safety_line ดูแลอยู่แล้ว)
"""
from __future__ import annotations

import re
import threading

# ผู้ใช้กำลังจะเอาเงิน/ชีวิตไปเสี่ยง
_COMMIT = re.compile(
    r"ลงทุน|ลงเงิน|ทุ่มเงิน|กู้|เปิดร้าน|เปิดกิจการ|ลาออก|ซื้อ(?:หุ้น|คริปโต|บ้าน|รถ|ทอง)|เทรด|ยิงแอด|ลงแอด|โฆษณา"
    r"|\b(?:invest|loan|borrow|quit my job|open a (?:shop|store|business)|buy (?:stocks?|crypto|a house|a car)|trade|ads?)\b",
    re.I)
# คำตอบเชียร์ให้ทำ
_CHEER = re.compile(
    r"ลุยเลย|ทำเลย|จัดไปเลย|คุ้มแน่|คุ้มมาก|ไม่มีอะไรต้องกลัว|แนะนำให้ลง|ควรลงทุน|โอกาสทอง|รวยแน่|กำไรแน่"
    r"|\b(?:go for it|do it now|definitely worth|can't lose|no[- ]brainer|guaranteed (?:profit|return))\b",
    re.I)
# คำตอบพูดถึงด้านเสียแล้ว
_DOWNSIDE = re.compile(
    r"เสี่ยง|ความเสี่ยง|ขาดทุน|เสียเงิน|เสียได้|แย่สุด|แย่ที่สุด|ถ้าพลาด|ถ้าไม่เป็นไปตาม|เงินสำรอง|เผื่อ"
    r"|\b(?:risk|lose|loss|worst case|downside|if it fails|emergency fund)\b",
    re.I)
# คำห้าม
_NO = re.compile(r"ห้าม|อย่า|ไม่ควร|หยุด|เลิก|\b(?:don'?t|do not|never|stop|avoid|must not|shouldn'?t)\b", re.I)
# มีทางไปต่อแล้ว
_WAY = re.compile(
    r"ลอง|เริ่ม(?:จาก|ที่)|ขั้นแรก|ขั้นตอน|ทางเลือก|โทร|ติดต่อ|ทำได้คือ|สิ่งที่ทำได้|^\s*\d+[.)]"
    r"|\b(?:try|start (?:by|with)|first step|you can|option|call|contact)\b",
    re.I | re.M)

_LINES = {
    "upside": {
        "th": "ก่อนตัดสินใจ ลองตอบตัวเองข้อเดียว: ถ้าไม่เป็นไปตามที่หวัง เสียได้มากสุดเท่าไหร่ และยังอยู่ไหวไหม",
        "en": "Before you decide, answer one question: if it doesn't go as hoped, what's the most you could lose, and could you live with that?",
    },
    "constraint": {
        "th": "ทางที่ยังทำได้ตอนนี้: เลือกสิ่งเล็กที่สุดหนึ่งอย่างที่ทำได้วันนี้ แล้วค่อยดูทีละก้าว",
        "en": "One thing you can still do now: pick the smallest step you can take today, then go one step at a time.",
    },
}

_lock = threading.Lock()
_STATS = {"checked": 0, "upside": 0, "constraint": 0}


def stats() -> dict:
    with _lock:
        return dict(_STATS)


def _lang(text: str) -> str:
    return "th" if re.search(r"[฀-๿]", text or "") else "en"


def classify(text: str, reply: str) -> str | None:
    """'upside' · 'constraint' · None (สมดุลแล้ว)"""
    if _COMMIT.search(text or "") and _CHEER.search(reply) and not _DOWNSIDE.search(reply):
        return "upside"
    if len(_NO.findall(reply)) >= 3 and not _WAY.search(reply):
        return "constraint"
    return None


def balance(text: str, reply: str, a: dict | None = None) -> str:
    """คืนคำตอบที่เติมด้านที่ขาดแล้ว (หรือคำตอบเดิมถ้าสมดุลอยู่แล้ว)"""
    if not isinstance(reply, str) or not reply.strip():
        return reply
    a = a if isinstance(a, dict) else {}
    with _lock:
        _STATS["checked"] += 1
    if a.get("crisis"):
        return reply
    kind = classify(text or "", reply)
    if not kind:
        return reply
    with _lock:
        _STATS[kind] += 1
    line = _LINES[kind][_lang(text or reply)]
    m = re.search(r"\n+(—\s*(?:LYLA|VEGA)[^\n]*)\s*$", reply)       # ใส่ก่อนลายเซ็น
    if m:
        return reply[:m.start()].rstrip() + "\n\n" + line + "\n\n" + m.group(1)
    return reply.rstrip() + "\n\n" + line
