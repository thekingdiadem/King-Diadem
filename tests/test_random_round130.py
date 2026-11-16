"""รอบสุ่ม 130: มีคนงัดเข้าบ้าน ต้องได้คำแนะนำเรื่องผู้บุกรุก ไม่ใช่หัวข้อสุขภาพ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ประตูบ้านพัง มีคนงัดเข้ามา", "มีคนปีนหน้าต่างเข้ามาในบ้าน", "someone is trying to break in right now",
])
def test_break_in_gets_intruder_advice(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "intruder" in a["topics"]


@pytest.mark.parametrize("q", ["ประตูบ้านพัง ต้องเรียกช่าง", "เคยมีขโมยงัดเข้าบ้านเมื่อปีที่แล้ว", "door is broken need a locksmith"])
def test_repairs_and_old_stories_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
