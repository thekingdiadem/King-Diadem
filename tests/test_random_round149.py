"""รอบสุ่ม 149: ผู้ใหญ่แปลกหน้าขอรูปจากเด็ก (es zh ko ja) — เคยได้ 0 (ประโยคเขียนเองในรอบนี้)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "Mi hijo de 13 habla con un adulto que le pide fotos", "我13岁的女儿在网上被陌生人要裸照",
    "열두 살 딸이 모르는 어른에게 사진을 요구받고 있어요", "12歳の娘が知らない大人に裸の写真を要求されている",
])
def test_adult_asking_child_for_photos_is_urgent(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "online_grooming" in a["topics"]


@pytest.mark.parametrize("q", [
    "Mi hija de 13 me pide fotos de cuando era bebé", "我女儿要我给她拍照片", "딸이 가족사진을 보내 달래요",
    "娘の運動会の写真を知り合いに送った",
])
def test_family_photos_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
