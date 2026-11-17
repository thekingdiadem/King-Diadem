"""รอบสุ่ม 134: ล็อกประตูขังไว้ไม่ให้ออก"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "he locked the door and won't let me leave", "he locked the door and took my keys",
    "she locked the door and is screaming at me", "แฟนล็อกประตูไม่ให้ออก", "สามีล็อกประตูแล้วยึดมือถือ",
])
def test_locked_in_by_someone_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["he locked the door so the cat wouldn't get out", "แม่ล็อกประตูก่อนออกไปทำงาน", "my boss won't let me leave early today"])
def test_ordinary_locking_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
