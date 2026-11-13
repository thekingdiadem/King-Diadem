"""ถูกทำร้าย/ขู่ ภาษาอังกฤษ — พบจากการทดสอบ PR #193: "how do I make my bf stop hitting me" ได้ Risk 0 และแผน 3 ขั้นทั่วไป
ตัวจับเดิมรู้แค่รูป "hits me" ไม่รู้รูป -ing คำขู่ และ "กลัวสามี" · ระบบห้ามประมาท: ประโยคที่ดูธรรมดาอาจมาจากคนที่อยู่ในอันตราย"""
import pytest

from core.kernel_voice import assess, compose

VICTIM = ["how do I make my bf stop hitting me", "he keeps hitting me", "she threatens to kill me", "i'm scared of my husband",
          "my dad won't stop beating me", "my ex threatened to hurt my kids", "my partner is choking me when he drinks",
          "my stepdad keeps hurting me"]
NOT_VIOLENCE = ["he hit a home run", "this song keeps hitting me", "my friend keeps hitting me up for money",
                "i'm afraid of my dad finding out my grades", "the boss is killing me with deadlines",
                "he is hurting inside and i want to help", "my brother is kicking me out of the game",
                "scared of my ex seeing me happy"]


@pytest.mark.parametrize("text", VICTIM)
def test_victim_gets_the_safety_reply(text):
    a = assess(text)
    assert "violence" in a["topics"] and a["text_risk"] >= 80, a
    r = compose(text)
    assert r.startswith("Your safety comes first."), r[:80]
    assert "emergency number" in r and "Anger this strong" not in r      # คนที่ถูกขู่ไม่ใช่คนที่โกรธอยากทำร้ายใคร


@pytest.mark.parametrize("text", NOT_VIOLENCE)
def test_everyday_sentences_are_not_flagged(text):
    assert "violence" not in assess(text)["topics"], text
