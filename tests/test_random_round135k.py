"""รอบสุ่ม 135: บัญชีม้า (ถูกจ้างให้เปิดบัญชี) · เงินถูกโอนออกจากบัญชีแม่ · ตำรวจมาให้ความรู้เรื่องมิจฉาชีพ ≠ ถูกหลอก"""
import pytest
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("t", ["มีคนให้รับจ้างเปิดบัญชีธนาคาร ได้เงิน 3,000",
                               "they offered me 3000 baht to open a bank account in my name for them"])
def test_money_mule_offer_is_named(t):
    a = assess(t)
    assert a["topics"][0] == "kp_money_mule" and a["risk_shown"] >= 60
    r = compose(t, footer=False)
    assert "บัญชีม้า" in r or "money laundering" in r


def test_money_taken_from_moms_account_gets_recovery_steps():
    a = assess("ตำรวจมาเตือนว่ามีคนโอนเงินออกจากบัญชีแม่ไปแล้ว")
    assert a.get("scam") == ["lost"] and a["risk_shown"] >= 60


@pytest.mark.parametrize("t", ["ตำรวจมาเตือนเรื่องมิจฉาชีพที่ชุมชน", "เปิดบัญชีธนาคารใหม่ให้ลูก", "โอนเงินออกจากบัญชีไปจ่ายค่าเทอมแล้ว"])
def test_awareness_and_ordinary_banking_are_calm(t):
    a = assess(t)
    assert a["risk_shown"] < 60 and not a.get("scam")
