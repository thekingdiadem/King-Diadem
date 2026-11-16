"""รอบสุ่ม 125: มีคนกำลังบุกเข้าบ้าน (อังกฤษ ไม่มีคำว่า my)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "someone is trying to break in right now", "a man is trying to get in through the back door, i'm hiding",
    "someone's breaking in downstairs",
])
def test_break_in_now_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["how do i break in new shoes", "the sun is breaking in through the window", "can someone help me get in to the zoom call"])
def test_idioms_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
