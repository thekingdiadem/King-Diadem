"""ข้อความสั้นที่ตอบต่อจากเรื่องหนัก (core/followup.py)

คำตอบรอบแรกของเรื่องมิจฉาชีพ อารมณ์หนัก และความโกรธ จบด้วยคำถาม — คนตอบกลับสั้นๆ
เดิม: "โอนไปห้าพันแล้ว" "เงินหายไปแล้ว" → Risk 0 แผนทั่วไป · "ก็มีบ้าง" ต่อคำถามว่ามีความคิดไม่อยากอยู่ไหม → Risk 0 ทุกภาษา
"yes i already paid it" → คำตอบแรกซ้ำ "อย่าเพิ่งกดลิงก์" · "แฟน" ต่อจากความโกรธ → คำแนะนำเรื่องความรัก
"""
import re
import uuid

import pytest

from tests.conftest import FAKE_LLM

SCAM = "ได้ SMS ว่ามีใบสั่งจราจรค้างจ่าย ให้กดลิงก์ชำระค่าปรับด่วน"
GOLD = "มีคนโทรมาอ้างเป็นตำรวจ บอกให้ถอนเงินไปซื้อทอง แล้วจะส่งเจ้าหน้าที่มารับที่บ้าน"
HEAVY_TH = "ดิ่งมากเลยวันนี้ ไม่อยากทำอะไร"

# (เรื่องเดิม, คำตอบสั้น, ขึ้นต้นคำตอบที่ต้องได้, เบอร์ที่ต้องมี, Risk ขั้นต่ำ)
CASES = [
    (SCAM, "กดไปแล้ว กรอกเลขบัตรด้วย", "ไม่เป็นไรนะคะ เกิดขึ้นได้กับทุกคน", "1441", 75),
    (SCAM, "โอนไปห้าพันแล้ว", "ไม่เป็นไรนะคะ เกิดขึ้นได้กับทุกคน", "1441", 75),
    (SCAM, "ให้เลขบัตรไป", "ไม่เป็นไรนะคะ เกิดขึ้นได้กับทุกคน", "1441", 75),
    (SCAM, "ยังค่ะ", "ดีมากเลยค่ะ ที่หยุดไว้ก่อน", "1441", 0),
    (SCAM, "เปล่าค่ะ", "ดีมากเลยค่ะ ที่หยุดไว้ก่อน", "1441", 0),
    (GOLD, "ให้ไปแล้ว ทองสองบาท", "ไม่เป็นไรนะคะ", "1441", 75),
    (GOLD, "เขามาถึงหน้าบ้านแล้ว", "ไม่ต้องเปิดประตูนะคะ", "191", 85),
    ("ลงแอปจากลิงก์ไปแล้ว มันขอสิทธิ์การช่วยเหลือการเข้าถึง กดอนุญาตไปแล้ว", "เงินหายไปแล้ว", "ไม่เป็นไรนะคะ", "1441", 75),
    ("เพื่อนส่งเมลมายืมเงิน ฉันถามกลับไปทางเมล เขาตอบว่าจริง", "โอนไปแล้ว", "ไม่เป็นไรนะคะ", "1441", 75),
    ("got a text about an unpaid toll, link to pay the fine", "yes i already paid it", "It's okay — this happens", "1441", 75),
    ("got a text about an unpaid toll, link to pay the fine", "nah not yet", "Good call stopping there", "1441", 0),
    ("the app asked for accessibility permission and i allowed it", "money is gone", "It's okay — this happens", "1441", 75),
    (HEAVY_TH, "ก็มีบ้าง", "ขอบคุณที่บอกตรงๆ นะคะ", "1323", 90),
    (HEAVY_TH, "ค่ะ", "ขอบคุณที่บอกตรงๆ นะคะ", "1323", 90),
    (HEAVY_TH, "อืม", "ขอบคุณที่บอกตรงๆ นะคะ", "1323", 90),
    (HEAVY_TH, "คิดบ่อยเลย", "ขอบคุณที่บอกตรงๆ นะคะ", "1323", 90),
    (HEAVY_TH, "แค่เหนื่อย", "ขอบคุณที่ตอบนะคะ", "1323", 45),
    (HEAVY_TH, "ไม่ค่ะ แค่เหนื่อย", "ขอบคุณที่ตอบนะคะ", "1323", 45),
    ("i can't stop crying", "sometimes yes", "Thank you for telling me honestly", "1323", 90),
    ("i can't stop crying", "i think so", "Thank you for telling me honestly", "1323", 90),
    ("i can't stop crying", "not really, just tired", "Thanks for answering", "1323", 45),
    ("涙が止まらない", "少しある", "正直に話してくれてありがとう", "1323", 90),
    ("涙が止まらない", "疲れただけ", "答えてくれてありがとう", "1323", 45),
    ("我一直哭停不下来", "有一点", "谢谢你愿意说实话", "1323", 90),
    ("我一直哭停不下来", "只是累", "谢谢你回答", "1323", 45),
    ("눈물이 멈추지 않아", "조금 있어", "솔직하게 말해줘서 고마워요", "1323", 90),
    ("눈물이 멈추지 않아", "그냥 피곤해", "대답해 줘서 고마워요", "1323", 45),
    ("no puedo parar de llorar", "a veces sí", "Gracias por decírmelo con sinceridad", "1323", 90),
    ("no puedo parar de llorar", "solo cansada", "Gracias por responder", "1323", 45),      # เคยได้คำตอบภาษาอังกฤษ
    ("tôi khóc không ngừng được", "có một chút", "Cảm ơn bạn đã nói thật", "1323", 90),   # เคยได้คำตอบภาษาสเปน
    ("tôi khóc không ngừng được", "chỉ mệt thôi", "Cảm ơn bạn đã trả lời", "1323", 45),
    ("โกรธจนมือสั่น อยากทุบทุกอย่าง", "แฟน", "ขอบคุณที่บอกนะคะ — ตอนนี้ยังไม่ต้องคุย", "1323", 45),
    ("i'm furious, i want to smash everything", "my boss", "Thanks for telling me — you don't have to talk", "1323", 45),
]


def _run(client, first, reply):
    ip = "10.44.%d.%d" % tuple(uuid.uuid4().bytes[:2])
    return client.post("/run", json={"input": reply, "history": [{"role": "user", "content": first}, {"role": "assistant", "content": "..."}]},
                       headers={"cf-connecting-ip": ip}).json()


@pytest.mark.parametrize("first,reply,opener,number,risk", CASES)
def test_short_reply_continues_the_heavy_story_without_ai(client, monkeypatch, first, reply, opener, number, risk):
    monkeypatch.setenv("KD_AI", "off")
    r = _run(client, first, reply)
    out = r["ai_response"]
    assert out.startswith(opener), out[:80]
    assert number in out
    assert (r.get("risk_score") or 0) >= risk


@pytest.mark.parametrize("first,reply,number", [(SCAM, "โอนไปห้าพันแล้ว", "1441"), (HEAVY_TH, "ก็มีบ้าง", "1323"),
                                                ("i can't stop crying", "sometimes yes", "1323"), (GOLD, "เขามาถึงหน้าบ้านแล้ว", "191")])
def test_ai_reply_without_numbers_gets_the_right_one(client, first, reply, number):
    FAKE_LLM.update(text="ลองแบ่งเป็นสามขั้น 1) จด 2) แยก 3) เลือก\n— LYLA ◈")
    r = _run(client, first, reply)
    assert r["answer_source"] == "llm" and number in r["ai_response"], r["ai_response"]
    assert any("ตอบต่อจาก" in p or "ผู้ใช้" in p for p in FAKE_LLM["systems"] + FAKE_LLM["prompts"])


def test_ai_is_told_what_the_short_reply_means(client):
    FAKE_LLM.update(text="ok\n— LYLA ◈")
    _run(client, HEAVY_TH, "ก็มีบ้าง")
    sent = "\n".join(FAKE_LLM["systems"] + FAKE_LLM["prompts"])
    assert "มีความคิดไม่อยากมีชีวิตอยู่" in sent


def test_unrelated_short_message_is_not_pulled_into_the_old_story(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    r = _run(client, "วันนี้อากาศดีจัง", "ก็มีบ้าง")
    assert not r["ai_response"].startswith("ขอบคุณที่บอกตรงๆ")


def test_crisis_followup_uses_question_particles_correctly(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    out = _run(client, "อยากตาย", "ค่ะ")["ai_response"]
    assert "นะค่ะ" not in out and "ไหมค่ะ" not in out and "ปลอดภัยไหมคะ" in out


@pytest.mark.parametrize("text,risk_max", [("ทำรายงานเรื่องแก๊งคอลเซ็นเตอร์ ข่าวล่าสุด", 34), ("ข่าวแก๊งคอลเซ็นเตอร์วันนี้", 34),
                                           ("โดนแก๊งคอลเซ็นเตอร์โทรมาขู่", 100)])
def test_call_center_gang_word_alone_is_not_a_threat(text, risk_max):
    from core.kernel_voice import assess
    a = assess(text)
    assert a["text_risk"] <= risk_max
    if risk_max == 100:
        assert a["text_risk"] >= 60
