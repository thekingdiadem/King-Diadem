"""รอบสุ่ม 142: สัญญาณเตือน CO ดัง · ทุกคนในบ้านปวดหัวพร้อมกัน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "everyone in the house has a headache and the CO alarm is beeping", "the carbon monoxide detector keeps beeping",
    "มีกลิ่นแก๊สในห้อง คนในบ้านปวดหัวทุกคน",
])
def test_co_signs_are_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["how often should I test the CO alarm", "ทุกคนในบ้านปวดหัวเพราะนอนดึกดูบอล"])
def test_maintenance_and_ordinary_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
