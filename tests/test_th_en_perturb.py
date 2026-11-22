"""เรื่องด่วนไทย/อังกฤษ — บิดแบบที่คนตกใจพิมพ์จริง (ยืดตัวท้าย · !!! · ค่ะ/pls · อีโมจิ · ตัวใหญ่ · สะกดย่อ)

เทสต์นี้เจอ 2 ประโยคพื้นฐานที่ได้ Risk 0 แม้พิมพ์ปกติ: "มีคนจะเข้ามาทำร้าย" · "someone is breaking in"
ไม่ได้บิดแบบ "ไม่เว้นวรรคเลย" ในภาษาอังกฤษ (iwanttodie) และ "เว้นทุกตัวอักษร" ในภาษาไทย — คนตกใจแทบไม่พิมพ์แบบนั้น
"""
import re

import pytest

from core.kernel_voice import assess

TH = ["แม่หายใจไม่ออก", "ลูกกินยาพาราไปทั้งแผง", "อยากตาย", "ไม่อยากอยู่แล้ว", "แฟนตบหน้าเลือดออก",
      "พ่อเจ็บหน้าอกเหงื่อแตก", "ไฟไหม้บ้านออกไม่ได้", "ลูกจมน้ำ", "มีคนจะเข้ามาทำร้าย", "กินยาฆ่าหญ้าไป"]
EN = ["my mom can't breathe", "i want to die", "he is hitting me", "my baby swallowed a battery",
      "chest pain and sweating", "house on fire im trapped", "i took all my pills", "someone is breaking in"]
THAI = re.compile(r"[ก-๙]")

TWISTS = {
    "ยืดตัวท้าย": lambda t: t + t[-1] * 4,
    "!!!": lambda t: t + "!!!",
    "ขึ้นต้นขอความช่วยเหลือ": lambda t: ("ช่วยด้วย " if THAI.search(t) else "help ") + t,
    "ลงท้ายสุภาพ": lambda t: t + ("ค่ะ" if THAI.search(t) else " pls"),
    "อีโมจิ": lambda t: t + " 😭",
    "ตัวใหญ่": str.upper,
    "สะกดย่อ": lambda t: t.replace("can't", "cant").replace("breathe", "breath").replace("i want", "i wanna"),
}


@pytest.mark.parametrize("twist", TWISTS)
@pytest.mark.parametrize("t", TH + EN)
def test_urgent_th_en_survives_twists(t, twist):
    u = TWISTS[twist](t)
    a = assess(u)
    assert a["text_risk"] >= 75 or a["crisis"], (twist, u, a["text_risk"])


def test_intruder_now_vs_story():
    for t in ("มีคนจะเข้ามาทำร้าย", "someone is breaking in", "ดูข่าวอยู่ แล้วมีคนบุกเข้าบ้านฉันตอนนี้"):
        assert assess(t)["text_risk"] >= 85, t
    for t in ("ดูหนังที่มีคนบุกเข้ามาในบ้าน", "ข่าวโจรบุกเข้ามาปล้นร้านทอง",
              "they are breaking in new shoes", "someone broke in to the conversation"):
        assert assess(t)["text_risk"] < 60, t
