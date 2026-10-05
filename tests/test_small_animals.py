"""ANIMA-SAFE: WORLD_MODEL/small_animal_model ต่อเข้าแชทผ่าน core/engine_bridge"""
import pytest
from WORLD_MODEL.small_animal_model import full_assessment
from core.engine_bridge import analyze
from tests.conftest import FAKE_LLM


@pytest.mark.parametrize("text, animal", [
    ("จะวางยาเบื่อหนู", "mouse"), ("หนูกินของในครัว อยากกำจัด", "mouse"),
    ("I want to kill the rats in my garage", "rat"), ("mice in the attic", "mouse"),
])
def test_animals_that_were_missed_are_detected(text, animal):
    """เดิม "ยาเบื่อหนู" "หนู...ในครัว" และพหูพจน์อังกฤษ (rats/mice) ไม่ถูกนับว่าพูดถึงสัตว์"""
    assert animal in [a["animal"] for a in full_assessment(text)["animal_detection"]["animals"]]


@pytest.mark.parametrize("text", ["หนูพยายามแล้วค่ะ", "หนูกินข้าวแล้ว", "หนูไม่สบายค่ะ"])
def test_pronoun_nu_is_not_an_animal(text):
    assert full_assessment(text)["response_type"] == "MONITOR" and analyze(text)["data"].get("animal") is None


def test_rabbit_not_eating_is_not_good():
    """เดิม "ไม่ยอมกิน" ติดคำว่า "กิน" ฝั่งดี → ประเมินว่าสบายดี"""
    assert full_assessment("กระต่ายที่บ้านไม่ยอมกิน")["welfare"]["welfare_status"] == "POOR"
    assert full_assessment("กระต่ายวิ่งเล่นกินผักทุกวัน")["welfare"]["welfare_status"] == "GOOD"


def test_killing_time_is_not_harm():
    assert full_assessment("ฆ่าเวลาเล่นกับกระต่าย")["response_type"] == "GUIDE"


def test_poison_gets_humane_options_first():
    lines = " ".join(analyze("จะวางยาเบื่อหนู")["lines"])
    assert "ไม่ต้องฆ่า" in lines and "กรงดักแบบเป็น" in lines


def test_sick_pet_goes_to_vet_not_wildlife_hotline():
    lines = " ".join(analyze("กระต่ายที่บ้านไม่ยอมกิน")["lines"])
    assert "สัตวแพทย์" in lines and "1362" not in lines


def test_just_mentioning_a_pet_adds_nothing():
    assert analyze("อยากได้กระต่ายมาเลี้ยง")["lines"] == []


def test_run_passes_humane_options_to_llm(client):
    client.post("/run", json={"input": "จะวางยาเบื่อหนูในครัว ทำยังไงดี"})
    assert "กรงดักแบบเป็น" in FAKE_LLM["prompts"][-1]
