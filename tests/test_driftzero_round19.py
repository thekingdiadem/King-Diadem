"""DriftZero รอบสุ่ม 19: ความปลอดภัยของเด็กและผู้สูงอายุในองค์กร — เดิมผ่านทุกด่านทั้ง 8 แบบ"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t", ["เนอสเซอรี่จะให้พี่เลี้ยง 1 คนดูเด็ก 20 คน", "รถรับส่งนักเรียนจะไม่มีครูเช็กเด็กก่อนล็อกรถ",
                               "สถานรับเลี้ยงเด็กจะไม่ตรวจประวัติอาชญากรรมพนักงานใหม่",
                               "โรงเรียนจะให้ครูผู้ชายอยู่กับนักเรียนหญิงตามลำพังในห้องปิด",
                               "บ้านพักคนชราจะมัดผู้สูงอายุไว้กับเตียงเพราะคนไม่พอ",
                               "we'll let volunteers work with kids without background checks",
                               "the school bus won't do a final headcount before locking", "สระว่ายน้ำจะไม่มีไลฟ์การ์ดช่วงวันธรรมดา"])
def test_unsafe_care_of_children_and_elders_stops(t):
    assert "P1" in _stops(audit(t))


@pytest.mark.parametrize("t", ["เนอสเซอรี่จะเพิ่มพี่เลี้ยงให้ครบ 1 ต่อ 5", "รถรับส่งจะเดินเช็กทุกที่นั่งก่อนล็อกทุกครั้ง"])
def test_safe_care_passes(t):
    assert not _stops(audit(t))
