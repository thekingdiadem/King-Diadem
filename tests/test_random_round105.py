"""รอบสุ่ม 105: ถูกบังคับแต่งงาน · คู่ขู่ฆ่าตัวตายถ้าเลิก (อังกฤษ) · "เช็คมือถือให้หน่อย" ไม่ใช่การควบคุม"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["ถูกบังคับแต่งงานกับคนที่ไม่รู้จัก", "my parents are forcing me to marry a stranger",
                               "i'm being forced into a marriage", "he says he'll kill himself if i leave"])
def test_missed_before_now_urgent(q):
    # ทุกข้อเคยได้ 0
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["แฟนเช็คมือถือให้หน่อยว่าเสียไหม", "แต่งงานเดือนหน้า ตื่นเต้นมาก", "พ่อแม่บังคับให้กินผัก 555",
                               "the movie is about a forced marriage"])
def test_everyday_is_calm(q):
    assert assess(q)["risk_shown"] < 60


def test_real_phone_control_still_flagged():
    assert assess("แฟนเช็คมือถือทุกวัน ห้ามคุยกับเพื่อน")["risk_shown"] >= 60
