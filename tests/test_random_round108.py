"""รอบสุ่ม 108: งูกัดแล้วบวม/ชา ฉบับไทยต้องได้เท่าฉบับอังกฤษ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["โดนงูกัดที่ขา ตอนนี้บวมมาก", "งูกัดมือ ชาไปทั้งแขน", "ลูกโดนงูกัด ตาพร่า หนังตาตก",
                               "snake bit my leg in the garden, swelling fast"])
def test_snakebite_with_symptoms_is_urgent(q):
    # ฉบับไทยเคยได้ 75 ขณะที่ฉบับอังกฤษได้ 85
    assert assess(q)["risk_shown"] >= 80


def test_plain_mosquito_is_calm():
    assert assess("โดนยุงกัดคันมาก")["risk_shown"] < 60
