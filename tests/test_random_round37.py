"""รอบสุ่ม 37: มิจฉาชีพ — ต้องเข้าหมวด scam (ระดับ 60 ขึ้นไป + บอกให้โทรธนาคาร/1441)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['โดนหลอกให้ลงทุนคริปโต เสียเงินห้าแสน เป็นเงินเก็บทั้งชีวิตของแม่', 'มีคนโทรมาอ้างเป็นตำรวจ บอกว่าบัญชีเราพัวพันยาเสพติด ให้โอนเงินไปตรวจสอบ', 'มีคนส่งลิงก์มาให้กดรับพัสดุ กดไปแล้วเงินในบัญชีหายหมด', 'แฟนในแอปหาคู่ขอยืมเงินค่ารักษาแม่ โอนไปแล้วสามแสน ตอนนี้บล็อกเรา', 'someone claiming to be police said my account is linked to drugs and I must transfer money to verify', 'clicked a parcel delivery link and now my bank account is empty', "my online boyfriend asked for money for his mom's surgery, I sent $10k and now he blocked me"])
def test_scam_recognised(q):
    a = assess(q)
    assert (a.get("scam") or "scam" in a["topics"]) and a["risk_shown"] >= 60


@pytest.mark.parametrize("q", ['ลงทุนกองทุนรวมเดือนละพัน', 'ตำรวจจราจรเรียกตรวจใบขับขี่', 'สั่งของออนไลน์ พัสดุมาถึงแล้ว', 'my bank called about my new card, I called back the number on the card'])
def test_everyday_calm(q):
    a = assess(q)
    assert not a.get("scam") and a["risk_shown"] < 60
