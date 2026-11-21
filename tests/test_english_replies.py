"""ทุกหัวข้อต้องมีคำตอบภาษาอังกฤษ — เดิม 21 หัวข้อมีแต่ไทย ผู้ใช้อังกฤษเลยได้แค่ "Let's lay this out step by step"
(relationship · lonely มีคำตอบอังกฤษจากชั้นอื่นอยู่แล้ว)"""
import pytest
from core.kernel_voice import EN_TOPIC, TOPICS, compose

_ELSEWHERE = {"relationship", "lonely"}


def test_every_topic_has_an_english_reply():
    missing = [t[0] for t in TOPICS if t[0] not in EN_TOPIC and t[0] not in _ELSEWHERE]
    assert not missing, missing


@pytest.mark.parametrize("q", [
    "I'm so stressed about my exams", "my friend stopped talking to me", "I just got diagnosed with diabetes",
    "I'm drowning in credit card debt", "my parents fight every night", "I failed my exam", "I got promoted today!",
    "I'm so lonely, nobody ever texts me", "my girlfriend broke up with me",
])
def test_everyday_english_gets_a_specific_reply(q):
    assert not compose(q).startswith("Let's lay this out step by step")


def test_english_detection_keeps_danger_first():
    from core.kernel_voice import assess
    assert assess("I'm drowning in debt and want to die")["crisis"]
