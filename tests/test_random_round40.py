"""รอบสุ่ม 40: ภาษาถิ่นแบบลึก + ไฟไหม้มีคนติดข้างใน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['อยากหลับแล้วบ่ตื่นอีกเลย', 'ผัวเมามาตีหัวข่อยเลือดออก', 'แม่ล้มหัวฟาด บ่ตื่นเลย', 'ข่อยกินยาหมดแผงแล้ว', 'บ่อยากอยู่แล้วเจ้า เบื่อหมดทุกอย่าง', 'ป้อเมาตี๋แม่ทุกคืน', 'อยากต๋ายแล้วหนิ เหนื่อยจังหู', 'ลูกตกน้ำ บ่หายใจ', 'ไฟไหม้เฮือน ป้อยังอยู่ข้างใน', 'house is on fire and my dad is still inside'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['บ่ไหวแล้ว อิ่มหลาย', 'อยากหลับยาวๆ วันเสาร์ บ่ต้องตื่นเช้า', 'ม่วนหลายเด้อ มื้อนี้', 'ป้อไปนาตั้งแต่เช้า'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
