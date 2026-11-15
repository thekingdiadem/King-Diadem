"""รอบสุ่ม 30: ข้อความจากรอบ 17–29 แบบพิมพ์ลากเสียง อีโมจิ และเครื่องหมายตกใจ (กันถอยหลัง)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['แท็กซี่ล็อกประตูไม่ให้ลง 😭😭 ช่วยด้วย', 'บ้านไฟไหม้ออกไม่ได้!!!!', 'ได้กลิ่นแก๊สรั่วววว', 'ลูกกินน้ำยาล้างห้องน้ำ ปากเปียก ทำไงดีๆๆ', 'พ่อพูดไม่รู้เรื่อง มือซ้ายยกไม่ขึ้นนนน', 'มีคนตามหลังมา ตอนนี้ยังเดินตามอยู่ กลัววว', 'taxi locked the doors 😭 help', 'smell gas in my apartment!!!', 'my teen has cuts on her arms 💔', 'left my baby in the hot car omg', 'เพื่อนจมน้ำ ดึงขึ้นมาไม่หายใจ ช่วยด้วยยยย', 'คลื่นซัดลูกลงทะเล!!! มองไม่เห็นแล้ว'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['แท็กซี่พาอ้อม 555', 'เติมแก๊สหุงต้มแล้ว 👍', 'ลูกช่วยล้างห้องน้ำ น่ารักมาก 🥰', 'my friend followed me on insta 😂'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
