"""ปืนในบ้าน: เล่าเฉยๆ vs น่ากลัว · ไฟป่าใกล้หมู่บ้านต้องไม่ต่ำกว่าไฟป่าเฉยๆ"""
from core.kernel_voice import assess


def test_gun_mention_alone_is_not_alarming():
    a = assess("มีปืนอยู่ในบ้าน")
    assert "weapon" in a["topics"] and a["risk"] < 60


def test_gun_with_danger_context_is_high():
    for t in ("เจอปืนในบ้าน ไม่รู้ของใคร", "พ่อเมาแล้วมีปืน กลัวมาก", "อยากตาย ที่บ้านมีปืน"):
        assert assess(t)["risk"] >= 85, t


def test_toy_guns_and_idioms_are_not_weapons():
    for t in ("มีปืนฉีดน้ำ", "เจอปืนของเล่น", "มีระเบิดอารมณ์บ้าง"):
        assert "weapon" not in assess(t)["topics"], t


def test_weapon_reaches_llm_prompt():
    assert '"weapon" in k_topics' in open("app.py", encoding="utf-8").read()


def test_forest_fire_near_village_not_lower():
    base = assess("ไฟไหม้ป่า")["risk"]
    for t in ("ป่าไฟไหม้ใกล้หมู่บ้าน", "ไฟป่าลามมาใกล้บ้าน"):
        assert assess(t)["risk"] >= base, t
    assert assess("ข่าวไฟป่าที่แคลิฟอร์เนีย")["risk"] < base
