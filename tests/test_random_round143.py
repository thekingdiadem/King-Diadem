"""รอบสุ่ม 143: ตกน้ำแข็ง (อังกฤษ) ต้องได้เท่าฉบับไทย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["fell through the ice on the lake", "my friend fell through the ice", "ตกน้ำแข็งที่ทะเลสาบ"])
def test_ice_fall_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


def test_ice_skating_stays_calm():
    assert assess("we went ice skating on the lake, so fun")["risk_shown"] < 60
