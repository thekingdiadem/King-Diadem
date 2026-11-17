"""รอบสุ่ม 144: เด็กเอาของเข้าปากแต่ไม่ได้กลืน/คายแล้ว และไม่มีอาการ ไม่ใช่เหตุฉุกเฉิน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ลูกกินแม่เหล็กติดตู้เย็นเล่นๆ ไม่ได้กลืน", "ลูกเอาถ่านเข้าปากแต่ไม่ได้กลืน คายแล้ว",
    "my kid put a battery in his mouth but spat it out",
])
def test_spat_out_without_symptoms_is_calm(q):
    a = assess(q)
    assert a["risk_shown"] < 60 and "swallowed" not in a["topics"]


@pytest.mark.parametrize("q", [
    "ลูกเอาถ่านเข้าปาก ไม่แน่ใจว่ากลืนไปหรือเปล่า", "ลูกกินแม่เหล็กไม่ได้กลืน แต่ตอนนี้ไอไม่หยุด",
    "ลูกกินแม่เหล็กเข้าไปสองเม็ด", "my toddler swallowed two magnets",
])
def test_doubt_or_symptoms_stay_urgent(q):
    assert assess(q)["risk_shown"] >= 80
