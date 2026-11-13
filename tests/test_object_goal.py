"""ปริศนาล้างรถ 100 เมตร (core/object_goal.py) — ของที่เป้าหมายต้องใช้ ต้องไปด้วย
บทเรียนจากเจ้าของโปรเจกต์: AI ที่ดูแค่ตัวเลขตอบ "เดินไป ประหยัดพลังงาน" ทั้งที่งานคือล้างรถ
ระบบเดิมก็ตก: ได้ "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน" ทั้งล้างรถ ซ่อมตู้เย็น และพาหมาไปฉีดวัคซีน"""
import pytest

from core.kernel_voice import compose
from core.object_goal import check


@pytest.mark.parametrize("text,kind", [
    ("จะเอารถไปล้างที่ร้านห่างไป 100 เมตร ควรเดินไปหรือขับรถไป", "vehicle"),
    ("ร้านล้างรถอยู่ห่างแค่ 100 เมตร เอารถไปล้าง เดินไปดีไหม", "vehicle"),
    ("จะเอามอไซค์ไปเปลี่ยนยาง ร้านอยู่ปากซอย เดินไปได้ไหม", "vehicle"),
    ("I want to wash my car at a place 100m away, should I walk or drive?", "vehicle"),
    ("จะเอาหมาไปฉีดวัคซีนที่คลินิกใกล้บ้าน เดินไปเองได้ไหม", "pet"),
    ("จะเอาตู้เย็นไปซ่อมที่ร้านห่าง 200 เมตร เดินไปดีไหม", "heavy"),
    ("เอามือถือไปซ่อมจอ ร้านอยู่ปากซอย เดินไปได้ไหม", "small"),
])
def test_reads_what_must_travel(text, kind):
    assert check(text)[0] == kind


def test_car_must_go_and_choice_is_kept():
    r = compose("จะเอารถไปล้างที่ร้านห่างไป 100 เมตร ควรเดินไปหรือขับรถไป")
    assert "รถต้องไปถึงร้านด้วย" in r and "1) " in r and "2) " in r and "3) " in r    # คืนทางเลือก ไม่ใช่สั่งทางเดียว
    assert "ประหยัดพลังงาน" not in r


def test_each_kind_gets_a_different_truth():
    assert "เดินไปได้ ถ้าพาน้องไปด้วย" in compose("จะเอาหมาไปฉีดวัคซีนที่คลินิกใกล้บ้าน เดินไปเองได้ไหม")
    assert "เดินถือไปไม่ได้" in compose("จะเอาตู้เย็นไปซ่อมที่ร้านห่าง 200 เมตร เดินไปดีไหม")
    assert "ต้องเอาติดตัวไปด้วย" in compose("เอามือถือไปซ่อมจอ ร้านอยู่ปากซอย เดินไปได้ไหม")


@pytest.mark.parametrize("text", ["ร้านกาแฟห่าง 100 เมตร เดินไปดีไหม", "รถชนกันเล็กน้อย คู่กรณีไม่ยอมจ่าย", "อยากซื้อรถใหม่ดีไหม"])
def test_no_object_to_carry_is_left_alone(text):
    assert check(text) is None


def test_crisis_still_comes_first():
    assert "1323" in compose("อยากตาย จะเอารถไปล้างเดินไปดีไหม")


def test_ai_learns_object_goal_and_memory_of_intent():
    import core.llm_gemini as L
    for name in ("LYLA_SYSTEM", "VEGA_SYSTEM", "COUNCIL_SYSTEM"):
        p = getattr(L, name)
        assert "ของที่เป้าหมายต้องใช้ต้องไปด้วย" in p and "จำเป้าหมายแรกของผู้ใช้ตลอดบทสนทนา" in p, name
