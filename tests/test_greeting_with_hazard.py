"""ทักทายพ่วงเรื่องอันตราย เช่น "แผ่นดินไหว สวัสดี" เคยได้แค่คำทักทาย ไม่มีทางไปต่อ"""
import pytest

from core.kernel_voice import compose


@pytest.mark.parametrize("t", ["แผ่นดินไหว สวัสดี", "สวัสดี แผ่นดินไหว"])
def test_hazard_beats_greeting(t):
    out = compose(t)
    assert "เล่าเรื่องที่กำลังตัดสินใจ" not in out and "1)" in out, out


def test_plain_greeting_still_greets():
    assert "เล่าเรื่องที่กำลังตัดสินใจ" in compose("สวัสดีค่ะ")
