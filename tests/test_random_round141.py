"""รอบสุ่ม 141: แน่นหน้าอกของคนในบ้าน (อังกฤษ) แม้เจ้าตัวบอกว่าแค่ลมในท้อง"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["dad has chest pressure but says it's just gas", "my husband feels chest tightness and won't go to the doctor", "พ่อเจ็บหน้าอก แต่บอกว่าแค่ลมในท้อง"])
def test_chest_pressure_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["dad has chest pressure exercises in his gym plan", "my chest feels tight after crying, I'm okay now"])
def test_everyday_stays_below_emergency(q):
    assert assess(q)["risk_shown"] < 80
