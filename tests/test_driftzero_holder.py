"""ด่าน H1 "คนทำต้องอยู่รอดด้วย" — จากแกนคุ้มครองผู้ถือระบบของเจ้าของโปรเจกต์:
ระบบที่ปกป้องทุกชีวิตแต่ทำลายผู้ถือมัน ถือว่ายังไม่สมบูรณ์ · ดีพอให้รอด สำคัญกว่าดีสุดจนพัง
"""
import pytest

from ENGINE.driftzero import audit, follow_up


def _stops(r):
    return [g["id"] for g in r["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("text", [
    "ผมจะลาออกมาทำเต็มตัว ใช้เงินเก็บทั้งหมดเปิดร้าน",
    "I will put my life savings into the startup and work for free for a year",
    "ทีมจะทำงานไม่หยุดจนกว่าจะส่งงาน ไม่รับเงินเดือนสามเดือน",
])
def test_plans_that_spend_the_makers_survival_minimum_are_stopped(text):
    r = audit(text)
    assert "H1" in _stops(r) and r["verdict"] == "stop"
    g = next(x for x in r["gates"] if x["id"] == "H1")
    assert "กันส่วนที่ต้องใช้กินอยู่ไว้ก่อน" in g["why"]["th"] and "set aside what you need to live on first" in g["why"]["en"]


@pytest.mark.parametrize("text", [
    "spend 10k on facebook ads",
    "บริษัทจะขยายสาขา ใช้งบ 20 ล้าน ภายในปีนี้",
    "we will hire 5 unpaid interns",
])
def test_ordinary_business_decisions_are_not_stopped(text):
    assert "H1" not in _stops(audit(text))


def test_a_stated_worst_case_is_not_the_plan():
    """ตอบข้อ "ถ้าพลาดจะเสียอะไร" ว่าจ่ายค่าเช่าไม่ไหว = ผลเสียสมมติ ไม่ใช่แผน — ไม่โดนหยุดเพราะตอบตรงๆ"""
    a = audit("spend 10k on facebook ads")
    r = follow_up(a["text"], [q["key"] for q in a["asks"]], "1 i do it 2. i can't pay rent 3 1k")
    assert "worst case: i can't pay rent" in r["text"] and "H1" not in _stops(r)
    # แต่ถ้าเขียนไว้ในแผนเอง ยังโดนหยุด
    assert "H1" in _stops(audit("I can't pay rent this month but I will spend 10k on facebook ads"))
