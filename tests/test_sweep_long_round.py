"""ไล่หาบั๊กรอบยาว (หลัง PR #72): เรื่องฉุกเฉินที่หลุด · ข้อเสนอหลอกลงทุน · นายหน้า · ไล่ออกจากหอ
· เพื่อนยืมเงินไม่คืน · หลังน้ำลด · ลูกไม่ยอมไปโรงเรียน"""
import pytest

from core.engine_bridge import parse_debts
from core.kernel_voice import assess, compose
from core.thai_signals import offer_red_flags


# A: เดิม Risk 0 + "เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว"
@pytest.mark.parametrize("text,needle", [("ลูก 2 ขวบกลืนถ่านกระดุม", "1669"), ("น้องกินแม่เหล็กติดตู้เย็นเข้าไป", "1669"),
                                         ("my toddler swallowed a button battery", "emergency room")])
def test_swallowed_battery_or_magnet_is_an_emergency(text, needle):
    a = assess(text)
    assert a["topics"][0] == "swallowed" and a["text_risk"] >= 75
    assert needle in compose(text)


@pytest.mark.parametrize("text", ["ลูกอมเหรียญช็อกโกแลตอร่อยไหม", "น้องหมากลืนถ่านกระดุม"])
def test_candy_and_pets_are_not_a_child_swallowing(text):
    assert "swallowed" not in assess(text)["topics"]


# D: เดิมได้คำแนะนำทำธุรกิจ Risk 0
@pytest.mark.parametrize("text", ["มีคนทักมาชวนลงทุนคริปโต ได้ 30% ต่อเดือน", "ลงทุนได้ 10% ต่อวัน", "invest and get 20% a month"])
def test_monthly_percentage_offer_is_flagged(text):
    assert "guarantee" in offer_red_flags(text)


def test_offer_reply_warns():
    assert "สัญญาณที่พบบ่อยในการหลอกลงทุน" in compose("มีคนทักมาชวนลงทุนคริปโต ได้ 30% ต่อเดือน")


# C
def test_broker_fee_for_overseas_work_points_to_department_of_employment():
    out = compose("อยากย้ายไปทำงานญี่ปุ่น มีนายหน้าเรียกค่าหัว 80,000")
    assert "1694" in out


# E
def test_eviction_by_tomorrow_gets_tenant_rights():
    out = compose("เจ้าของหอไล่ออก ให้ย้ายภายในพรุ่งนี้")
    assert "บอกกล่าวล่วงหน้า" in out and "1300" in out


# G: เดิม "หนี้ที่คุณเล่ามา: เงินยืม 20,000"
@pytest.mark.parametrize("text", ["โดนเพื่อนยืมเงิน 20,000 ไม่ยอมคืน", "ให้แฟนยืมไป 5 หมื่น ตอนนี้เลิกกันแล้ว"])
def test_money_lent_out_is_not_the_users_debt(text):
    assert parse_debts(text) == []
    out = compose(text)
    assert "ทวงคืนได้" in out and "หนี้ที่คุณเล่ามา" not in out


def test_money_borrowed_by_user_is_still_debt():
    assert parse_debts("ยืมเงินเพื่อนมา 10,000 ยังไม่มีคืน")


def test_lent_english():
    assert "asked back" in compose("my friend borrowed 500 and won't pay it back")


# B: เดิม "ขึ้นที่สูงหรือชั้นบน"
def test_flood_aftermath_is_not_an_active_flood():
    out = compose("บ้านโดนน้ำท่วมเมื่อวาน ตอนนี้น้ำลดแล้ว")
    assert "ฉี่หนู" in out and "ขึ้นที่สูง" not in out
    assert "ขึ้นที่สูง" in compose("น้ำท่วมบ้าน ติดอยู่บนหลังคา")


# F: เดิม "ครอบครัวเลือกไม่ได้ แต่ระยะห่างเลือกได้"
def test_child_refusing_school():
    out = compose("ลูกไม่ยอมไปโรงเรียน ร้องไห้ทุกเช้า")
    assert "ฟังก่อนบังคับ" in out and "ระยะห่างเลือกได้" not in out
