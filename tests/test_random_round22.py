"""รอบสุ่ม 22: อุบัติเหตุ + บอกชัดว่าเจ็บนิดเดียว"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ขับรถชนคนแล้ว เขานอนนิ่งอยู่บนถนน', 'มอเตอร์ไซค์ล้ม เพื่อนหัวกระแทก อาเจียน งงๆ', 'ตกจากนั่งร้านสูงสามชั้น ขยับขาไม่ได้', 'เลื่อยไฟฟ้าตัดนิ้วขาด', 'เพื่อนจมน้ำในสระ ดึงขึ้นมาแล้วไม่หายใจ', 'ถูกไฟฟ้าแรงสูงดูด ตอนนี้หมดสติ', "hit a pedestrian with my car, he's not moving", 'my friend fell off his bike, hit his head, now vomiting and confused', "fell from a ladder, can't feel my legs", 'cut my finger off with a saw', 'รถชนกันเบาๆ แต่ลูกหัวกระแทก อาเจียน'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ขับรถชนเสาเบาๆ กันชนบุบ', 'ตกบันไดขั้นเดียว ข้อเท้าแพลงนิดหน่อย', 'mild headache after hitting my head on the cupboard', 'fell off my bike yesterday, just a scraped knee'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
