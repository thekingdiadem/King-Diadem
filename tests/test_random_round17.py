"""รอบสุ่ม 17: ภัยในบ้านที่คนมักไม่รู้ว่าอันตราย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["ได้กลิ่นแก๊สรั่วในห้องครัว", "smell gas in my apartment", "left my baby in the hot car for 20 minutes",
                               "running a generator in the garage, everyone has a headache", "จุดเตาถ่านในห้องปิดเพราะหนาว ตอนนี้ปวดหัว คลื่นไส้",
                               "ลืมลูกไว้ในรถ ตากแดดมาครึ่งชั่วโมง", "my son ate peanuts and his throat is swelling", "เด็กกลืนถ่านกระดุม"])
def test_hazard_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ["เติมแก๊สหุงต้มแล้ว", "gas prices are up again", "I left my phone in the car", "ทำแกงเห็ดฟางกินกับแม่",
                               "ลูกนอนในรถ เปิดแอร์ จอดรอแม่อยู่หน้าร้าน", "peanut butter sandwich for lunch"])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
