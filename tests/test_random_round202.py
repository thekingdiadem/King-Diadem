"""รอบสุ่ม 202 (เดิมเลข 132 ซึ่งซ้ำกับอีกแชท): ราดน้ำมันขู่จุดไฟ · ทวงหนี้ปาสีขู่จะกลับมา · ปืนบนโต๊ะตอนทะเลาะ · ยาลดน้ำหนักแล้วใจสั่น · ลูกหายไปกับคนจากเน็ต
และ "ราดน้ำมันใส่สลัด" ที่เคยได้ 85"""
import pytest
from core.kernel_voice import assess

REAL = ["ผัวเอาน้ำมันราดตัวขู่จะจุดไฟ", "แม่โดนแก๊งทวงหนี้มาปาสีใส่บ้าน ขู่จะมาอีกคืนนี้", "พ่อเอาปืนมาวางบนโต๊ะตอนทะเลาะกับแม่",
        "เพื่อนกินยาลดน้ำหนักจากเน็ตแล้วใจสั่นหนักมาก", "my dad put a gun on the table while yelling at mom",
        "my daughter ran off with a guy she met online, no contact for 2 days", "he poured gasoline on himself and is threatening to light it",
        "debt collectors splashed paint on our house and said they'll be back tonight", "ลูกสาวหนีไปกับผู้ชายที่รู้จักในเน็ต ติดต่อไม่ได้ 2 วัน"]
CALM = ["พ่อทำความสะอาดปืนบนโต๊ะ เตรียมไปสนามยิงปืน", "ลูกสาวไปเที่ยวกับแฟน กลับพรุ่งนี้", "เพื่อนกินยาลดน้ำหนักแล้วผอมลง 3 กิโล",
        "ราดน้ำมันใส่สลัด", "ราดน้ำมันมะกอกบนขนมปัง", "my dad cleans his hunting rifle on Sundays", "เอามีดมาวางบนโต๊ะตอนหั่นผัก"]


@pytest.mark.parametrize("t", REAL)
def test_missed_before_now_urgent(t):
    assert assess(t)["risk_shown"] >= 80


@pytest.mark.parametrize("t", CALM)
def test_everyday_calm(t):
    assert assess(t)["risk_shown"] < 60
