"""รอบสุ่ม 214 (อังกฤษ): อันตรายที่เล่าแบบบรรยาย ไม่มีคำแรง — เคยได้ 0 · ชมรมยิงปืนไม่ใช่เหตุยิงกราด"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q,floor", [
    ("her boyfriend checks her messages and won't let her meet her family", 65),
    ("an unknown man is hiding in our shed", 80),
    ("my uncle is drunk and waving a knife around", 80),
    ("my brother kept saying his family would be better off without him", 80),
    ("a caller claims they kidnapped my daughter and wants bitcoin", 60),
    ("my newborn's fontanelle looks sunken", 80),
    ("dad is pale and trembling since his insulin this morning", 80),
    ("we're trapped on the roof and the water keeps coming", 80),
])
def test_described_danger_is_urgent(q, floor):
    assert assess(q)["risk_shown"] >= floor


def test_threat_after_shooting_club_stays_urgent():
    assert assess("he joined a shooting club and now says he'll shoot people at school")["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "my daughter wants to join the archery club", "we went to the gun range today, it was fun",
    "her boyfriend helped her move apartments", "a stray cat sleeps in our garage", "my dad is cutting the grass with a machete",
    "someone keeps calling about my car's extended warranty", "we're on the roof watching fireworks",
])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
