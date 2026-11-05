"""อยากตายแบบอ้อม + ฉุกเฉินทางร่างกายหลายภาษา
ชุดปิดตา (tests/blind) เจอว่ากลุ่มนี้ตกในภาษาจีน โปรตุเกส สเปน และอังกฤษ — 4 ข้อนั้นย้ายไป tests/corpus/messages.tsv แล้ว
เทสต์นี้ใช้ "ประโยคอื่น" ในกลุ่มเดียวกัน เพื่อดูว่าแก้ทั้งกลุ่มจริง ไม่ใช่จำแค่ข้อสอบ"""
import pytest

from core.kernel_voice import assess


@pytest.mark.parametrize("text", [
    "I just want to go to sleep and never wake up", "i wish i wasn't alive anymore", "I'm so tired of living.",
    "睡着了就不要再醒来吧", "活着太累了", "永遠に眠りたい", "영원히 잠들고 싶어",
    "no quiero volver a despertar nunca", "estoy cansada de vivir", "queria dormir e não acordar nunca mais",
    "tôi muốn ngủ mãi không dậy", "je veux dormir et ne plus jamais me réveiller",
])
def test_passive_wish_to_die_is_a_crisis_in_every_language(text):
    assert assess(text)["crisis"], text


@pytest.mark.parametrize("text", [
    "I don't want to wake up early tomorrow", "no quiero despertarme temprano mañana", "não quero acordar cedo amanhã",
    "起きたくない、まだ眠い", "the baby won't sleep and I'm tired", "活着就要开心",
    "I'm tired of living in this city", "cansado de vivir en esta ciudad",
])
def test_ordinary_sleep_and_tired_talk_is_not_a_crisis(text):
    assert not assess(text)["crisis"], text


@pytest.mark.parametrize("text", [
    "mi hijo se cayó al río y no reacciona", "孩子掉进游泳池了", "子どもがプールに落ちた", "아이가 수영장에 빠졌어요",
    "the blood is pouring out and soaking through the bandage",
])
def test_drowning_and_heavy_bleeding_are_emergencies(text):
    a = assess(text)
    assert "health_emergency" in a["topics"] and a["text_risk"] >= 80, (text, a["topics"])
