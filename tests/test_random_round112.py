"""รอบสุ่ม 112: "disappear into …" — หนังสือดีๆ ไม่ใช่สัญญาณ แต่ทะเลคืนนี้คือวิกฤต"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["i want to disappear into a good book this weekend", "i want to disappear into my garden all day"])
def test_hobby_is_calm(q):
    # "disappear into a good book" เคยถูกเตือน 65
    a = assess(q)
    assert a["risk_shown"] < 60 and not a["crisis"]


@pytest.mark.parametrize("q", ["i want to disappear into the sea tonight", "i just want to disappear into the ocean"])
def test_sea_is_crisis(q):
    # เคยได้แค่ 65 (เตือน) ไม่ใช่วิกฤต
    assert assess(q)["crisis"]
