"""ลำดับความสำคัญทางใจ — "เขาบอกไม่ว่าง" ได้มุมมองอ่อนโยน ไม่ตัดสินแทน และไม่ไปโดนเรื่องงาน"""
import pytest
from core.kernel_voice import compose, assess

HIT = ["เขาบอกว่าไม่ว่างตลอดเลย แต่ลงสตอรี่เที่ยวกับเพื่อน", "ทักไปแล้วเขาไม่ตอบ อ่านไม่ตอบสองวันแล้ว",
       "แฟนนัดแล้วเท", "คนที่คุยด้วยตอบช้ามาก"]
MISS = ["หัวหน้าบอกว่าไม่ว่าง ส่งงานไม่ทัน", "ช่วงนี้ไม่ว่างเลยงานเยอะ"]


@pytest.mark.parametrize("m", HIT)
def test_gets_heart_priority_view_without_verdict(m):
    r = compose(m)
    assert "ใจเป็นคนจัดลำดับก่อน" in r and "ยังบอกอะไรไม่ได้" in r     # ไม่ฟันธงว่าเขาไม่สนใจ
    assert assess(m).get("text_risk", 0) < 50 and not assess(m).get("crisis")


@pytest.mark.parametrize("m", MISS)
def test_work_or_self_busy_not_matched(m):
    assert "ใจเป็นคนจัดลำดับก่อน" not in compose(m)
