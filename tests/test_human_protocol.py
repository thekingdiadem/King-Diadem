"""HUMAN PROTOCOL (ENFORCED) — core/human_protocol.py
ไฟล์เดิมของเจ้าของโปรเจกต์ (AI/HUMAN_PROTOCOL.py, เม.ย. 2026) เป็นข้อความ markdown ที่ตั้งชื่อ .py จึงไม่เคยถูกรัน
หลัก "อย่างน้อย 2 ทางเลือก · ไม่สรุปแทนผู้ใช้" ถูกสั่งใน prompt แล้ว ไฟล์นี้ตรวจว่าคำตอบจริงทำตามหรือไม่"""
import pytest

from core.human_protocol import audit, enforce, forced, options_in


@pytest.mark.parametrize("reply,n", [
    ("1) ขอลดเวลาทำงาน\n2) หาคนช่วยดูแล", 2),
    ("- ทางแรก\n- ทางที่สอง\n- ทางสำรอง", 3),
    ("ทางแรกคือคุยกับหัวหน้า หรือจะลองหางานใหม่ก็ได้", 2),
    ("Option A: rent. Option B: buy.", 2),
    ("ลองพักผ่อนให้เต็มที่นะคะ", 0),
])
def test_counts_options(reply, n):
    assert options_in(reply) == n


@pytest.mark.parametrize("reply", ["ทางเดียวคือลาออก", "ไม่มีทางอื่นแล้วค่ะ", "คุณต้องขายบ้านเท่านั้น", "You have no choice but to quit."])
def test_spots_forced_single_conclusion(reply):
    assert forced(reply) and not audit(reply)["ok"]


def test_patch_restores_options_before_the_signature():
    out, a = enforce("แม่ป่วยติดเตียง ต้องลาออกมาดูแล เงินไม่พอ", "ต้องลาออกเท่านั้น ไม่มีทางอื่นแล้ว\n\n— LYLA ◈")
    assert a["patched"] and "ทางที่ยังเปิดอยู่:" in out and "คุณเป็นคนเลือกเสมอ" in out
    assert out.rstrip().endswith("— LYLA ◈") and out.index("ทางที่ยังเปิดอยู่") < out.index("— LYLA ◈")


def test_good_answers_and_small_talk_are_untouched():
    good = "มีสองทาง\n1) ขอลดเวลาทำงาน\n2) หาคนช่วยดูแล"
    assert enforce("แม่ป่วยติดเตียง ต้องลาออกมาดูแล เงินไม่พอ", good)[0] == good
    out, a = enforce("สวัสดีค่ะ", "สวัสดีค่ะ ยินดีที่ได้คุยนะคะ")
    assert out == "สวัสดีค่ะ ยินดีที่ได้คุยนะคะ" and a["applies"] is False


def test_no_lens_means_no_guessing():
    out, a = enforce("อยากกินข้าวมันไก่ร้านไหนดี", "ลองร้านนี้ดูค่ะ")
    assert out == "ลองร้านนี้ดูค่ะ" and a["applies"] and not a["patched"]


def test_urgent_is_never_patched():
    out, a = enforce("แม่ป่วยติดเตียง ต้องลาออกมาดูแล", "โทร 1669 เดี๋ยวนี้ค่ะ", urgent=True)
    assert out == "โทร 1669 เดี๋ยวนี้ค่ะ" and not a["applies"]


def _run(client, text, ai_text):
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = ai_text
    try:
        return client.post("/run", json={"input": text}).json()
    finally:
        FAKE_LLM["text"] = None


def test_live_ai_reply_that_forces_one_path_gets_options(client):
    d = _run(client, "แม่ป่วยติดเตียง ต้องลาออกมาดูแล แต่เงินเก็บใกล้หมด พี่น้องไม่ช่วยเลย", "ทางเดียวคือลาออกไปดูแลแม่ค่ะ")
    assert "ทางที่ยังเปิดอยู่:" in d["ai_response"]


def test_live_crisis_reply_is_left_alone(client):
    d = _run(client, "ไม่อยากอยู่แล้ว เหนื่อยมาก", "ตอนนี้โทร 1323 ได้เลยนะคะ")
    assert "ทางที่ยังเปิดอยู่:" not in d["ai_response"]


def test_ai_learns_worth_lies_in_intent_not_outcome():
    """เจ้าของโปรเจกต์: "เจตนาที่บริสุทธิ์ในการเลือกทำสิ่งที่ดีที่สุดภายใต้ข้อจำกัดนั้น คือสิ่งคุณค่า ...
    Make them feel like they're worth something again." """
    import core.llm_gemini as L
    for name in ("LYLA_SYSTEM", "VEGA_SYSTEM", "COUNCIL_SYSTEM", "CRISIS_SYSTEM"):
        p = getattr(L, name)
        assert "คุณค่าอยู่ที่เจตนาดีในการเลือกทางที่ดีที่สุดภายใต้ข้อจำกัดนั้น" in p, name
        assert "ทำให้เขารู้สึกว่าตัวเองมีค่าอีกครั้ง" in p and "ไม่ตัดสินคนจากผลลัพธ์" in p, name
