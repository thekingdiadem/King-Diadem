"""รอบสุ่ม 106: บังคับแต่งงานและควบคุมด้วยเงิน มีคำตอบเฉพาะของตัวเอง"""
import pytest
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("q", ["ถูกบังคับแต่งงานกับคนที่ไม่รู้จัก", "my parents are forcing me to marry a stranger"])
def test_forced_marriage_has_its_own_reply(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and a["topics"][0] == "forced_marriage"
    r = compose(q, footer=False)
    assert ("สิทธิ์ปฏิเสธ" in r or "right to refuse" in r) and "ถูกหลอกไป" not in r


def test_money_control_named_gently():
    a = assess("สามียึดเงินเดือนหมด ไม่ให้ใช้สักบาท")
    assert a["topics"][0] == "money_control" and 60 <= a["risk_shown"] < 80
    assert "1300" in compose("สามียึดเงินเดือนหมด ไม่ให้ใช้สักบาท", footer=False)


@pytest.mark.parametrize("q", ["สามีเก็บเงินเดือนไว้ลงทุนด้วยกัน", "แต่งงานเดือนหน้า ตื่นเต้นมาก"])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
