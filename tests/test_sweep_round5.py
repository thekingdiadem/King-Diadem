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
