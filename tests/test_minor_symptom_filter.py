"""อาการเล็กน้อยที่มีสาเหตุธรรมดา ต้องไม่ถูกเตือนเป็นเหตุฉุกเฉิน — แต่สัญญาณอันตรายต้องชนะเสมอ"""
import pytest
from core.kernel_voice import assess

CALM = [
    "เจ็บหน้าอกนิดหน่อยตอนหายใจลึกๆ เพราะเป็นหวัด",
    "Slight chest pain when I breathe deeply because of a cold",
    "Leve dolor de pecho al respirar hondo por el resfriado",
    "เจ็บหน้าอกนิดหน่อยตอนวิ่งเพราะจุก",
    "ลูกกินปลาทูแล้วไอเพราะสำลักน้ำแกง สักพักก็หาย",
    "庭で薬をまくときは防護服を全部着る",
    "의사가 관절 진통제를 사흘 처방했는데 다 먹었어요",
    "ปากบวมนิดหน่อยเพราะกินเผ็ด",
    "หายใจไม่ทันตอนวิ่งขึ้นเขา พักแล้วหาย",
    "爬山喘不过气，休息就好",
    "指を切り落とすシーンのあるホラー映画を見た",
]
DANGER = [
    "เจ็บหน้าอกร้าวไปแขนซ้าย เหงื่อแตก",
    "ลูกสำลักกระดูกปลา หายใจไม่ออก",
    "chest pain while running and sweating a lot",
    "เจ็บหน้าอกนิดหน่อยตอนวิ่ง แต่ยังไม่หายเลย เหงื่อแตก",
    "我把药都吃完了，不想活了",
]


@pytest.mark.parametrize("text", CALM)
def test_minor_with_benign_cause_is_calm(text):
    r = assess(text)
    assert r["text_risk"] < 60 and not r["crisis"], (text, r["topics"])


@pytest.mark.parametrize("text", DANGER)
def test_red_flags_still_win(text):
    r = assess(text)
    assert r["text_risk"] >= 75 or r["crisis"], (text, r["topics"])


def test_whole_bottle_of_cough_syrup_is_not_minor():
    # "ho" = ไอ และ "hết" = หมด ไม่ใช่ "หายแล้ว"
    assert assess("con tôi uống hết cả chai siro ho của người lớn")["risk_shown"] >= 65
