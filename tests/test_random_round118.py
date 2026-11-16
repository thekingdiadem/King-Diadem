"""รอบสุ่ม 118: "หลงป่า" (ไม่มีคำว่าหลงทาง) ต้องได้เท่า "lost in the woods" """
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["หลงป่า แบตเหลือ 5%", "หลงป่า มืดแล้ว"])
def test_lost_in_forest_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


def test_friend_lost_on_mountain_gets_stranded_advice():
    assert "stranded" in assess("เพื่อนหลงเขา ติดต่อไม่ได้")["topics"]


@pytest.mark.parametrize("q", ["หลงป่าในเกมไม่รู้ทางไป", "ตอนเด็กเคยหลงป่ากับพ่อ สนุกดี", "หลงเสน่ห์ทะเลมาก"])
def test_story_and_idiom_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
