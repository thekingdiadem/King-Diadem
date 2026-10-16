"""ความรุนแรงภาษาไทย ใครเป็นคนทำก็ตาม — ตาราง 10,080 ข้อความเคยหลุด 3,192"""
import pytest

from core.kernel_voice import assess


@pytest.mark.parametrize("text", ["เจ้านายต่อยหนู", "คนแปลกหน้า ตบหนู", "สามีไม่ให้หนูกินข้าว", "พ่อเอาบุหรี่จี้หนู",
                                  "ลุงขังหนูไว้ในห้อง", "แฟนเก่าตามหนูกลับบ้านทุกคืน", "พ่อเลี้ยงไม่ให้หนูออกจากบ้าน", "แฟนยึดพาสปอร์ตหนู"])
def test_violence_by_anyone(text):
    assert assess(text)["text_risk"] >= 60


@pytest.mark.parametrize("text", ["พ่อไม่ให้หนูออกจากบ้านตอนกลางคืน", "น้องตามหนูกลับบ้าน", "แม่ไม่ให้หนูกินขนม", "ตีหนูในเกม",
                                  "เพื่อนผลักหนูเล่นตอนเล่นน้ำ"])
def test_house_rules_and_play_are_not_violence(text):
    assert assess(text)["text_risk"] < 60
