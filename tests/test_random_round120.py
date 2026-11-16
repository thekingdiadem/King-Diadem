"""รอบสุ่ม 120: ขู่เอาชีวิตเพื่อทวงเงิน แม้ไม่มีคำว่า "ขู่" """
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "เพื่อนบอกว่าจะเอาให้ตายถ้าไม่จ่ายหนี้", "ถ้าไม่โอนคืนพรุ่งนี้ จะซ้อมให้ตาย", "เขาขู่จะเอาให้ถึงตาย",
])
def test_money_death_threat_is_urgent(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "grief" not in a["topics"][:1]


@pytest.mark.parametrize("q", ["แม่บอกจะตีให้ตายถ้าไม่ทำการบ้าน 555", "ขำจะตายถ้าไม่ได้ดูคลิปนี้"])
def test_family_teasing_stays_calm(q):
    assert assess(q)["risk_shown"] < 80
