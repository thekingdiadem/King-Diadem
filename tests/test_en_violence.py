"""ความรุนแรงภาษาอังกฤษ — ตาราง 10,200 ข้อความเคยหลุด 2,675 (คนทำร้ายที่ไม่ใช่สามี/แฟน · ผลักตกบันได · ถือมีดขู่ · สะกดรอย)
และสำนวน "beats me why" "that song hits me hard" "my brother beats me at chess" เคยได้ 85"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text", [
    "a stranger punches me", "my stepdad pushed me down the stairs", "someone has a knife and is threatening me",
    "a stranger is following me home", "my boss keeps touching me", "my mom burns me with cigarettes", "my teacher keeps touching me",
    "he took my phone and locked the door", "there is a man with a knife outside my door", "my dad beats my mom every night",
    "he beats me when he is drunk",
])
def test_english_violence_is_recognised(text):
    assert assess(text)["text_risk"] >= 60


@pytest.mark.parametrize("text", ["beats me why", "that song hits me hard", "my brother beats me at chess", "my back hurts me",
                                  "he kicks me out of the game lol", "a man with a knife on the cooking show"])
def test_english_idioms_are_not_violence(text):
    assert assess(text)["text_risk"] < 60


def test_minor_dating_adult():
    for t in ("I'm 15 and my boyfriend is 30", "หนูอายุ 14 ปี แฟนอายุ 28"):
        assert assess(t)["text_risk"] >= 70
    assert "1387" in compose("หนูอายุ 14 ปี แฟนอายุ 28")
