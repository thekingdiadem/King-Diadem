"""DriftZero รอบสุ่ม 15: คนที่กำลังจะโดนหลอก พิมพ์มาเป็น "การตัดสินใจ" — ด่าน F1 สัญญาณมิจฉาชีพ"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


SCAM = ["จะโอนเงิน 5 แสนลงทุนกับคนในไลน์ที่บอกว่าได้ผลตอบแทน 30% ต่อเดือน", "มีคนชวนลงทุนคริปโต การันตีกำไรวันละ 2% จะเอาเงินเก็บทั้งหมดไปลง",
        "บริษัทจะโอนเงินให้ซัพพลายเออร์ตามอีเมลที่บอกว่าเปลี่ยนเลขบัญชีใหม่", "เจ้าหน้าที่ธนาคารโทรมาให้ย้ายเงินไปบัญชีปลอดภัย จะทำตามดี",
        "we got an email from the CEO asking to wire 40k urgently to a new vendor", "someone on telegram offers 5% daily returns, I'll put my savings in",
        "จะสมัครงานออนไลน์ที่ให้โอนค่าประกันก่อน 3,000 บาท"]


@pytest.mark.parametrize("t", SCAM)
def test_scam_shaped_decisions_stop_at_f1(t):
    a = audit(t)
    assert "F1" in _stops(a)
    why = next(g for g in a["gates"] if g["id"] == "F1")["why"]["th"]
    assert "1441" in why


@pytest.mark.parametrize("t", ["จะลงทุนกองทุนรวมผ่านแอปธนาคารเดือนละ 5,000", "จะโทรกลับเบอร์ทางการของซัพพลายเออร์ก่อนเปลี่ยนเลขบัญชี",
                               "ร้านเราได้กำไร 12% ต่อปี"])
def test_normal_money_moves_pass(t):
    assert "F1" not in _stops(audit(t))
