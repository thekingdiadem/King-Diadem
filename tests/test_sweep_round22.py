"""รอบหาบั๊ก 22: เด็กกินของใช้ทั่วไป → 1367 ก่อน · ไข้หลังโดนสัตว์กัด · ไม่ได้นอนหลายวัน"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("t", ["น้องกินแชมพูเข้าไป", "ลูกกลืนซองกันชื้น"])
def test_mild_household_goes_to_poison_center_first(t):
    a = assess(t)
    assert "household" in a["topics"] and "overdose" not in a["topics"]
    out = compose(t)
    assert out.index("1367") < out.index("1669")


@pytest.mark.parametrize("t", ["ลูกกินน้ำมันก๊าดเข้าไป", "หลานดื่มเจลล้างมือ"])
def test_dangerous_household_is_still_an_emergency(t):
    assert "overdose" in assess(t)["topics"]


def test_fever_after_rat_bite():
    t = "คนในบ้านมีไข้สูงหนาวสั่นหลังโดนหนูกัด"
    assert "first_aid" in assess(t)["topics"]
    assert "ไข้หนูกัด" in compose(t)
    assert "ไข้หนูกัด" not in compose("โดนน้ำร้อนลวกแล้วมีไข้")


def test_nail_biting_is_not_a_bite():
    assert "first_aid" not in assess("หนูกัดเล็บจนเลือดออก")["topics"]


@pytest.mark.parametrize("t", ["ฉันไม่ได้นอนมาสามวันแล้ว รู้สึกแปลกๆ", "ไม่ได้นอนมา 2 คืน เพราะอ่านหนังสือสอบ"])
def test_sleepless_nights(t):
    assert "sleepless" in assess(t)["topics"]


@pytest.mark.parametrize("t", ["เคยไม่ได้นอนสามวันตอนปีที่แล้ว", "นอนไม่หลับ"])
def test_not_sleepless_topic(t):
    assert "sleepless" not in assess(t)["topics"]
