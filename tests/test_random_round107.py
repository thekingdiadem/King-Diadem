"""รอบสุ่ม 107: เด็กโดนเพื่อนรุมทุบ/รุมต่อยทุกวัน ต้องได้ความดูแลเท่ากับ "รุมกระทืบ" """
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["น้องโดนเพื่อนในห้องรุมทุบทุกวัน", "ลูกโดนรุ่นพี่รุมต่อยหลังเลิกเรียน", "โดนเด็กแว้นรุมเตะที่ป้ายรถเมล์"])
def test_group_beating_is_urgent(q):
    # "รุมทุบทุกวัน" เคยได้ 0 ขณะที่ "รุมกระทืบ" ได้ 85
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["เพื่อนรุมทุบหลังเล่นๆ ตอนวันเกิด", "โดนเพื่อนรุมแซวทั้งวัน"])
def test_playful_is_calm(q):
    assert assess(q)["risk_shown"] < 60
