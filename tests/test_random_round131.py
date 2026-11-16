"""รอบสุ่ม 131: คนใกล้ตัวขอโทษทุกคนแล้วติดต่อไม่ได้"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "เพื่อนส่งข้อความว่าขอโทษทุกคน แล้วปิดเครื่อง", "my friend texted sorry for everything and turned off his phone",
    "แฟนพิมพ์มาว่าขอโทษสำหรับทุกอย่าง ตอนนี้โทรไม่ติด",
])
def test_farewell_apology_then_silence_is_urgent(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "someone" in a["topics"]


@pytest.mark.parametrize("q", ["เพื่อนส่งข้อความขอโทษที่มาสาย", "my friend said sorry for everything after our fight and we made up"])
def test_ordinary_apology_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
