"""WORLD_MODEL/earth_guardian — เผาไร่/เผาขยะ/ทิ้งของเสียลงน้ำ ต่อเข้าแชทผ่าน core/engine_bridge"""
import pytest
from core.engine_bridge import analyze
from tests.conftest import FAKE_LLM


@pytest.mark.parametrize("text, kind, must", [
    ("จะเผาตอซังดีไหม รีบปลูกรอบใหม่", "field_burning", "ไถกลบ"),
    ("ไม่เผาฟางแล้วทำยังไง", "field_burning", "ไถกลบ"),
    ("เผาขยะหลังบ้านทุกวัน", "trash_burning", "รับซื้อของเก่า"),
    ("ทิ้งน้ำมันทอดลงท่อระบายน้ำได้ไหม", "water_dumping", "ไบโอดีเซล"),
    ("is burning the rice straw ok", "field_burning", "ไถกลบ"),
])
def test_own_burning_or_dumping_gets_alternatives(text, kind, must):
    r = analyze(text)
    assert r["data"]["earth"]["kind"] == kind and r["data"]["earth"]["self"] is True
    assert must in " ".join(r["lines"])


def test_neighbour_burning_gets_protection_and_complaint_channel():
    r = analyze("เพื่อนบ้านเผาขยะทุกเย็น ควันเข้าบ้าน")
    lines = " ".join(r["lines"])
    assert r["data"]["earth"]["self"] is False and "N95" in lines and "1567" in lines


@pytest.mark.parametrize("text", ["ห้ามเผาไร่ช่วงนี้ไหม", "เผาผีตอนตายไหม", "ทำปุ๋ยหมักยังไง", "ไฟไหม้หญ้าข้างบ้าน ตอนนี้ลามมา"])
def test_unrelated_or_active_fire_is_not_earth_advice(text):
    assert "earth" not in analyze(text)["data"]


def test_run_passes_alternatives_to_llm(client):
    client.post("/run", json={"input": "จะเผาตอซังพรุ่งนี้ ดีไหม"})
    assert "ไถกลบ" in FAKE_LLM["prompts"][-1]


def test_new_short_topic_is_not_dragged_into_earlier_basic_needs(client):
    """หน้าจอจริง: "จะเผาตอซังดีไหม" หลังคุยเรื่องหมดเงิน ได้ 1300 + "คืนนี้มีที่นอนไหม" แทรกมา และเส้นทาง SURVIVAL"""
    d = client.post("/run", json={"input": "จะเผาตอซังดีไหม", "history": [
        {"role": "user", "content": "ตอนนี้หมดเงิน งานหมด อาหาร1มื้อ"}, {"role": "assistant", "content": "..."}]}).json()
    p = FAKE_LLM["prompts"][-1]
    assert d["route"] != "survival" and "1300" not in p and "ไถกลบ" in p
