"""รอบสุ่ม 229: ข้อยกเว้นต้องทนเครื่องหมายวรรคตอนและการสลับลำดับท่อน
assess ลองสลับลำดับท่อนที่คั่นด้วยจุลภาค — ข้อยกเว้นที่ดูแค่ "ข้างหลังคำ" จึงพังเมื่อมีจุลภาค
("i hurt myself, at the gym" เคยเป็นวิกฤต) ตอนนี้ข้อยกเว้นเหล่านี้ดูทั้งข้อความ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "i hurt myself, at the gym lifting", "Me corto, el pelo mañana", "this is my last post, of the year",
    "I've given away everything, at the garage sale, sorted now", "ถ้าเห็นข้อความนี้ แปลว่าหนูไปแล้ว ไปเที่ยวทะเลนะ",
    "if you're reading this I'm already gone, on my flight to Bali", "at the gym, i hurt myself lifting",
])
def test_exceptions_survive_commas_and_reordering(q):
    r = assess(q)
    assert not r["crisis"] and r["risk_shown"] < 60


@pytest.mark.parametrize("q", [
    "i keep hurting myself", "this is my last post", "me corto otra vez", "Me corto los brazos todas las noches",
    "ถ้าเห็นข้อความนี้ แปลว่าหนูไปแล้ว", "if you're reading this I'm already gone", "I've given away everything, it's all sorted now",
])
def test_real_signals_still_caught(q):
    r = assess(q)
    assert r["crisis"] or r["risk_shown"] >= 80
