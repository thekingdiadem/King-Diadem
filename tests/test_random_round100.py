"""รอบสุ่ม 100: ถูกจับตัวซ้ำๆ โดยคนที่มีอำนาจ · ไฟดูดจนไหม้ · ชักนาน — และการแตะตัวที่ปกติ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q,topic", [("โดนเพื่อนร่วมงานลูบขาทุกวัน", "sexual_abuse"), ("teacher keeps touching my leg", "sexual_abuse"),
                                     ("น้องเล่นปลั๊กไฟ ตอนนี้มือดำไหม้", "health_emergency"), ("พ่อโดนไฟช็อตแล้วหมดสติ", "health_emergency"),
                                     ("my mom is seizing for 5 minutes", "health_emergency")])
def test_missed_before_now_urgent(q, topic):
    a = assess(q)
    assert a["risk_shown"] >= 80 and topic in a["topics"]


@pytest.mark.parametrize("q", ["พ่อเลี้ยงจับตัวหนู", "ลุงลูบขาหนู", "ครูจับหน้าอก", "น้าจับก้นหนูตอนไม่มีใคร"])
def test_abuse_still_caught(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["หัวหน้าจับไหล่ให้กำลังใจ", "หัวหน้าจับมือแสดงความยินดี", "โค้ชจับขาตอนยืดเส้น",
                               "เสียบปลั๊กแล้วไฟดับทั้งบ้าน"])
def test_everyday_touch_and_plugs_are_calm(q):
    # "หัวหน้า" เคยถูกอ่านเป็น "น้า" + จับ ได้ 85
    assert assess(q)["risk_shown"] < 60
