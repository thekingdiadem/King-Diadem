"""เรื่องด่วนภาษาอื่น (จีน ญี่ปุ่น เกาหลี สเปน) — เดิมจับได้แค่ "อยากตาย" ที่เหลือได้ "ลองเรียงเรื่องทีละขั้น" Risk 45"""
import pytest

from core.kernel_voice import assess, compose
from core.lang_signals import detect_lang
from ENGINE.risk_engine import evaluate_risk
from core import llm_gemini

CASES = [
    ("我妈妈晕倒了", "120"), ("母が倒れた", "119"), ("엄마가 쓰러졌어", "119"), ("mi mamá se desmayó", "112"),
    ("我被老公打了", "110"), ("夫に殴られた", "110"), ("남편한테 맞았어", "112"), ("mi esposo me pegó", "016"),
    ("地震了", "119"), ("火事だ", "119"), ("불이 났어", "119"), ("hay un incendio en mi casa", "112"),
    ("有人冒充警察让我转账到安全账户", "96110"), ("警察を名乗る人から送金しろと言われた", "#9110"),
    ("경찰이라며 돈을 보내래", "112"), ("me pidieron transferir dinero", "112"),
]


@pytest.mark.parametrize("text,number", CASES)
def test_urgent_reply_in_users_language_with_local_number(text, number):
    a = assess(text)
    assert a["text_risk"] >= 70 and a["intl_urgent"], text
    r = compose(text)
    assert number in r and "ทีละขั้น" not in r


@pytest.mark.parametrize("text", ["我朋友说他想自杀", "友達が死にたいと言っている", "친구가 죽고 싶대", "mi amigo quiere suicidarse",
                                  "我朋友说他想自杀ค่ะ"])
def test_someone_else_in_crisis_is_not_users_crisis(text):
    a = assess(text)
    assert not a["crisis"] and "someone" in a["topics"]
    assert not evaluate_risk(text)["self_harm"] and not llm_gemini.detect_crisis(text)


def test_user_crisis_next_to_friends_still_caught():
    assert assess("友達が死にたいと言っている、私も死にたい")["crisis"]


@pytest.mark.parametrize("text", ["想死你了", "死ぬほど笑った", "죽을 만큼 웃겼어", "me muero de risa", "今天天气很好"])
def test_idioms_and_small_talk_stay_calm(text):
    a = assess(text)
    assert not a["crisis"] and not a["intl_urgent"] and a["text_risk"] < 50


def test_spanish_with_accents_is_spanish():
    assert detect_lang("mi mamá se desmayó") == "es" and detect_lang("hay un terremoto") == "es"


def test_english_glued_to_thai_particle():
    """"I want to dieค่ะ" เคยหลุดเพราะ \\b ไม่ตัดคำระหว่างอังกฤษกับไทย"""
    for t in ("I want to dieค่ะ", "I cut myselfครับ"):
        assert assess(t)["crisis"] and evaluate_risk(t)["self_harm"] and llm_gemini.detect_crisis(t), t


def test_llm_gets_local_numbers_for_foreign_disaster(client):
    from tests.conftest import FAKE_LLM
    client.post("/run", json={"input": "地震了"})
    assert "ญี่ปุ่น 110/119" in FAKE_LLM["prompts"][-1] or "จีน 110/119/120" in FAKE_LLM["prompts"][-1]
