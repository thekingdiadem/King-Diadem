"""รอบสุ่ม 109: ไฟไหม้ใกล้ๆ แล้วควันเข้าห้อง ต้องเป็นเหตุฉุกเฉินเต็มที่"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["ไฟไหม้ห้องข้างๆ ควันเข้าห้องแล้ว", "ไฟไหม้ชั้นล่าง ควันลอดใต้ประตูขึ้นมา",
                               "there's smoke coming under my door, fire in the hallway"])
def test_smoke_entering_is_urgent(q):
    # "ไฟไหม้ห้องข้างๆ ควันเข้าห้องแล้ว" เคยได้ 64
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ควันธูปเข้าห้อง", "ไฟดับทั้งซอย"])
def test_everyday_smoke_is_calm(q):
    assert assess(q)["risk_shown"] < 60
