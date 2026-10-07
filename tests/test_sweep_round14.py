"""รอบหาบั๊ก 14: ถูกขโมย · รีดไถ · รูปโป๊ถูกโพสต์ · ภาษาอังกฤษ (homeless/fever/locked in/touched) · บังคับทำงาน"""
from core.kernel_voice import assess, compose


def test_theft_topic():
    for t in ("โดนขโมยมอเตอร์ไซค์", "โดนวิ่งราว", "มือถือหาย", "my phone was stolen"):
        assert "theft" in assess(t)["topics"], t
    for t in ("ขโมยซีน", "จับขโมยได้", "รถหายไปไหน"):
        assert "theft" not in assess(t)["topics"], t
    assert "อายัด" in compose("โดนวิ่งราว", "general")
    assert '"theft" in k_topics' in open("app.py", encoding="utf-8").read()


def test_intimate_images_posted_without_threat():
    assert "sextortion" in assess("แฟนเก่าเอารูปโป๊ไปโพสต์")["topics"]
    assert "sextortion" not in assess("ส่งรูปส่วนตัวให้แฟนดู")["topics"]


def test_english_and_misc():
    assert "bullying" in assess("น้องโดนรุ่นพี่รีดไถ")["topics"]
    assert "basic" in assess("I am homeless")["topics"]
    assert "health" in assess("my kid has a high fever")["topics"]
    assert "health" not in assess("fever dream")["topics"]
    assert "health" in assess("ตัวร้อนจี๋")["topics"]
    assert "labor" in assess("ถูกบังคับให้ทำงาน")["topics"]
    assert assess("someone locked me in")["risk"] >= 85
    assert "sexual_abuse" in assess("someone touched me on the bus")["topics"]
    assert "stress" in assess("เหนื่อยกับชีวิต")["topics"]
