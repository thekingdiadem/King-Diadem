"""รอบสุ่ม 137: เด็กตกแล้วอาเจียน · ท้องแข็งเป็นดาน (อังกฤษ) ต้องได้เท่าฉบับไทย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "baby fell off the bed and vomited twice", "my toddler hit his head and now he is very sleepy",
    "stomach is rock hard and the pain is unbearable", "ลูกเล็กตกเตียง หัวโน อาเจียน 2 ครั้ง",
])
def test_red_flags_are_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", ["baby fell asleep after vomiting milk a little, now fine", "my abs are rock hard after the gym, no pain"])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
