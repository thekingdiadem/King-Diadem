"""รอบสุ่ม 81: ความร้อน/ความเย็นที่อันตราย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['คนงานก่อสร้างล้มกลางแดด ตัวร้อนมาก ไม่มีเหงื่อ พูดไม่รู้เรื่อง', 'ยายอยู่บ้านคนเดียว ร้อน 40 องศา ไม่มีพัดลม ซึมๆ', 'เด็กเล่นน้ำทะเลตอนหนาว ตัวสั่น ปากม่วง ง่วงซึม', 'ทำงานในห้องเย็นติดอยู่ข้างใน ประตูเปิดไม่ได้', 'a worker collapsed in the sun, very hot skin, not sweating, confused', 'grandma alone at home, 40 degrees, no fan, very drowsy', 'my kid was swimming in cold water, shivering, blue lips, very sleepy', "I'm stuck inside the walk-in freezer at work, door won't open"])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ร้อนจัง ไปว่ายน้ำดีกว่า', 'หนาวจัง ขอผ้าห่มเพิ่ม', "it's so hot today, going for ice cream", 'cold morning, made hot cocoa'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
