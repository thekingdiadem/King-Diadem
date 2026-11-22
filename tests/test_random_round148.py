"""รอบสุ่ม 148: "passed out" ที่แปลว่าหลับเป็นตาย ไม่ใช่หมดสติ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "My dad passed out on the couch after the game, snoring loudly", "I passed out after my night shift lol",
])
def test_fell_asleep_is_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", [
    "My dad passed out and isn't responding", "she passed out at the mall", "he passed out on the couch and won't wake up",
    "my friend passed out on the bed after drinking a whole bottle of vodka",
])
def test_real_collapse_stays_urgent(q):
    assert assess(q)["risk_shown"] >= 80
