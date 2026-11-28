"""กตญาณ — รอบที่สามของญาณในอริยสัจ: รู้ว่าสิ่งที่ควรทำ ได้ทำแล้ว

ธัมมจักกัปปวัตตนสูตร: สัจจญาณ (รู้ว่าเป็นอะไร) → กิจจญาณ (รู้ว่าต้องทำอะไร) → กตญาณ (รู้ว่าทำแล้ว)
core/reflect.py ทำสองรอบแรก — แยกให้เห็นว่าอะไรเกิดแล้ว อะไรเป็นแค่ความกลัว แล้วชวนทำหนึ่งอย่างที่ทำได้วันนี้
ที่นี่คือรอบที่สาม: กลับมาถามว่าก้าวนั้นเป็นอย่างไร (เจ้าของโปรเจกต์อนุมัติกรอบนี้แล้ว)

กรอบที่ตกลงกัน:
  · เก็บแค่ "เรื่องที่เกิดขึ้นแล้ว" ท่อนเดียวกับวันที่ — ไม่เก็บเรื่องราวทั้งหมด
  · ถามครั้งเดียว ในวันถัดไปขึ้นไป เฉพาะตอนผู้ใช้แค่ทักทาย (ไม่แทรกเรื่องใหม่ที่เขากำลังจะเล่า)
  · ไม่ทวนเรื่องเดิม · บอกว่าไม่ต้องตอบก็ได้ · ไม่ถามซ้ำ
  · เฉพาะคนที่เปิดความจำ · ไม่ทำกับเรื่องเปราะบาง (ทำร้ายตัวเอง ถูกทำร้าย วิกฤต) เลย
  · เขาบอกว่าทำแล้ว → รับรู้ว่าก้าวนั้นเสร็จแล้วจริงๆ แล้วลืมเรื่องนั้น
"""
from __future__ import annotations

import re
from datetime import date

KEY_STEP = "next_step"            # "YYYY-MM-DD|ท่อนที่เกิดขึ้นแล้ว"
KEY_ASKED = "next_step_asked"     # "YYYY-MM-DD" วันที่ถามไปแล้ว

_DONE = re.compile(r"ทำแล้ว|ได้ทำ|ลองแล้ว|ลองทำแล้ว|เรียบร้อย|เสร็จแล้ว|โอเคขึ้น|ดีขึ้นแล้ว|"
                   r"\b(?:did\s+it|done|i\s+tried|i\s+did|went\s+(?:well|ok)|better\s+now)\b", re.I)
_TH = re.compile(r"[฀-๿]")


def _today() -> str:
    return date.today().isoformat()


def remember(user_email: str, user_input: str, save, sensitive: bool = False) -> bool:
    """หลังตอบ: ถ้าข้อความนี้ได้บล็อกแยกกอง และไม่ใช่เรื่องเปราะบาง → จำท่อน "เกิดขึ้นแล้ว" ไว้ถามวันหลัง"""
    if sensitive:
        return False
    from core.reflect import split_truth, applies
    piles = split_truth(user_input)
    if not applies(user_input, piles) or not piles["fact"]:
        return False
    save(user_email, KEY_STEP, f"{_today()}|{piles['fact'][0]}", "general", importance=3)
    save(user_email, KEY_ASKED, "", "general", importance=1)          # เรื่องใหม่ = ยังไม่ได้ถาม
    return True


def _parse(step: str | None):
    if not step or "|" not in step:
        return None, None
    d, fact = step.split("|", 1)
    return d, fact


def checkin(user_email: str, user_input: str, get, save, enabled: bool, is_greeting: bool) -> str | None:
    """ตอนผู้ใช้ทักทายในวันถัดไป: ถามหนึ่งครั้งว่าก้าวที่ตั้งใจไว้เป็นอย่างไร — ไม่เข้าเงื่อนไขคืน None"""
    if not (enabled and is_greeting):
        return None
    d, fact = _parse(get(user_email, KEY_STEP))
    if not d or d >= _today() or (get(user_email, KEY_ASKED) or ""):
        return None
    save(user_email, KEY_ASKED, _today(), "general", importance=1)
    if _TH.search(user_input or ""):
        return ("ครั้งก่อนเราแยกเรื่องที่หนักใจออกมาดูด้วยกัน แล้วชวนลองทำสิ่งเล็กๆ หนึ่งอย่าง — "
                "ตอนนี้เป็นยังไงบ้าง ได้ลองไหม ไม่ต้องเล่าก็ได้นะ")
    return ("Last time we sorted out what was weighing on you and picked one small thing to try — "
            "how did it go? You don't have to say.")


def acknowledge(user_email: str, user_input: str, get, save) -> str | None:
    """วันเดียวกับที่ถามไป ผู้ใช้บอกว่าทำแล้ว → รับรู้ว่าก้าวนั้นเสร็จแล้ว (กตญาณ) แล้วลืมเรื่องนั้น"""
    if (get(user_email, KEY_ASKED) or "") != _today() or not _DONE.search(user_input or ""):
        return None
    if not _parse(get(user_email, KEY_STEP))[0]:
        return None
    save(user_email, KEY_STEP, "", "general", importance=1)
    save(user_email, KEY_ASKED, "", "general", importance=1)
    if _TH.search(user_input or ""):
        return "ก้าวนั้นทำเสร็จแล้วจริงๆ — ไม่ใช่แค่คิดไว้ เห็นไหมว่ามันทำได้"
    return "That step is actually done — not just planned. You did it."
