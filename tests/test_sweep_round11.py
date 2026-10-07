"""รอบหาบั๊ก 11: ข่าวน้ำท่วมบ้าน · กลิ่นแก๊ส · SMS ลิงก์ · เหงา (อังกฤษ)"""
from core.kernel_voice import assess


def test_news_or_past_flood_at_home_is_not_happening_now():
    now = assess("น้ำท่วมบ้าน")["risk"]
    for t in ("ข่าวน้ำท่วมบ้าน", "น้ำท่วมบ้านเมื่อปีที่แล้ว"):
        assert assess(t)["risk"] < now, t
    assert assess("ข่าวน้ำท่วม ตอนนี้ท่วมบ้านแล้ว")["risk"] >= now


def test_smelling_gas_is_urgent():
    for t in ("I smell gas", "ได้กลิ่นแก๊สในห้อง"):
        assert assess(t)["risk"] >= 60, t
    assert assess("ข่าวแก๊สรั่ว")["risk"] < 60


def test_sms_phishing_link_is_scam():
    for t in ("ได้ sms ให้กดลิงก์ยืนยันบัญชี", "มีข้อความไลน์ส่งลิงก์มาให้รับเงินคืนภาษี",
              "got a text with a link to verify my account"):
        assert "scam" in assess(t)["topics"], t
    for t in ("ส่งข้อความหาแม่", "เพื่อนส่งลิงก์เพลงมาในไลน์"):
        assert "scam" not in assess(t)["topics"], t


def test_english_loneliness():
    for t in ("I feel lonely", "nobody cares about me", "I have no friends"):
        assert "lonely" in assess(t)["topics"], t
