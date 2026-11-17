"""รอบสุ่ม 139: กินยาละลายลิ่มเลือดแล้วหัวกระแทก"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["แม่ทานยาละลายลิ่มเลือด ล้มหัวกระแทก", "my mom is on blood thinners and hit her head", "พ่อกินวาร์ฟาริน หัวโขกโต๊ะ"])
def test_head_bump_on_thinners_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


def test_thinners_alone_stay_calm():
    assert assess("แม่ทานยาละลายลิ่มเลือดตามหมอสั่ง ไม่มีอาการ")["risk_shown"] < 60
