"""สำนวนความคิดอยากตายภาษาอังกฤษ — ตาราง 3,850 ข้อความเคยหลุด 1,529"""
import pytest

from core.kernel_voice import assess


@pytest.mark.parametrize("text", ["I'm done with life", "there's no point in living", "life isn't worth it anymore", "I bought pills to end it"])
def test_crisis_idioms(text):
    assert assess(text)["crisis"]


@pytest.mark.parametrize("text", ["I can't keep living like this", "I don't want to wake up tomorrow", "I just want it all to stop",
                                  "I'm saying goodbye to everyone", "I'm going to jump"])
def test_warning_idioms(text):
    assert assess(text)["text_risk"] >= 65


@pytest.mark.parametrize("text", ["I'm done with life drawing class", "I just want it all to stop raining", "I'm going to jump into the pool",
                                  "I'm saying goodbye to everyone at the office party", "I'm ready to go"])
def test_everyday_versions_stay_calm(text):
    a = assess(text)
    assert not a["crisis"] and a["text_risk"] < 60
