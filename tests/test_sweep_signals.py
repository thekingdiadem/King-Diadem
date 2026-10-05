"""รอบหาบั๊กทุกไฟล์: ข้อความจริงที่เคยได้ Risk 0 หรือคำตอบทั่วไปที่ไม่ตรงเรื่อง"""
import pytest

from core.engine_bridge import analyze
from core.kernel_voice import assess, compose
from ENGINE.risk_engine import evaluate_risk
from tests.conftest import FAKE_LLM


# ── ทำร้ายตัวเองแบบอ้อม ─────────────────────────────────────────────
@pytest.mark.parametrize("text", ["อยากหลับไม่ตื่น", "อยากจบทุกอย่าง", "ถ้าฉันไม่อยู่ทุกคนคงสบายกว่า",
                                  "ไม่อยากตื่นขึ้นมาอีกแล้ว", "อยากหายไปจากโลกนี้"])
def test_indirect_self_harm_is_crisis(text):
    assert evaluate_risk(text)["self_harm"] and assess(text)["crisis"]
    assert "1323" in compose(text)


@pytest.mark.parametrize("text", ["เหนื่อยจนอยากหายไป", "เบื่อชีวิต", "ไม่มีอะไรจะเสียแล้ว", "เป็นภาระของทุกคน"])
def test_warning_signs_ask_gently_and_directly(text):
    a = assess(text)
    assert not a["crisis"] and a["text_risk"] >= 60 and a["topics"][0] == "warning"
    r = compose(text)
    assert "ขอถามตรงๆ" in r and "1323" in r


@pytest.mark.parametrize("text", ["ไม่อยากตื่นเช้า", "อยากจบงานนี้ให้เสร็จ", "อยากหายไปเที่ยวทะเล",
                                  "อยากหายไปสักพัก", "ตายแน่ๆ สอบพรุ่งนี้", "ฆ่าเวลาด้วยการดูหนัง"])
def test_everyday_phrases_stay_calm(text):
    a = assess(text)
    assert not a["crisis"] and "warning" not in a["topics"]


def test_run_warning_goes_to_risk_and_tells_llm_to_ask(client):
    d = client.post("/run", json={"input": "เบื่อชีวิต"}).json()
    assert d["route"] == "risk" and d["risk_score"] >= 60
    assert "สัญญาณเตือนเรื่องทำร้ายตัวเอง" in FAKE_LLM["prompts"][-1]


# ── กินยาเกินขนาด ────────────────────────────────────────────────────
@pytest.mark.parametrize("text", ["กินยาเกินขนาดไป", "กินยาไป 20 เม็ด", "ลูกกินยาฆ่าแมลง"])
def test_overdose_is_an_emergency(text):
    a = assess(text)
    assert a["topics"][0] == "overdose" and a["text_risk"] >= 85
    r = compose(text)
    assert "1669" in r and "1367" in r and "บัตรทอง" not in r          # ขั้นฉุกเฉินครบ ไม่แบ่งให้หัวข้อรอง


@pytest.mark.parametrize("text", ["กินยาแก้ปวด", "ลืมกินยา"])
def test_ordinary_medicine_is_not_overdose(text):
    assert "overdose" not in assess(text)["topics"]


def test_run_overdose_route(client):
    d = client.post("/run", json={"input": "กินยาเกินขนาดไป"}).json()
    assert d["route"] in ("collapse", "survival") and d["risk_score"] >= 85
    assert "1367" in FAKE_LLM["prompts"][-1]


# ── มิจฉาชีพ ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("text", ["มีคนโทรมาบอกว่าเป็นตำรวจ ให้โอนเงิน", "ได้ข้อความว่าพัสดุตกค้าง ให้กดลิงก์",
                                  "ธนาคารส่ง sms ให้กดลิงก์ยืนยันตัวตน"])
def test_scam_warning(text):
    a = assess(text)
    assert a["topics"][0] == "scam" and a["text_risk"] >= 75
    r = compose(text)
    assert r.startswith("เรื่องนี้มีลักษณะของมิจฉาชีพ") and "1441" in r and "OTP" in r


@pytest.mark.parametrize("text", ["ตำรวจจับคนร้ายได้แล้ว", "ไปธนาคารโอนเงินให้แม่", "แฟนส่งลิงก์เพลงมา"])
def test_ordinary_bank_or_police_talk_is_not_scam(text):
    assert assess(text)["scam"] == []


def test_already_scammed_gets_recovery_steps(client):
    r = compose("โดนโกงซื้อของออนไลน์")
    assert r.startswith("เสียใจด้วยที่เจอแบบนี้") and "thaipoliceonline.go.th" in r
    d = client.post("/run", json={"input": "โดนโกงซื้อของออนไลน์"}).json()
    assert d["route"] == "risk" and "ผู้ใช้ถูกโกงไปแล้ว" in FAKE_LLM["prompts"][-1]


# ── หัวข้อที่เคยตกไปทาง "ทั่วไป" ─────────────────────────────────────
@pytest.mark.parametrize("text, topic, number", [
    ("ติดพนันออนไลน์ หมดไปแสนนึง", "addiction", "1413"),
    ("ท้องไม่พร้อม", "pregnancy", "1663"),
    ("โดนเพื่อนแกล้งที่โรงเรียน", "bullying", "1387"),
    ("หมาที่บ้านตาย เสียใจมาก", "grief", "1323"),
    ("ช่วยด้วย", "help", "191"),
])
def test_topics_with_right_hotlines(text, topic, number):
    assert assess(text)["topics"][0] == topic and number in compose(text)


def test_llm_gets_correct_hotlines(client):
    client.post("/run", json={"input": "ติดเหล้าเลิกไม่ได้"})
    assert "เบอร์ที่ถูกต้องสำหรับเรื่องนี้" in FAKE_LLM["prompts"][-1] and "1413" in FAKE_LLM["prompts"][-1]


def test_grief_is_not_crisis_or_idiom():
    assert assess("พ่อจะตายไหม")["topics"][:1] != ["grief"]
    assert not assess("หมาที่บ้านตาย เสียใจมาก")["crisis"]


# ── อังกฤษ: ถูกทำร้าย ─────────────────────────────────────────────────
def test_english_abuse():
    a = assess("my boyfriend hit me")
    assert a["relationship"] == "collapse_risk" and a["text_risk"] >= 80
    assert compose("my boyfriend hit me").startswith("Your safety comes first")


# ── ตัวเลข/คำที่อ่านผิด ───────────────────────────────────────────────
def test_thai_percent_word_in_debt():
    assert "240%" in " ".join(analyze("กู้นอกระบบ 10000 ดอกร้อยละ 20 ต่อเดือน")["lines"])


def test_spaced_minus_is_calculated_but_ranges_are_not():
    assert "คิดเลข: 25000 - 18000 = 7,000" in analyze("ช่วยคิด 25000 - 18000 ให้หน่อย")["lines"]
    assert "calc" not in analyze("ทำงาน 1-2 วัน ได้เท่าไหร่")["data"]


@pytest.mark.parametrize("text", ["ตึกถล่มในข่าวน่ากลัวมาก", "ไปเที่ยวพังงามา"])
def test_short_stress_words_need_word_edges(text):
    """"ล่ม" อยู่ใน "ถล่ม" · "พัง" อยู่ใน "พังงา" """
    assert evaluate_risk(text)["level"] == "low"


def test_new_tags_never_reach_the_user():
    from core.llm_gemini import scrub_internal
    for tag in ("[ข้อความมีลักษณะมิจฉาชีพ: x]", "[อาจกินยาเกินขนาด: x]", "[สัญญาณเตือนเรื่องทำร้ายตัวเอง: x]",
                "[เบอร์ที่ถูกต้องสำหรับเรื่องนี้: x]", "[ผู้ใช้ถูกโกงไปแล้ว: x]"):
        assert scrub_internal("ตอบ\n" + tag) == "ตอบ"


# ── ข้อมูลน้อยเกินจะสรุป: 👎 ครั้งเดียวเคยทำให้ /dashboard ขึ้น COLLAPSE_RISK ─────────
def test_one_vote_does_not_raise_alarms():
    from AI import reality_feedback, reality_learning
    from AI.planetary_dashboard import planetary_status
    reality_feedback._STORE.clear(); reality_learning._LOG.clear()
    reality_learning.record_outcome("", "risk", "negative", route="risk")
    reality_feedback.record_feedback("คำตอบเส้นทาง risk", "x", False, route="risk")
    assert reality_learning.learning_summary()["signal"] == "LOW_DATA"
    assert reality_feedback.feedback_stats()["signal"] == "LOW_DATA"
    assert planetary_status()["planetary_status"] != "COLLAPSE_RISK"


def test_signals_still_work_with_enough_data():
    from AI import reality_learning
    reality_learning._LOG.clear()
    for _ in range(12):
        reality_learning.record_outcome("", "risk", "negative", route="risk")
    assert reality_learning.learning_summary()["drift_risk"] == "HIGH"


# ── body ที่ไม่ใช่ JSON object เคยทำให้ทุก endpoint ตอบ 500 ─────────────────────
@pytest.mark.parametrize("path", ["/run", "/simulate", "/register", "/api/feedback"])
def test_weird_body_is_422_not_500(client, path):
    r = client.post(path, content=b"Infinity", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


# ── เรื่องเล่าผู้สร้าง: ไม่มีชื่อ-นามสกุลและวันเกิด (ผู้สร้างขอไว้) ─────────────────
_PRIVATE = ("นิธิกร", "บุญสร้าง", "Nithikorn", "Bunsrang", "2:31")


@pytest.mark.parametrize("text", ["ใครสร้างระบบนี้", "ระบบนี้สร้างมาทำไม", "who created this"])
def test_creator_story_without_private_details(text):
    r = compose(text)
    assert "มือถือ" in r or "mobile" in r.lower()
    assert not any(p in r for p in _PRIVATE)


def test_creator_story_reaches_llm_without_name(client):
    client.post("/run", json={"input": "ใครสร้างระบบนี้"})
    prompt, system = FAKE_LLM["prompts"][-1], FAKE_LLM["systems"][-1]
    assert "ผู้ใช้ถามถึงที่มาของระบบ" in prompt
    assert not any(p in prompt + system for p in _PRIVATE)


def test_creator_story_module_has_no_private_details():
    import inspect
    from core import creator_story
    src = inspect.getsource(creator_story)
    assert not any(p in src for p in _PRIVATE)


def test_ordinary_origin_questions_are_not_creator_questions():
    from core.creator_story import detect_creator_question
    assert not detect_creator_question("ที่มาของรายได้คืออะไร")
