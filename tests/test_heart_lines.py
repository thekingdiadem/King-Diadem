"""คำตอบที่ได้ใจ — ตอบความรู้สึกที่ผู้ใช้เล่า ไม่ใช่แค่ขั้นตอน (core/heart_lines.py)
หลัก: เราไม่ได้ต้องการคำตอบที่สมบูรณ์แบบ เราแค่ต้องการรู้ว่ายังมีทางเลือกอยู่"""
import pytest
from core.kernel_voice import compose


@pytest.mark.parametrize("q,must", [
    ("โดนหลอกโอนเงินไปหมดตัว รู้สึกโง่มาก", ["เขาเก่งเรื่องโกหก", "ยังมีทางเลือก", "1323"]),
    ("แฟนทุบหนูอีกแล้ว ไม่รู้จะไปไหน", ["ไม่ได้แปลว่าไม่มีทางเลือก", "1300", "ไม่ใช่ความผิดของคุณ"]),
    ("I lost all my savings to a scam and I'm so ashamed", ["skilled liars", "still have choices"]),
    ("my husband hit me again and I have nowhere to go", ["doesn't mean having no options", "not your fault"]),
])
def test_reply_answers_the_feeling(q, must):
    r = compose(q)
    for m in must:
        assert m in r, (m, r)
    assert r.count("\n") < 40


@pytest.mark.parametrize("q", ["มีคนอ้างเป็นตำรวจให้โอนเงิน", "อยากตาย", "สามีตบหนู"])
def test_no_extra_lines_when_feeling_not_said(q):
    r = compose(q)
    assert "เขาเก่งเรื่องโกหก" not in r and "ไม่ได้แปลว่าไม่มีทางเลือก" not in r
