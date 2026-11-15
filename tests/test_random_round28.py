"""รอบสุ่ม 28: สัตว์เลี้ยงฉุกเฉิน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['หมากินช็อกโกแลตไปทั้งแท่ง ตัวสั่น', 'แมวกัดดอกลิลลี่ในแจกัน', 'หมาท้องบวมเป่ง พยายามอ้วกแต่ไม่มีอะไรออก', 'หมาโดนรถชน ขาหลังขยับไม่ได้', 'แมวกินยาพาราของคน', 'my dog ate a whole chocolate bar and is shaking', 'my cat chewed on a lily from the vase', "dog's belly is swollen and he's trying to vomit but nothing comes out", "my dog got hit by a car and can't move his back legs", 'my cat ate my tylenol'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['หมาชอบกินขนมหมา', 'แมวนอนข้างแจกันดอกลิลลี่ ไม่ได้กัด', 'my dog loves his chew toy', "cat sleeps next to the lily but didn't touch it"])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
