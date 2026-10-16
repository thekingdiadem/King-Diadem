"""สำนวนความคิดอยากตายภาษาไทยที่ไม่มีคำว่า "อยากตาย" — ตาราง 5,250 ข้อความเคยหลุด 2,114"""
import pytest

from core.kernel_voice import assess


@pytest.mark.parametrize("text", ["ถ้าตายไปทุกคนคงสบาย", "ไม่มีใครต้องการ ตายไปคงดีกว่า", "มีชีวิตอยู่ไปทำไม", "เบื่อการมีชีวิต",
                                  "อยากไปให้พ้นๆ จากโลกนี้", "คืนนี้คงเป็นคืนสุดท้าย", "กูอยากแขวนคอ..."])
def test_crisis_idioms(text):
    assert assess(text)["crisis"]


@pytest.mark.parametrize("text", ["ไม่เห็นทางออกแล้ว", "ซื้อยามาเก็บไว้แล้ว", "อยากปล่อยตัวเองไป", "ไม่อยากตื่นมาเจอพรุ่งนี้", "มีชีวิตอยู่เพื่ออะไร"])
def test_ambiguous_idioms_are_a_warning(text):
    assert assess(text)["text_risk"] >= 65


@pytest.mark.parametrize("text", ["อยากไปให้พ้นๆ จากที่ทำงาน", "ไม่เห็นทางออกของโจทย์ข้อนี้", "ซื้อยามาเก็บไว้แล้วเผื่อป่วย",
                                  "คืนนี้คงเป็นคืนสุดท้ายที่นี่แล้ว", "อยากปล่อยตัวเองไปเที่ยวทะเล"])
def test_everyday_versions_stay_calm(text):
    a = assess(text)
    assert not a["crisis"] and a["text_risk"] < 60
