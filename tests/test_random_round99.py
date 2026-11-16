"""รอบสุ่ม 99: คนแปลกหน้าทุบประตูตอนดึก และ "พูดไม่ชัด" ที่ไม่ใช่สโตรก"""
import pytest
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("q", ["มีคนแปลกหน้าทุบประตูห้องตอนตีสอง", "someone is banging on my door at 2am",
                               "a stranger is trying to break my door right now"])
def test_stranger_at_the_door_at_night_is_urgent(q):
    # เดิมได้ 0 ทั้งไทยและอังกฤษ
    a = assess(q)
    assert a["risk_shown"] >= 80 and a["topics"][0] == "intruder"


def test_intruder_reply_says_dont_open_and_call_police():
    assert "อย่าเปิดประตู" in compose("มีคนแปลกหน้าทุบประตูห้องตอนตีสอง", footer=False)
    assert "don't open the door" in compose("someone is banging on my door at 2am", footer=False)


@pytest.mark.parametrize("q", ["ทุบประตูห้องน้ำเพราะลูกบิดค้าง", "มีคนเคาะประตูส่งพัสดุ", "someone banging on the door at the party lol",
                               "ยายพูดไม่ชัดเพราะไม่ใส่ฟันปลอม", "พ่อเมาพูดไม่ชัด ร้องคาราโอเกะ"])
def test_everyday_door_and_speech_are_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["พ่อพูดไม่ชัด ปากเบี้ยว", "แม่พูดไม่ชัดกะทันหัน"])
def test_real_stroke_signs_still_urgent(q):
    assert assess(q)["risk_shown"] >= 80
