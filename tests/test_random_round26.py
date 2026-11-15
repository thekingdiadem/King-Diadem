"""รอบสุ่ม 26: ความปลอดภัยส่วนตัวนอกบ้าน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['มีคนตามหลังมาตั้งแต่ลงรถเมล์ ตอนนี้ยังเดินตามอยู่', 'แท็กซี่ขับออกนอกเส้นทาง ล็อกประตูไม่ให้ลง', 'คนแปลกหน้าในผับใส่อะไรในแก้ว ตอนนี้มึนมาก', 'เพื่อนไปเดทกับคนในแอป ไม่ติดต่อกลับมาสิบชั่วโมงแล้ว', 'แฟนเก่าแอบติด GPS ที่รถ ตามมาถึงที่ทำงาน', 'someone has been following me since I got off the bus', 'the taxi went off route and locked the doors', 'a stranger put something in my drink, I feel really dizzy', "my friend went on a dating app date and hasn't answered in 10 hours", 'my ex put a tracker on my car and showed up at my work'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['เพื่อนเดินตามมาข้างหลัง คุยกันสนุก', 'แท็กซี่พาอ้อมนิดหน่อย เสียตังค์เพิ่ม', 'my friend followed me on instagram', 'the taxi took a longer route, cost more'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
