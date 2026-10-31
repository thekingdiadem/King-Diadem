"""หลอกซ้ำ (recovery scam) — คนที่เพิ่งโดนโกงถูกทักว่า "ช่วยตามเงินคืนได้ แต่ต้องจ่ายก่อน"

เดิม "มีทนายติดต่อมาว่าจะช่วยเอาเงินคืน ขอค่าธรรมเนียมก่อน" ได้ Risk 0 และคำตอบทั่วไป
ไลล่า (One-Line Audit Truth): อ้างเป็นแฮกเกอร์/ผู้ช่วยตามเงินคืน = recovery scam 100%"""
import pytest

from core.kernel_voice import compose, compose_council
from core.thai_signals import scam_flags

RECOVERY = [
    "มีคนทักมาบอกว่าเป็นแฮกเกอร์สายขาว ช่วยตามเงินที่โดนโกงคืนได้ แต่ต้องจ่ายค่าดำเนินการก่อน 5000",
    "มีทนายติดต่อมาว่าจะช่วยเอาเงินคืนจากแก๊งคอลเซ็นเตอร์ให้ ขอค่าธรรมเนียมก่อน",
    "เพจรับตามเงินคืน บอกว่าได้คืน 100% ต้องโอนค่ามัดจำ",
    "someone says they are a recovery agent and can get my scammed crypto back for a fee",
    "a fund recovery company contacted me, they want an upfront payment to retrieve my lost money",
]
NOT_RECOVERY = [
    "อยากได้เงินคืนจากร้านที่ส่งของผิด",
    "ยืมเงินเพื่อนไป จะทวงคืนยังไงดี",
    "โดนแก๊งคอลเซ็นเตอร์หลอกโอนไป 20000",
    "how do I get a refund for a broken phone",
]


@pytest.mark.parametrize("t", RECOVERY)
def test_recovery_offer_is_flagged(t):
    assert "recovery" in scam_flags(t)


@pytest.mark.parametrize("t", NOT_RECOVERY)
def test_ordinary_refunds_and_first_scam_are_not_recovery(t):
    assert "recovery" not in scam_flags(t)


@pytest.mark.parametrize("t", RECOVERY)
def test_answer_says_stop_and_gives_free_real_channels(t):
    for out in (compose(t), compose_council(t)):
        first = out.split("\n", 1)[0]
        assert ("หยุด" in first or "Stop" in first), first
        assert "1441" in out
        assert "ไม่จ่าย" in out or "Don't pay" in out          # บอกตรงๆ ว่าอย่าจ่าย
