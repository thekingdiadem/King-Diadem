"""รอบสุ่ม 25: คนท้องและทารกแรกเกิด (ผ่านตั้งแต่ครั้งแรก — กันถอยหลัง)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ท้อง 8 เดือน ปวดหัวมาก ตามัว เท้าบวม', 'ตั้งท้อง 3 เดือน เลือดออกเยอะ ปวดท้องบิด', 'ลูกแรกเกิด 2 สัปดาห์ ตัวร้อน ไม่ยอมดูดนม', 'ลูก 6 เดือน หายใจหอบ ซี่โครงบุ๋ม', 'หลังคลอดเลือดออกชุ่มผ้าอนามัยทุกชั่วโมง', '36 weeks pregnant with a terrible headache, blurry vision and swollen feet', '12 weeks pregnant, bleeding heavily with cramping', "my 2 week old has a fever and won't feed", 'my baby is breathing fast and her ribs are sucking in', 'soaking a pad every hour after giving birth'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ท้อง 5 เดือน อยากกินมะม่วงดอง', 'ลูกแรกเกิดนอนเยอะ ปกติไหม', 'pregnant and craving pickles', 'newborn sleeps a lot, is that normal?'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
