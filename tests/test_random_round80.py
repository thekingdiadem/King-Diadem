"""รอบสุ่ม 80: ล่อลวงเด็กไปโรงแรม · งานต่างประเทศจากเฟซ · แม่ถูกหลอกว่าเป็นลูก"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ลูกเล่นมือถือแล้วบอกว่ามีคนในแชทให้ไปเจอที่โรงแรมคืนนี้ บอกห้ามบอกแม่', 'น้องสาวได้งานต่างประเทศจากเฟซ เงินเดือนสูงมาก ต้องไปพรุ่งนี้ นายหน้าเก็บพาสปอร์ต', 'my daughter says someone from a chat wants to meet her at a hotel tonight and told her not to tell me', 'my sister got a job abroad from facebook, huge salary, leaving tomorrow, the agent took her passport'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


def test_parent_tricked_by_fake_child_is_scam():
    a = assess("แม่เชื่อคนในไลน์ว่าเป็นลูกชาย กำลังจะโอนเงินแสน")
    assert (a.get("scam") or "scam" in a["topics"]) and a["risk_shown"] >= 60


@pytest.mark.parametrize("q", ['ลูกไปค่ายโรงเรียน ครูดูแล', 'น้องได้งานต่างประเทศผ่านบริษัทจัดหางานที่ขึ้นทะเบียน', 'my daughter is meeting her school friends at the mall'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
