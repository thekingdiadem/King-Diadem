"""รอบสุ่ม 207 (เดิมเลข 137 ซึ่งซ้ำกับอีกแชท): น้ำตาลในเลือดต่ำในคนเป็นเบาหวาน · ตกเลือดหลังคลอด (อังกฤษ) · เบาหวานออกกำลังแล้วสดชื่น ≠ ฉุกเฉิน"""
import pytest
from core.kernel_voice import assess

REAL = ["พ่อเป็นเบาหวาน กินข้าวไม่ได้ทั้งวัน ตอนนี้เหงื่อแตก มือสั่น พูดไม่รู้เรื่อง", "just gave birth 3 days ago and bleeding won't stop",
        "my diabetic dad is sweaty, shaking and confused", "เบาหวานออกกำลังกายแล้วเหงื่อแตก หน้ามืดจะเป็นลม", "แม่เป็นเบาหวาน หน้ามืดจะเป็นลม",
        "ลูก 2 ขวบเปิดตู้กินยาความดันของยายไปหลายเม็ด", "แม่เพิ่งคลอดได้ 3 วัน เลือดออกไม่หยุด"]
CALM = ["เบาหวานออกกำลังกายแล้วเหงื่อแตก สดชื่นดี", "พ่อเป็นเบาหวาน คุมอาหารดีขึ้นมาก", "just gave birth 3 days ago, baby is feeding well",
        "แม่คลอดลูกแล้ว แข็งแรงดีทั้งคู่", "เจอตะขาบในบ้าน ตีตายแล้ว"]


@pytest.mark.parametrize("t", REAL)
def test_urgent(t):
    # สองข้อแรกเคยได้ 0
    assert assess(t)["risk_shown"] >= 80


@pytest.mark.parametrize("t", CALM)
def test_calm(t):
    # "เบาหวานออกกำลังกายแล้วเหงื่อแตก สดชื่นดี" เคยได้ 85
    assert assess(t)["risk_shown"] < 60
