"""รอบสุ่ม 140: เลือดกำเดาไหลไม่หยุด (อังกฤษ) ต้องได้เท่าฉบับไทย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["nosebleed won't stop for 30 minutes", "my son's nose bleed keeps going for 40 minutes", "เลือดกำเดาไหลไม่หยุดครึ่งชั่วโมง"])
def test_long_nosebleed_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", ["had a small nosebleed this morning, stopped quickly", "เลือดกำเดาไหลนิดหน่อย หยุดแล้ว"])
def test_short_nosebleed_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
