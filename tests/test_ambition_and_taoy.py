"""ความทะเยอทะยาน · และคำว่า "แต่อยาก" / "ต่อยอด" ที่เคยถูกอ่านเป็น "ต่อย" (ความรุนแรง)"""
import pytest
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("q", ["ชอบเขาแต่อยากรอให้พร้อมก่อน", "แฟนแต่อยู่กันคนละที่", "งานดีแต่อยากต่อยอด",
                               "งานดีอยู่แล้วแต่อยากต่อยอดธุรกิจ", "เหนื่อยนะแต่อยากสู้ต่อ"])
def test_tae_yak_is_not_violence(q):
    a = assess(q)
    assert "violence" not in a["topics"] and "first_aid" not in a["topics"] and a["risk"] < 75


@pytest.mark.parametrize("q", ["เขาต่อยฉัน", "สามีต่อยหน้าหนู", "โดนเพื่อนต่อย", "แฟนต่อยหน้า"])
def test_real_punch_still_violence(q):
    assert "violence" in assess(q)["topics"]


def test_wasp_sting_still_first_aid():
    assert "first_aid" in assess("โดนตัวต่อต่อยที่แขน บวมมาก")["topics"]


def test_ambition_gets_direction_not_flattery():
    a = compose("ฉันมีความทะเยอทะยานสูง อยากเป็นที่หนึ่ง", footer=False)
    assert "ทิศทาง" in a and "วัดได้" in a
    assert "Ambition is a good force" in compose("I want to be successful and build something big", footer=False)


def test_ambition_on_shaky_base_stabilizes_first():
    a = compose("เงินจะหมดแล้วแต่อยากเปิดบริษัทใหญ่", footer=False)
    assert "ฐานยังไม่มั่น" in a


def test_get_rich_scam_still_scam():
    assert "ความทะเยอทะยาน" not in compose("อยากรวยเร็ว มีคนชวนลงทุนแล้วได้ 10% ต่อวัน", footer=False)
