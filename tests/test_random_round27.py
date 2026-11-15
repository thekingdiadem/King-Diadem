"""รอบสุ่ม 27: อุบัติเหตุในที่ทำงาน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['คนงานตกถังสารเคมี เพื่อนลงไปช่วยแล้วหมดสติทั้งคู่', 'ทำงานในโรงงาน ร้อนมาก เพื่อนพูดไม่รู้เรื่อง ตัวร้อนจัด หยุดเหงื่อ', 'หัวหน้าบังคับให้ทำงานบนที่สูงไม่มีเชือก เพื่อนเพิ่งตกลงไป', 'ไซต์ก่อสร้าง ปั้นจั่นล้มทับคน', 'เครื่องจักรดูดแขนเพื่อนเข้าไป', 'a worker fell into the tank and the guy who went in after him passed out too', 'in the factory heat my coworker is confused, very hot and stopped sweating', 'crane fell on someone at the construction site', "the machine pulled my coworker's arm in", 'คนงานตกจากนั่งร้านชั้นสาม'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ทำงานโรงงาน ร้อนแต่ดื่มน้ำบ่อย', 'หัวหน้าให้ทำโอทีทุกวัน เหนื่อย', 'factory work is hot, drinking lots of water', 'my boss makes me work overtime', 'เพื่อนตกลงไปในรักครั้งใหม่', 'เพื่อนตกลงไปเที่ยวด้วย', 'ราคาหุ้นตกลงมาเยอะ', 'the stock price fell on my birthday'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
