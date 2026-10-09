"""เสียงที่ตอบกับป้ายชื่อต้องตรงกัน (ภาพจากเว็บจริง: หัวข้อขึ้น LYLA แต่ตอบ "สวัสดีครับ … ผม")

ส่วนจัดเส้นทางเห็นคำว่า "กลยุทธ์" → ใช้ prompt VEGA แต่ app.py เขียนป้ายทับเป็น LYLA
"""
from core import llm_gemini as L
from tests.conftest import FAKE_LLM

CHESS = "อยากได้กลยุทธ์หมากรุกมีไหม"


def _run(client, text, persona_ui="auto", history=None):
    r = client.post("/run", json={"input": text, "route": "general", "voice_mode": "lyla",
                                  "persona_ui": persona_ui, "history": history or []})
    assert r.status_code == 200
    return r.json()


def test_auto_strategy_question_is_labelled_vega(client):
    d = _run(client, CHESS)
    assert FAKE_LLM["systems"] and FAKE_LLM["systems"][-1].startswith(L.VEGA_SYSTEM)
    assert d["persona"] == "VEGA"


def test_user_chosen_lyla_stays_lyla(client):
    d = _run(client, CHESS, persona_ui="lyla")
    assert FAKE_LLM["systems"][-1].startswith(L.LYLA_SYSTEM)
    assert d["persona"] == "LYLA"


def test_plain_message_stays_lyla(client):
    d = _run(client, "วันนี้เหนื่อยจัง")
    assert not FAKE_LLM["systems"][-1].startswith(L.VEGA_SYSTEM)
    assert d["persona"] == "LYLA"


def test_lyla_prompt_when_route_vega_but_voice_lyla():
    """ตัวเลือก prompt ใน llm_gemini: route vega แต่ voice_mode lyla → ต้องเป็น LYLA"""
    FAKE_LLM.update(systems=[])
    L.get_llm().generate_with_governance(prompt="สวัสดี", route="vega", voice_mode="lyla")
    assert not FAKE_LLM["systems"][-1].startswith(L.VEGA_SYSTEM)


def test_continuing_chat_does_not_re_greet_and_keeps_its_voice(client):
    hist = [{"role": "user", "content": CHESS}, {"role": "assistant", "content": "สวัสดีครับ ผมเข้าใจครับ"}]
    _run(client, "3", persona_ui="lyla", history=hist)
    last = FAKE_LLM["prompts"][-1]
    assert "ไม่ต้องขึ้นต้นด้วยคำทักทาย" in last and "LYLA (ฉัน/ค่ะ)" in last
