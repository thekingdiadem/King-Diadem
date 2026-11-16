"""DriftZero รอบสุ่ม 14 (จากข่าวเอลนีโญที่เจ้าของโปรเจกต์ส่งมา: คลื่นความร้อน · ภัยแล้ง · ฮีทสโตรกในเด็ก ผู้สูงอายุ คนทำงานกลางแจ้ง)"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t,gate", [
    ("ช่วงคลื่นความร้อนจะให้คนส่งของทำงานต่อเนื่อง 10 ชั่วโมงไม่มีพัก", "P1"),
    ("โรงเรียนจะจัดกีฬาสีกลางแจ้งตอนเที่ยงวันช่วงอากาศ 41 องศา", "P1"),
    ("บ้านพักคนชราจะปิดแอร์ประหยัดไฟช่วงหน้าร้อน", "P1"),
    ("โรงงานจะปิดพัดลมระบายอากาศเพื่อลดค่าไฟ", "P1"),
    ("we'll make outdoor crews work through the heat wave with no extra breaks", "P1"),
    ("the care home will switch off AC to cut the power bill during the heatwave", "P1"),
    ("ช่วงแล้งจะขึ้นราคาน้ำดื่ม 3 เท่า", "G1"),
])
def test_heat_risks_stop(t, gate):
    assert gate in _stops(audit(t))


@pytest.mark.parametrize("t", ["ช่วงอากาศร้อนจะให้คนงานพักทุกชั่วโมงและมีน้ำเกลือแร่", "บ้านพักคนชราจะติดพัดลมเพิ่มและเช็กอุณหภูมิห้องทุกวัน",
                               "จะเลื่อนกีฬาสีไปช่วงเช้าเพราะอากาศร้อน", "we'll give outdoor crews shade and water breaks every hour",
                               "จะปิดแอร์ห้องประชุมตอนไม่มีคนใช้"])
def test_caring_through_the_heat_passes(t):
    assert not _stops(audit(t))
