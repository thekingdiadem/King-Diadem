"""รอบสุ่ม 103: เด็กหอบเพราะวิ่งเล่นไม่ใช่เรื่องด่วน — แต่หอบไม่หาย ปากเขียว ซี่โครงบุ๋ม ยังด่วน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["ลูกหายใจหอบเพราะวิ่งเล่น", "เด็กหายใจหอบหลังเตะบอล"])
def test_breathless_from_play_is_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["ลูกหายใจหอบหลังวิ่งเล่น พักแล้วไม่หาย ปากเขียว", "ลูกหายใจหอบ ซี่โครงบุ๋ม", "ทารก 2 เดือนตัวร้อน 38.5",
                               "คุณตาเบาหวาน เหงื่อแตก ซึม เรียกไม่ค่อยตอบ", "grandpa is diabetic, sweaty and confused"])
def test_child_and_elder_danger_still_urgent(q):
    assert assess(q)["risk_shown"] >= 80
