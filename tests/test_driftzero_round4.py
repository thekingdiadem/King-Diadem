"""DriftZero รอบสุ่ม 4: แผนที่ซื่อตรงต้องไม่โดนหยุด — กันไม่ให้การเพิ่มด่านรอบหลังๆ หยุดคนดีโดยไม่ตั้งใจ"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


HONEST = ["we want to raise prices by 10% next month and tell customers in advance", "จะขึ้นเงินเดือนพนักงาน 5% ปีนี้",
          "จะจ้างพนักงานเพิ่ม 2 คน งบเดือนละ 3 หมื่น มีเงินสด 5 แสน ขั้นต่ำ 2 แสน ผู้จัดการอนุมัติ",
          "we will stop selling the product until the brake defect is fixed", "จะปิดร้านวันจันทร์ให้พนักงานได้พัก",
          "จะซื้อเครื่องชงกาแฟใหม่ 8 หมื่น ผ่อน 0% 10 เดือน", "จะเปิดให้ลูกค้าผ่อนจ่ายได้",
          "we will report the data breach to customers and regulators within 72 hours",
          "จะให้ AI ช่วยร่างอีเมลตอบลูกค้า แล้วพนักงานตรวจก่อนส่ง"]


@pytest.mark.parametrize("t", HONEST)
def test_honest_plans_are_not_stopped(t):
    assert not _stops(audit(t))


@pytest.mark.parametrize("t,gate", [("we'll invest our entire reserves into a new warehouse", "E2"),
                                    ("ผมจะทำงานไม่หยุดเลยทั้งเดือนเพื่อให้ทันส่งงาน", "H1")])
def test_real_risks_still_stop(t, gate):
    assert gate in _stops(audit(t))
