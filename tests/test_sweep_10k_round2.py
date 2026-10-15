"""ไล่หาบั๊กชุด 2: ความรุนแรง · การค้ามนุษย์ · วิธีทำร้ายตัวเอง · มิจฉาชีพ · หัวข้อที่เคยไม่มีคำตอบภาษาอังกฤษ"""
import pytest

from core.kernel_voice import assess, compose

GENERIC = ("เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว", "Write what happened in one sentence")


@pytest.mark.parametrize("text,min_risk", [
    ("คิดจะกินยาให้ตาย", 85), ("อยากยิงตัวเอง", 85), ("มีปืนอยู่ในบ้าน อยากยิงตัวเอง", 85), ("อยากกระโดดตึกตาย", 85),
    ("โดนคอลเซ็นเตอร์หลอกโอนเงิน", 60), ("เพื่อนหายออกจากบ้านไปสองวัน", 75),
    ("ลูกสาวถูกนายจ้างขังไว้ในโรงงาน", 80), ("เพื่อนถูกพาไปทำงานแก๊งคอลเซ็นเตอร์ที่กัมพูชา", 80),
    ("ถูกหลอกไปทำงานต่างประเทศแล้วถูกยึดพาสปอร์ต", 80), ("ไม่กินข้าวมาสามวัน อาเจียนทุกครั้งที่กิน", 60),
    ("แฟนบอกว่าจะฆ่าฉัน", 65),
    ("my friend got beaten by her husband", 75), ("my sister is being choked by her boyfriend", 75),
    ("my sister was threatened with a knife", 75), ("my sister is locked in a room", 75), ("my sister is being stalked by her ex", 60),
    ("my friend is trafficked and her passport was taken", 80), ("my friend can't stop vomiting blood", 85),
    ("my mom has a plan to end her life", 85), ("my friend is cutting herself", 75), ("my sister is missing since yesterday", 75),
])
def test_dangerous_cases_are_recognised(text, min_risk):
    assert assess(text)["text_risk"] >= min_risk
    assert not any(g in compose(text) for g in GENERIC)


@pytest.mark.parametrize("text,needle", [
    ("ถูกนายจ้างขังไว้ในโรงงาน", "ค้ามนุษย์"),
    ("พี่สาวอยากฆ่าแฟน", "อย่าเข้าไปขวางตัวต่อตัว"),
    ("my friend is drunk and wants to drive", "Don't get in that car"),
    ("I stopped taking my antidepressants suddenly", "Don't stop suddenly"),
    ("I got a needlestick injury at work", "within 2 hours"),
    ("my toddler drank some shampoo", "poison control"),
    ("my dog ate chocolate", "vet"),
    ("my boss hasn't paid me for 3 months", "1546"),
    ("I can't sleep for 4 days", "see a doctor"),
    ("I think I have an eating disorder", "treatable"),
    ("my friend sees things that aren't there", "very treatable"),
])
def test_specific_answer(text, needle):
    assert needle in compose(text)


@pytest.mark.parametrize("text", ["ฆ่าเวลา", "เพื่อนจะฆ่าฉันในเกม", "แม่ชักจะโมโห", "แทงบอลเสีย"])
def test_idioms_stay_calm(text):
    assert assess(text)["text_risk"] < 60


def test_threat_to_user_is_not_a_third_party_case():
    assert "อย่าเข้าไปขวางตัวต่อตัว" not in compose("สามีขู่ว่าจะฆ่าถ้าหนีไป")
