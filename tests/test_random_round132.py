"""รอบสุ่ม 132: ฆ่าตัวตายในเกม (รีสปอว์น) ไม่ใช่วิกฤต — แต่คำอื่นในประโยคยังถูกอ่าน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "แฟนบอกว่าจะฆ่าตัวตายในเกมเพื่อเริ่มใหม่", "จะฆ่าตัวตายในเกมเพื่อเริ่มใหม่",
    "i killed myself in the game to respawn",
])
def test_game_respawn_is_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["อยากตายจริงๆ ฆ่าตัวตายในเกมก็ไม่ช่วย", "อยากฆ่าตัวตาย", "แฟนบอกว่าจะฆ่าตัวตายถ้าเลิก"])
def test_real_crisis_still_heard(q):
    assert assess(q)["risk_shown"] >= 85


def test_fiction_writing_keeps_its_gentle_check():
    a = assess("เขียนนิยาย ตัวละครฆ่าตัวตาย ช่วยเกลาให้หน่อย")
    assert not a["crisis"] and "soft_check" in a["topics"]
