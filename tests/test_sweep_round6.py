"""รอบหาบั๊ก 6 (ต่อ): วิกฤตของคนอื่น · มิจฉาชีพแบบใหม่ · อันตรายในบ้านและสุขภาพ"""
import pytest
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text", ["เพื่อนส่งคลิปตัวเองกรีดแขน", "น้องบอกว่าจะกินยาฆ่าตัวตายคืนนี้"])
def test_someone_elses_crisis_is_not_the_users(text):
    """เดิมนับว่าผู้ใช้เองอยู่ในวิกฤต — คำตอบเลยไม่ได้บอกวิธีช่วยเพื่อน/น้อง"""
    a = assess(text)
    assert "someone" in a["topics"] and not a["crisis"]


@pytest.mark.parametrize("text, flag", [
    ("มีคนโทรมาบอกว่าลูกโดนจับ ให้โอนค่าประกันตัว", "story"),
    ("ได้ไลน์จากเพื่อน ขอยืมเงินด่วน", "story"),
    ("แฟนในแอปหาคู่ชวนลงทุนคริปโต", "romance"),
])
def test_new_scam_patterns(text, flag):
    assert flag in assess(text)["scam"]


def test_stranger_asking_for_nudes_is_sextortion_risk():
    assert "sextortion" in assess("คนในเน็ตขอรูปโป๊")["topics"]


@pytest.mark.parametrize("text, topic", [
    ("ป้ากินยาเบาหวานแล้วตัวเย็น เหงื่อแตก", "health_emergency"),
    ("หลานไข้สูง ซึม ไม่ยอมกินนม", "health_emergency"),
    ("หมาบ้าวิ่งไล่กัดคน", "first_aid"),
    ("ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง", "witness"),
    ("สอบตก ชีวิตจบแล้ว", "warning"),
])
def test_missed_dangers(text, topic):
    assert topic in assess(text)["topics"]


@pytest.mark.parametrize("text", ["แม่ลืมปิดแก๊ส ได้กลิ่นแก๊สเต็มบ้าน", "there's a gas leak"])
def test_gas_leak_is_a_hazard(text):
    a = assess(text)
    assert a["disaster"]["kind"] == "gas" and a["text_risk"] >= 50
    assert "199" in compose(text)


@pytest.mark.parametrize("text", ["เพื่อนขอยืมเงินไปซื้อข้าว", "ลูกโดนจับได้ว่าโดดเรียน", "ไม่ใช่ชีวิตจบแล้ว แค่เริ่มใหม่",
                                  "ชีวิตจบแล้ว 555 ลืมการบ้าน", "ลงทุนคริปโตดีไหม", "เพื่อนส่งรูปเลือดกำเดาไหล",
                                  "แก๊สหมด ต้องซื้อใหม่", "ราคาแก๊สขึ้น"])
def test_round6b_ordinary_phrases(text):
    a = assess(text)
    assert not a["crisis"] and not a["scam"] and a["disaster"] is None
    assert not {"someone", "warning"} & set(a["topics"])


@pytest.mark.parametrize("text, topic", [
    ("ลูกเอาเงินบำนาญแม่ไปหมด ไม่ให้กินข้าว", "elder_abuse"),
    ("ยายถูกทิ้งไว้คนเดียว ไม่มีใครดูแล", "basic"),
    ("แรงงานพม่าถูกยึดบัตร ไม่ได้ค่าแรง", "labor"),
    ("ตำรวจจับ ไม่ให้โทรหาใคร", "legal"),
    ("กินเหล้าทุกวัน หยุดไม่ได้", "addiction"),
    ("แฟนติดยา อาละวาด", "violence"),
    ("น้องสาวหายไปกับคนในเน็ต", "missing"),
    ("คนแก่หลงทาง เดินอยู่ริมถนน", "missing"),
    ("my boss touches me", "sexual_abuse"),
    ("my husband won't let me leave", "violence"),
    ("my child is missing", "missing"),
])
def test_round7_missed_topics(text, topic):
    """รอบหาบั๊ก 7: ผู้สูงอายุ · แรงงาน · เสพติด · คนหาย · ภาษาอังกฤษ เคยไม่เข้าหัวข้อ"""
    assert topic in assess(text)["topics"]


def test_english_right_now_hazard_is_active():
    assert assess("I smell gas in my apartment right now")["text_risk"] >= 60


@pytest.mark.parametrize("text", ["แม่ไม่ให้กินขนม", "กินเหล้าทุกวันเสาร์", "ไม่ให้กินข้าวก่อนเจาะเลือด",
                                  "my boss touches base with me weekly"])
def test_round7_ordinary_phrases(text):
    assert not {"violence", "sexual_abuse", "addiction"} & set(assess(text)["topics"])
