"""รอบหาบั๊ก 15: ข้อความลาตายของคนอื่น · จมน้ำ · ถูกข่มขู่ · คนหายออกจากบ้าน · ภาษาอังกฤษ"""
from core.kernel_voice import assess, compose


def test_goodbye_message_from_someone_else_is_crisis_not_grief():
    for t in ("เพื่อนส่งข้อความลาตาย", "my friend sent me a goodbye message"):
        a = assess(t)
        assert "someone" in a["topics"] and "grief" not in a["topics"] and a["risk"] >= 90, t
    assert "grief" in assess("เพื่อนตายแล้ว")["topics"]


def test_drowning_and_collapse_are_emergencies():
    for t in ("คนจมน้ำ", "my mom collapsed"):
        assert "health_emergency" in assess(t)["topics"], t


def test_threats_have_their_own_topic():
    for t in ("โดนข่มขู่", "มีคนโทรมาขู่", "someone is threatening me", "I got a threatening message"):
        a = assess(t)
        assert "threat" in a["topics"] and "sextortion" not in a["topics"], t
    assert "sextortion" in assess("he threatened to post my nudes")["topics"]
    assert "191" in compose("โดนข่มขู่", "risk")
    assert '"threat" in k_topics' in open("app.py", encoding="utf-8").read()


def test_misc():
    assert "missing" in assess("ลูกสาวหายออกจากบ้าน 2 วัน")["topics"]
    assert "sexual_abuse" in assess("I was sexually assaulted")["topics"]
    assert "labor" in assess("หัวหน้าไม่ให้ลา")["topics"]
    assert "stress" in assess("ไม่รู้จะทำอะไรกับชีวิต")["topics"]
