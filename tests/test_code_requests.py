"""ขอให้เขียน/แก้โค้ด — เดิมตอนไม่มี AI ได้ "เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว · แยกสิ่งที่ควบคุมได้…" ซึ่งไม่ตอบอะไร
ตอนนี้บอกตรงๆ ว่าไม่ใช่งานถนัด แล้วชวนกลับมาที่การตัดสินใจรอบงานนั้น · คำถามเชิงตัดสินใจเรื่องสายโค้ดยังได้คำตอบเดิม"""
import pytest

from core.kernel_voice import compose, compose_council

TH = "ไม่ใช่ผู้เชี่ยวชาญ"


@pytest.mark.parametrize("text", [
    "ช่วยเขียนโค้ด python หาเลขคู่ในลิสต์หน่อย", "python error KeyError แก้ไง", "ขอโค้ด sql ดึงยอดขายรายเดือน",
    "def f(x):\n    return x[0]\nทำไม error", "แก้บั๊กไม่ออกเลย",
])
def test_code_requests_get_an_honest_answer(text):
    assert TH in compose(text) and TH in compose_council(text)


def test_english_code_request():
    assert "isn't what KING DIADEM is built for" in compose("write a python function to sort a list")


@pytest.mark.parametrize("text", ["ควรเรียนเขียนโค้ดไหม หรือเรียนบัญชีดี", "จะลาออกไปเป็นโปรแกรมเมอร์ดีไหม",
                                  "รับงานเขียนเว็บราคาเท่าไหร่ดี", "อยากตาย เขียนโค้ดไม่ได้เลย"])
def test_decisions_about_coding_and_crises_are_not_deflected(text):
    assert TH not in compose(text)
