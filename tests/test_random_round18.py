"""รอบสุ่ม 18: สัญญาณค้ามนุษย์ / บังคับใช้แรงงาน-ค้าประเวณี"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["แฟนบังคับให้ไปขายตัวใช้หนี้", "เจ้านายไม่จ่ายเงิน ยึดบัตรประชาชนไว้", "they lock us in the dorm at night and take our phones",
                               "นายหน้ายึดพาสปอร์ตไว้ ไม่ให้กลับบ้าน", "my boss took my passport and won't let me leave"])
def test_trafficking_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ["ยึดบัตรประชาชนไว้ตอนเช็คอินโรงแรม", "แฟนบังคับให้ไปกินข้าวกับที่บ้าน", "นายหน้าขายบ้านโทรมาถามความคืบหน้า",
                               "my boss took my idea in the meeting", "lost a bit on crypto this week"])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
