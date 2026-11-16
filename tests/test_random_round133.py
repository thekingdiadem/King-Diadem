"""รอบสุ่ม 133: นายจ้างไม่ให้ออก + ยึดโทรศัพท์/พาสปอร์ต (อังกฤษ) ต้องได้เท่าฉบับไทย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "my employer won't let me leave and took my phone", "my boss took my passport and won't let me go home",
    "นายจ้างไม่ให้กลับบ้าน ยึดโทรศัพท์",
])
def test_held_by_employer_is_urgent(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "trafficking" in a["topics"]


@pytest.mark.parametrize("q", ["my boss won't let me leave early today, so annoying", "my employer keeps my id card in the office safe for the security system"])
def test_ordinary_work_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
