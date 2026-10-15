"""ไล่หาบั๊กรอบยาว 2: ชักตอนไข้สูง · ไส้ติ่ง · ไฟไหม้ · panic (อังกฤษ) · ประกัน/ร้านออนไลน์ · บัญชีโดนแฮก
· แฟนเก่าโพสต์รูป · หย่า · เปิดร้าน · ถูกปลด · กู้เรียนต่อ · ค่าชดเชย · พ่อแม่สูงอายุขับรถ · ลูกหมากินถ่าน"""
import pytest

from core.engine_bridge import parse_debts
from core.kernel_voice import assess, compose


def test_child_febrile_seizure_is_emergency_with_first_aid():
    out = compose("ลูกชักตอนไข้สูง")
    assert assess("ลูกชักตอนไข้สูง")["text_risk"] >= 75
    assert "1669" in out and "ห้ามงัดปาก" in out


def test_lower_right_abdominal_pain_with_fever():
    out = compose("ปวดท้องขวาล่างมาก มีไข้")
    assert "ไส้ติ่ง" in out and "คนท้อง" not in out and "เด็กไข้สูง" not in out


def test_fire_reply_does_not_start_with_eat_and_sleep():
    out = compose("ไฟไหม้ห้องข้างๆ ควันเข้ามาในห้อง", route="survival")
    assert "ออกจากอาคารทันที" in out and "กิน นอน ดื่มน้ำ" not in out


def test_panic_attack_english():
    assert "4, hold for 4" in compose("I think I'm having a panic attack")


@pytest.mark.parametrize("text,needle", [("ประกันไม่ยอมจ่ายค่ารักษา", "1186"), ("ซื้อของออนไลน์ ร้านไม่ส่งของ", "1166"),
                                         ("the seller never shipped my order", "chargeback")])
def test_consumer_problems(text, needle):
    assert needle in compose(text)


@pytest.mark.parametrize("text", ["เฟซโดนแฮก มีคนทักไปยืมเงินเพื่อน", "someone hacked my facebook and is asking my friends for money"])
def test_hacked_account(text):
    out = compose(text)
    assert "1441" in out


def test_ex_posting_photos_is_not_a_breakup():
    assert "sextortion" in assess("แฟนเก่าเอารูปไปโพสต์")["topics"]


def test_divorce_with_children():
    out = compose("แต่งงานมา 10 ปี อยากหย่า แต่กลัวลูกมีปัญหา")
    assert "1167" in out and "อำนาจปกครอง" in out


def test_planning_a_shop():
    out = compose("อยากเปิดร้านกาแฟ มีเงิน 300,000")
    assert "เงินหมุน" in out and "≈ 2,000 วัน" not in out


def test_laid_off_gets_severance_table():
    for t in ("ถูกปลดจากงานเพราะอายุมาก", "ถูกเลิกจ้าง ได้ค่าชดเชยไหม"):
        assert "20 ปีขึ้นไป = 400 วัน" in compose(t)


def test_future_student_loan_is_not_debt():
    assert parse_debts("อยากเรียนต่อ ป.โท แต่ต้องกู้ 300,000") == []
    assert parse_debts("กู้มาแล้ว 300,000 ผ่อนไม่ไหว")
    assert "ก่อนกู้เรียนต่อ" in compose("อยากเรียนต่อ ป.โท แต่ต้องกู้ 300,000")


def test_elderly_parent_driving():
    assert "ให้หมอเป็นคนกลาง" in compose("พ่อแก่แล้ว ขับรถไม่ไหว แต่ไม่ยอมเลิกขับ")


def test_puppy_eating_charcoal_is_a_pet_case():
    a = assess("ลูกหมากินถ่าน")
    assert "pet_poison" in a["topics"] and "health_emergency" not in a["topics"]
