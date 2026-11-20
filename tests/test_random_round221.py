"""รอบสุ่ม 221: "i keep hurting myself" เคยได้ 0 (รูปแบบเขียน hurt+ting ซึ่งไม่ใช่คำจริง) · เล่าว่าคนอื่นกำลังกรีดตัวเอง
· คนขู่ฆ่าอยู่หน้าประตู (เคยได้ 65) · "took my passport photo" ไม่ใช่การยึดพาสปอร์ต"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["i keep hurting myself", "I've been harming myself again", "i'm burning myself with lighters", "i cut myself on purpose"])
def test_self_harm_in_any_tense_is_crisis(q):
    assert assess(q)["crisis"]


@pytest.mark.parametrize("q", [
    "my sister has been cutting herself and hides it", "my roommate is cutting herself in the bathroom and won't open the door",
    "someone is pounding on our door yelling he'll stab us", "my boyfriend took my passport and won't let me go home",
])
def test_danger_is_urgent(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "i hurt myself at the gym lifting", "I cut myself shaving this morning", "my roommate is cutting her hair in the bathroom",
    "my boyfriend took my passport photo for the visa", "there's a man outside selling ice cream",
])
def test_everyday_stays_calm(q):
    r = assess(q)
    assert r["risk_shown"] < 60 and not r["crisis"]
