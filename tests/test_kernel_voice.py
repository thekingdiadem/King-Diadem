"""คำตอบจากสมการ (ไม่ใช้ AI) — ต้องถูกหัวข้อ ไม่สุ่ม และมีทางเลือก ≥ 1 เสมอ"""
import pytest

from core.kernel_voice import assess, compose, simulate

NOT_TOPIC = [
    ("มีไอเดียธุรกิจใหม่", "health"), ("ไอทีบริษัทล่ม", "health"), ("กินไอศกรีมแล้วมีความสุข", "health"),
    ("ชักจะเบื่องานแล้ว", "health_emergency"), ("งานเยอะจนหายใจไม่ทัน", "health_emergency"),
    ("ปวดท้องตั้งแต่เช้า", "stress"), ("ตั้งท้องได้ 3 เดือน", "stress"), ("ท้องเสีย", "stress"),
    ("เว็บนี้ไม่ปลอดภัยหรือเปล่า", "violence"), ("เป็นแฟนบอลลิเวอร์พูล", "relationship"),
    ("แฟนคลับศิลปิน", "relationship"), ("ตรวจสอบเอกสาร", "study"), ("สอบถามราคา", "study"),
    ("ชักชวนเพื่อนลงทุน", "health_emergency"), ("ไม่สบายใจเรื่องงาน", "health"),
    ("อยากได้ software ใหม่", "relationship"), ("ถูกตีความผิด", "violence"), ("ซื้อไอโฟนดีไหม", "health"),
    ("ชอบหนังแฟนตาซี", "relationship"),
]
TOPIC = [
    ("ไอมาสามวัน", "health"), ("ลูกชักเกร็ง", "health_emergency"), ("หายใจไม่ออก แน่นหน้าอก", "health_emergency"),
    ("ท้อแท้มาก", "stress"), ("แฟนบอกเลิก", "relationship"), ("ถูกแฟนทำร้าย", "violence"),
    ("โดนพ่อตีทุกวัน", "violence"), ("รู้สึกไม่ปลอดภัยที่บ้าน", "violence"), ("พรุ่งนี้จะสอบ อ่านไม่ทัน", "study"),
    ("เป็นไข้สูง", "health"), ("ไม่สบายมาสองวัน", "health"), ("ไม่มีข้าวกินมาสองวัน", "basic"),
]


@pytest.mark.parametrize("text,topic", NOT_TOPIC)
def test_not_topic(text, topic):
    assert topic not in assess(text)["topics"]


@pytest.mark.parametrize("text,topic", TOPIC)
def test_topic(text, topic):
    assert topic in assess(text)["topics"]


def test_crisis_gives_hotlines():
    r = compose("อยากตาย ไม่ไหวแล้ว")
    assert "1323" in r and "1669" in r


def test_violence_before_relationship():
    assert compose("ถูกแฟนทำร้าย").startswith("ความปลอดภัยของคุณมาก่อน")


def test_deterministic_and_always_a_choice():
    for t in ["ตกงาน", "", "😀" * 500, "ควรลาออกหรือทำต่อดี"]:
        a, b = compose(t), compose(t)
        assert a == b
        assert "1)" in a or "1323" in a or "สวัสดี" in a


def test_simulate_prefers_reversible():
    out = simulate("จะเปิดร้านกาแฟ", ["ลาออกแล้วเปิดร้านเลย", "ขายออนไลน์ช่วงเสาร์อาทิตย์ก่อน"])
    assert "แนะนำเริ่มจาก B" in out
