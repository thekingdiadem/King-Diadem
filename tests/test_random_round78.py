"""รอบสุ่ม 78: ติดค้างระหว่างเดินทาง + ลูกหายในที่คนเยอะ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['หลงป่าบนดอย มืดแล้ว แบตเหลือ 5% น้ำหมด', 'เรือเครื่องดับกลางทะเล คลื่นแรง เริ่มมีน้ำเข้า', 'รถเสียกลางทาง ไม่มีสัญญาณ หนาวมาก มีเด็กเล็กอยู่ด้วย', 'ลูกหายในห้างคนเยอะ หาครึ่งชั่วโมงแล้ว', "lost on the mountain, it's dark, phone at 5% and no water", 'boat engine died at sea, big waves, water coming in', 'car broke down, no signal, freezing, I have a toddler with me', 'lost my kid in a crowded mall 30 minutes ago'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['เดินป่าสนุกมาก วิวสวย', 'นั่งเรือเที่ยวเกาะ', 'รถเสีย รอช่างอยู่ในปั๊ม', 'hiking was great, beautiful view', 'waiting for a tow truck at the gas station'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
