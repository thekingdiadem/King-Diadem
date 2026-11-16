"""DriftZero รอบสุ่ม 21: ความปลอดภัยบนถนน — เดิมผ่านทุกด่านทั้ง 7 แบบ"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t", ["บริษัทขนส่งจะให้คนขับรถทัวร์ขับต่อเนื่อง 14 ชั่วโมงไม่มีคนสลับ", "จะให้คนขับรถบรรทุกกินยาแก้ง่วงขับกลางคืน",
                               "จะวิ่งรถบรรทุกน้ำหนักเกินเพื่อประหยัดเที่ยว", "จะเลื่อนเปลี่ยนเบรกรถตู้ออกไปอีก 3 เดือนทั้งที่เบรกดังแล้ว",
                               "we'll let drivers skip rest breaks to meet delivery targets",
                               "the company will keep the bus running even though the brakes failed inspection",
                               "ไรเดอร์จะได้โบนัสถ้าส่งเร็วกว่า 10 นาที"])
def test_road_risks_stop(t):
    assert "P1" in _stops(audit(t))


@pytest.mark.parametrize("t", ["จะให้คนขับพักทุก 4 ชั่วโมงและมีคนสลับ", "จะเปลี่ยนเบรกรถตู้ทันทีที่เบรกดัง",
                               "จะตรวจน้ำหนักรถบรรทุกไม่ให้เกินทุกเที่ยว"])
def test_safe_driving_policy_passes(t):
    assert not _stops(audit(t))
