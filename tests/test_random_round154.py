"""รอบสุ่ม 154: คนใกล้ตัวพูดบอกลาแบบอ้อม"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "เพื่อนพูดว่าจะไม่อยู่ให้เห็นหน้าแล้ว", "my friend said I won't have to worry about him anymore",
    "my sister said soon she won't be a burden to anyone", "my friend said he won't be around after this week",
])
def test_veiled_goodbye_from_someone_close_is_heard(q):
    a = assess(q)
    assert a["risk_shown"] >= 60 and "someone" in a["topics"]


@pytest.mark.parametrize("q", [
    "my friend said I won't have to worry about him anymore because he's moving abroad for college",
    "เพื่อนบอกว่าจะไม่อยู่ให้เห็นหน้าแล้ว เพราะย้ายไปทำงานต่างประเทศ",
])
def test_moving_away_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
