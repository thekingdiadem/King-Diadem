"""ภัยภูมิอากาศแบบค่อยๆ มา — คลื่นความร้อน · ฝุ่น PM2.5 · ภัยแล้ง (ROADMAP Phase 4: Climate disruption)"""
import pytest
from core.engine_bridge import analyze, nearby
from core.kernel_voice import assess


@pytest.mark.parametrize("text, kind, must", [
    ("ร้อนจนเป็นลม ตอนนี้แม่ตัวร้อนมาก", "heat", "1669"),
    ("น่าจะเป็นฮีทสโตรก ลุงพูดไม่รู้เรื่อง", "heat", "อย่าป้อนน้ำ"),
    ("ค่าฝุ่น PM2.5 เกิน 200 ที่เชียงใหม่ ลูกไอไม่หยุด", "haze", "N95"),
    ("AQI 250 ตอนนี้", "haze", "N95"),
    ("น้ำประปาไม่ไหลมา 3 วันแล้ว", "drought", "3 ลิตร"),
    ("หมู่บ้านเจอภัยแล้ง บ่อแห้งหมด", "drought", "1784"),
])
def test_climate_hazards_are_recognised(text, kind, must):
    d = assess(text)["disaster"]
    assert d["kind"] == kind and d["active"]
    assert assess(text)["text_risk"] >= 40
    assert must in " ".join(analyze(text)["lines"])


@pytest.mark.parametrize("text", [
    "วันนี้ร้อนจัง", "ฝุ่นเยอะจัง", "pm2.5 วันนี้ 35", "PM2.5 คืออะไร",
    "อยากกินน้ำปั่น", "ร้อนใจมาก ไม่รู้จะทำยังไง", "ไม่มีน้ำใจเลย",
])
def test_everyday_weather_talk_is_not_a_disaster(text):
    assert assess(text).get("disaster") is None


def test_heat_plan_question_gets_a_plan_not_an_alarm():
    d = assess("ถ้าเกิดคลื่นความร้อนควรเตรียมอะไร")
    assert d.get("disaster") is None or not d["disaster"]["active"]
    assert analyze("ถ้าเกิดคลื่นความร้อนควรเตรียมอะไร")["lines"][0].startswith("แผนเตรียมรับความร้อนจัด")


@pytest.mark.parametrize("kind, labels", [
    ("heat", ["โรงพยาบาล"]), ("haze", ["โรงพยาบาล"]), ("drought", []), ("flood", ["ศูนย์พักพิง/อพยพ", "โรงพยาบาล"]),
])
def test_help_buttons_fit_the_hazard(kind, labels):
    assert [l["label"] for l in nearby("", {"kind": kind, "active": True})] == labels
