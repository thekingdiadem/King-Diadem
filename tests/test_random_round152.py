"""รอบสุ่ม 152: แก๊งหลานโดนจับ ให้โอน/ซื้อบัตรของขวัญจ่ายค่าประกันตัว (อังกฤษ) ต้องได้เท่าฉบับไทย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "grandma got a call saying I was arrested and needs bail money in gift cards",
    "someone called my mom pretending to be me, said I was in jail and needs money",
    "a man said my grandson had an accident and we must wire money right away",
])
def test_grandparent_scam_is_flagged(q):
    a = assess(q)
    assert a["risk_shown"] >= 70 and "scam" in a["topics"]


@pytest.mark.parametrize("q", [
    "my brother was arrested last year and we paid the bail through a lawyer", "I bought gift cards for my nieces for Christmas",
])
def test_ordinary_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
