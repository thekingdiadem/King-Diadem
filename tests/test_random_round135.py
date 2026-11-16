"""รอบสุ่ม 135: แผลดำและมีกลิ่น (เนื้อตาย/ติดเชื้อรุนแรง)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "my dad's foot wound turned black and smells", "grandma's toe is black and oozing pus", "แผลที่ขาดำ มีกลิ่นเหม็น",
    "พ่อเป็นเบาหวาน แผลที่เท้าเน่าดำ มีกลิ่น",
])
def test_black_smelly_wound_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", ["my toe nail turned black after running, no pain", "แผลตกสะเก็ดสีดำ แห้งดี ไม่มีกลิ่น"])
def test_healing_scabs_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
