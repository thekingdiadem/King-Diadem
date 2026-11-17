"""รอบสุ่ม 145: ถูกบีบคอ/รัดคอ ใน es vi zh ko ja — เคยได้ 0 ทุกภาษา
(ประโยคเขียนขึ้นเองในรอบนี้ ไม่ได้คัดลอกจากชุดปิดตา เพื่อไม่จูนกับข้อสอบ)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "Mi esposo me aprieta el cuello cuando bebe", "Mi novio intentó estrangularme anoche",
    "Chồng tôi bóp cổ tôi mỗi khi say", "男朋友昨晚掐住我的脖子", "그 사람이 내 목을 졸랐어요", "彼氏に首を絞められた",
])
def test_strangulation_is_emergency(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "violence" in a["topics"]


@pytest.mark.parametrize("q", [
    "Me duele el cuello por dormir mal", "Cổ tôi bị đau vì ngồi máy tính", "我脖子很酸，可能是落枕了",
    "목이 아파서 병원에 가요", "首が痛いので湿布を貼った", "ネクタイで首を締め付けられる感じがして苦手",
])
def test_neck_pain_and_ties_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
