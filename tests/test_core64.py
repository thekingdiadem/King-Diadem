"""SYSTEM CORE 64 — แกนจริยธรรมของเจ้าของโปรเจกต์ แบ่งใช้ 3 ทาง (CORE64.md)
ไม่ส่งให้ AI ทั้ง 64 ข้อ เพราะคำสั่งยาวทำให้ AI คิดออกมาให้ผู้ใช้เห็น และบางข้อใช้ตรงๆ แล้วอันตราย"""
import re
from pathlib import Path

import pytest

from core.llm_gemini import KD_DNA
from ENGINE.driftzero import audit

ROOT = Path(__file__).resolve().parent.parent


def test_full_text_is_kept_with_all_64_rules():
    t = (ROOT / "CORE64.md").read_text(encoding="utf-8")
    nums = [int(n) for n in re.findall(r"^(\d+)\. ", t, re.M)]
    assert nums == list(range(1, 65))
    assert "ระบบคือกระจก ไม่ใช่เจ้านาย" in t and "ชีวิตต้องไม่ตายตามคน" in t


def test_ai_gets_a_short_version_not_all_64():
    core = KD_DNA[KD_DNA.index("SYSTEM CORE 64"):]
    assert len([l for l in core.splitlines() if l.startswith("- ")]) <= 12
    assert "ระบบเป็นกระจก ไม่ใช่เจ้านาย" in core


def test_risky_rules_are_guarded_for_the_ai():
    """ข้อ 46 ห้ามใช้กับคนสิ้นหวัง · ข้อ 63 ไม่ได้แปลว่าให้ฝ่าฝืนกฎหมาย · เรื่องสัตว์ไม่เทศนาผู้ใช้"""
    assert "ห้ามบอกคนที่สิ้นหวังหรือกำลังวิกฤตว่า \"ความหวังคือความยึดติด\"" in KD_DNA
    assert "ไม่ได้แปลว่าแนะนำให้ฝ่าฝืนกฎหมาย" in KD_DNA
    assert "ไม่เทศนาเรื่องการกินหรืออาชีพของผู้ใช้" in KD_DNA


@pytest.mark.parametrize("text,gate", [
    ("โรงงานจะวางยาเบื่อหมาจรจัดรอบโรงงานเพราะสะดวกกว่า", "C61"),
    ("We plan animal testing for the new cosmetic line", "C61"),
    ("โครงการคอนโดต้องไล่ที่ชุมชนริมทางรถไฟ 200 หลังคาเรือน", "C26"),
    ("The developer will evict 50 families next month", "C26"),
])
def test_core_gates_in_driftzero(text, gate):
    assert gate in [g["id"] for g in audit(text)["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("text", ["ร้านหมูกระทะจะเปิดสาขาใหม่ งบ 2 ล้าน", "ฟาร์มไก่จะขยายโรงเรือน"])
def test_ordinary_food_business_is_not_lectured(text):
    stops = [g["id"] for g in audit(text)["gates"] if g["status"] == "stop"]
    assert "C61" not in stops
