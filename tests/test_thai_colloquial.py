"""ภาษาพูดที่เคยหลุด (Risk 0): ไม่อยากตื่นมาอีกแล้ว · ไม่เห็นประโยชน์ที่จะอยู่ต่อ · เป็นลมปลุกไม่ตื่น · จะเป็นลมใจสั่น"""
import pytest

from core.kernel_voice import assess

CRISIS = ["เหนื่อยกับชีวิต ไม่อยากตื่นมาอีกแล้ว", "ไม่เห็นประโยชน์ที่จะอยู่ต่อ", "ไม่เห็นความหมายของการมีชีวิตอยู่"]
BODY = ["พ่อเป็นลมล้มฟุบ ปลุกไม่ตื่น", "รู้สึกจะเป็นลม ใจสั่นมาก มือเท้าเย็น", "ยายเป็นลมหมดสติ", "แม่ล้มลง เรียกไม่ตอบ"]
CALM = ["ปลุกลูกไม่ตื่นไปโรงเรียน", "ไม่เห็นประโยชน์ที่จะอยู่ต่อในบริษัทนี้", "วันจันทร์ไม่อยากตื่นมาทำงานเลย", "หน้ามืดตอนลุกเร็วๆ"]


@pytest.mark.parametrize("t", CRISIS)
def test_colloquial_crisis(t):
    assert assess(t)["crisis"], t


@pytest.mark.parametrize("t", BODY)
def test_colloquial_body_emergency(t):
    assert assess(t)["text_risk"] >= 50, t


@pytest.mark.parametrize("t", CALM)
def test_everyday_lookalikes_stay_calm(t):
    a = assess(t)
    assert not a["crisis"] and a["text_risk"] < 50, t
