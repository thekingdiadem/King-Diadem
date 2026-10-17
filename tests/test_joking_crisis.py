"""'อยากตาย 555' / 'I want to die 😂' — ประโยคเปิดนุ่มลง แต่เบอร์ช่วยเหลือยังครบ"""
from core.kernel_voice import compose


def test_joking_thai_gets_gentle_opener_but_keeps_hotline():
    out = compose("อยากตาย 555")
    assert out.startswith("อ่านแล้วเหมือนพูดขำๆ") and "1323" in out and "1669" in out


def test_joking_english_gets_gentle_opener():
    out = compose("I want to die 😂")
    assert out.startswith("That sounds like it might be a joke")


def test_laughter_with_method_stays_serious():
    assert compose("อยากตาย กินยา 30 เม็ด 555").startswith("ฉันได้ยินสิ่งที่คุณพูด")
    assert compose("lol bought pills, want to die tonight").startswith("I hear you")


def test_plain_crisis_unchanged():
    assert compose("อยากตาย").startswith("ฉันได้ยินสิ่งที่คุณพูด")


def test_translation_review_file_is_current():
    """ไฟล์ให้เจ้าของภาษาตรวจต้องตรงกับโค้ด — ถ้าล้ม รัน python scripts/build_translation_review.py"""
    from scripts import build_translation_review as tr
    assert open(tr.OUT, encoding="utf-8").read() == tr.render()
