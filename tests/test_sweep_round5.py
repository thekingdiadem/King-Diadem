"""รอบหาบั๊ก 5: อาการฉุกเฉินที่เคยได้ Risk 0 และยาเกินขนาดที่ตกใจเกินเหตุ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("text, topic", [
    ("จมน้ำ ช่วยขึ้นมาแล้ว ไม่หายใจ", "health_emergency"), ("ลูกตกน้ำ", "health_emergency"),
    ("แพ้กุ้ง ปากบวม หายใจลำบาก", "health_emergency"), ("มีดบาดลึก เลือดไม่หยุด", "health_emergency"),
    ("choking", "health_emergency"), ("my son is choking", "health_emergency"),
    ("ลูกกินยาพาราไป 10 เม็ด", "overdose"), ("ครูตีจนเป็นแผล", "violence"),
])
def test_emergencies_that_were_missed(text, topic):
    a = assess(text)
    assert topic in a["topics"] and a["text_risk"] >= 85


@pytest.mark.parametrize("text", [
    "กินยาคุมเกินไป 1 เม็ด", "กินพาราเกิน 8 เม็ดต่อวันอันตรายไหม", "กินยาวันละ 2 เม็ด",
    "สอนลูกว่ายน้ำกันจมน้ำ", "จมน้ำตาย ในหนัง", "ชีวิตจมน้ำตาคืนนี้", "I'm choking on my words lol",
    "แพ้อาหารทะเล ขึ้นผื่นนิดหน่อย", "แพ้ทาง หายใจลำบากเพราะวิ่ง",
])
def test_ordinary_text_is_not_an_emergency(text):
    a = assess(text)
    assert not ({"health_emergency", "overdose"} & set(a["topics"])) and a["text_risk"] < 85


@pytest.mark.parametrize("text", ["ติดพนันออนไลน์ หมดตัว", "เล่นบาคาร่าจนเป็นหนี้ 2 แสน", "I'm addicted to gambling and in debt"])
def test_gambling_losses_raise_risk(text):
    """เดิม "ติดพนันออนไลน์ หมดตัว" ได้ Risk 0"""
    a = assess(text)
    assert "addiction" in a["topics"] and a["text_risk"] >= 60


@pytest.mark.parametrize("text", ["ตำรวจเรียกรับเงิน", "โดนด่านรีดไถ", "จ่ายส่วยทุกเดือน"])
def test_bribery_gets_complaint_channels(text):
    from core.kernel_voice import compose
    assert "bribery" in assess(text)["topics"]
    r = compose(text)
    assert "1567" in r and "1205" in r


@pytest.mark.parametrize("text", ["ซื้อหวยงวดนี้", "พนันกันว่าใครจะชนะ", "หมดตัวเพราะซื้อของออนไลน์",
                                  "ตำรวจเรียกไปให้ปากคำ", "เจ้าหน้าที่เรียกเก็บค่าธรรมเนียมตามระเบียบ"])
def test_ordinary_money_and_police_talk(text):
    a = assess(text)
    assert "bribery" not in a["topics"] and "addiction" not in a["topics"]


@pytest.mark.parametrize("text", ["my boyfriend hits me I want to die", "my dad hit me and I'm suicidal"])
def test_own_crisis_after_naming_someone_else(text):
    """เดิม "my boyfriend ... I want to die" ถูกตีความว่าแฟนอยากตาย ผู้ใช้ไม่ได้สายด่วนของตัวเอง"""
    from core.kernel_voice import compose
    a = assess(text)
    assert a["crisis"] and "someone" not in a["topics"]
    assert "looking out for them" not in compose(text)


@pytest.mark.parametrize("text", ["my friend wants to die", "my mom said she wants to die", "my sister is suicidal",
                                  "my friend told me he wants to kill himself"])
def test_someone_else_in_crisis_still_detected(text):
    a = assess(text)
    assert "someone" in a["topics"] and not a["crisis"]
