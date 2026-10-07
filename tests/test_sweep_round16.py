"""รอบหาบั๊ก 16: แผนฆ่าตัวตาย · ภาระ/คนอื่นจะดีกว่าถ้าไม่มีฉัน · เสียงสั่ง · การกิน · ท้องแล้วแฟนหนี · ถูกเมิน"""
from core.kernel_voice import assess


def test_suicide_plan_is_crisis():
    for t in ("I have a plan to end it", "วางแผนจะฆ่าตัวตาย"):
        assert assess(t)["crisis"], t
    assert not assess("วางแผนเที่ยว")["crisis"]


def test_burden_and_better_off_without_me_are_warnings():
    for t in ("everyone would be better off without me", "I am a burden", "ถ้าไม่มีฉันทุกคนคงสบาย"):
        assert assess(t)["risk"] >= 65, t
    assert assess("ถ้าไม่มีผมงานคงไม่เสร็จ")["risk"] < 60


def test_command_voices_are_psychosis_not_witness():
    a = assess("ได้ยินเสียงคนสั่งให้ทำร้าย")
    assert "psychosis" in a["topics"] and "witness" not in a["topics"]
    assert "witness" in assess("ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง")["topics"]
    assert "psychosis" in assess("I hear voices")["topics"]


def test_misc():
    assert "eating" in assess("อ้วกหลังกินทุกครั้ง")["topics"]
    assert "pregnancy" in assess("ท้องแล้วแฟนหนี")["topics"]
    assert "bullying" in assess("โดนเพื่อนแบน")["topics"]
