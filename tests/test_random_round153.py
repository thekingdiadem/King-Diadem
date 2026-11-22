"""รอบสุ่ม 153: ผู้ใหญ่สั่งเด็กให้เก็บความลับจากพ่อแม่ — สัญญาณ grooming"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "my daughter says her coach told her to keep their secret from us", "ลูกบอกว่าครูที่โรงเรียนให้เก็บเป็นความลับ ห้ามบอกพ่อแม่",
    "my son's youth pastor gives him gifts and says not to tell us", "an older guy online told my 12yo to delete their chats",
])
def test_secrecy_from_parents_is_flagged(q):
    a = assess(q)
    assert a["risk_shown"] >= 75 and "online_grooming" in a["topics"]


@pytest.mark.parametrize("q", [
    "my coach told us to keep the surprise party a secret", "ครูให้ลูกเก็บเป็นความลับเรื่องเซอร์ไพรส์วันเกิดแม่",
    "my daughter's teacher said not to tell anyone the quiz answers",
])
def test_surprises_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
