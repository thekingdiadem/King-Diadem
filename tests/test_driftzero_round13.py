"""DriftZero รอบสุ่ม 13 (จากข่าวที่เจ้าของโปรเจกต์ส่งมา: กากอุตสาหกรรมพิษภาคตะวันออก · สารหนูจากเหมืองในแม่น้ำ · ฝุ่น PM2.5)"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


HARM = ["โรงงานจะเอากากอุตสาหกรรมไปทิ้งที่บ่อร้างในปราจีนบุรีเพราะถูกกว่าส่งกำจัด", "จะจ้างรถมาขนขยะพิษไปเทในที่ดินว่างตอนกลางคืน",
        "เหมืองจะปล่อยน้ำจากบ่อแร่ลงแม่น้ำกกช่วงฝนตก", "ฟาร์มจะเผาตอซังข้าวทั้งแปลงช่วงฝุ่นเยอะ", "จะฝังสารเคมีที่ใช้แล้วในดินหลังโรงงาน",
        "we will dump the used solvent in the empty lot behind the plant",
        "the mine will release tailings water into the river during the rainy season",
        "we'll burn the plastic waste on site to save disposal costs"]
DONE_RIGHT = ["โรงงานจะส่งกากอุตสาหกรรมให้บริษัทกำจัดที่มีใบอนุญาต", "ฟาร์มจะไถกลบตอซังแทนการเผา",
              "จะติดเครื่องบำบัดน้ำเสียก่อนปล่อยลงคลอง"]


@pytest.mark.parametrize("t", HARM)
def test_poisoning_land_water_air_stops(t):
    assert {"E1", "E2"} & set(_stops(audit(t)))


@pytest.mark.parametrize("t", DONE_RIGHT)
def test_treated_or_licensed_disposal_passes(t):
    # "ติดเครื่องบำบัดน้ำเสียก่อนปล่อยลงคลอง" เคยโดนหยุดเพราะมีคำว่าน้ำเสียกับลงคลอง
    assert not _stops(audit(t))
