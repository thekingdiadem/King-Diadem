"""รอบหาบั๊ก 13: อยากทำร้ายคนอื่น · ลูกหาย · ผึ้งต่อย · ไม่มีบัตรทอง · แฟนทิ้ง (อังกฤษ)"""
from core.kernel_voice import assess, compose


def test_wanting_to_harm_others_gets_its_own_topic():
    for t in ("จะฆ่ามัน", "อยากฆ่าพ่อ", "อยากทำร้ายแฟน", "I want to hurt him"):
        a = assess(t)
        assert "harm_others" in a["topics"] and a["risk"] >= 80, t
    for t in ("ฆ่าเวลา", "จะฆ่ายุง", "ช่วยฆ่าเชื้อ", "อยากฆ่าตัวตาย"):
        assert "harm_others" not in assess(t)["topics"], t
    assert "1323" in compose("อยากฆ่าพ่อ", "risk")


def test_harm_others_reaches_llm_prompt():
    src = open("app.py", encoding="utf-8").read()
    assert '"harm_others" in k_topics' in src


def test_bare_missing_child():
    assert "missing" in assess("ลูกหาย")["topics"]
    assert "missing" not in assess("หมาหาย")["topics"]


def test_small_fixes():
    assert "first_aid" in assess("ผึ้งต่อย")["topics"]
    assert "first_aid" not in assess("ต่อไป")["topics"]
    assert "health_rights" in assess("ไม่มีบัตรทอง")["topics"]
    assert "relationship" in assess("my wife left me")["topics"]
