"""รอบสุ่ม 82: หอบหืด/แพ้รุนแรง/อาหารติดคอ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['หอบหืดกำเริบ พ่นยาแล้วไม่ดีขึ้น พูดเป็นคำๆ', 'กินถั่วไปแล้วลิ้นบวม คอตีบ หายใจลำบาก', 'พ่อกินข้าวแล้วติดคอ ไอไม่ออก หน้าเขียว', 'แพ้ยา ผื่นขึ้นทั้งตัว ตาบวม หน้ามืด', "asthma attack, inhaler isn't helping, can only speak a few words", 'ate peanuts, tongue swelling, throat closing', "my dad is choking on food, can't cough, turning blue", 'allergic reaction, hives everywhere, eyes swelling, feeling faint'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['หอบหืดนิดหน่อย พ่นยาแล้วดีขึ้น', 'แพ้ฝุ่น จามบ่อย', 'mild asthma, inhaler worked', 'allergic to dust, sneezing a lot'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
