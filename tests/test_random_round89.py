"""รอบสุ่ม 89: แรงงานข้ามชาติ/ประมงถูกบังคับ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ไปทำงานเกาหลีผิดกฎหมาย นายจ้างไม่จ่ายเงิน ขู่จะแจ้งตำรวจจับ ไม่มีที่ไป', 'แรงงานพม่าในโรงงาน ถูกล็อกห้อง ไฟไหม้ ออกไม่ได้', 'คนงานประมง ถูกบังคับทำงานบนเรือ ไม่ได้ขึ้นฝั่งสามเดือน ถูกตี', "undocumented worker, boss won't pay, threatens to call immigration, nowhere to go", "fishing crew forced to work on the boat, haven't been ashore in 3 months, they beat us"])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ไปทำงานเกาหลีถูกกฎหมาย ได้วีซ่าแล้ว', 'คนงานประมงได้หยุดพักสัปดาห์ละวัน', 'working abroad legally, got my visa'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
