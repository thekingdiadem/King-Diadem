"""ไฟล์ที่เพิ่งต่อเข้าระบบ (ผ่าน core/engine_bridge):
DOMAINS/survival_engine (ภัยที่กำลังเจอ) · ENGINE/tool_executor (คิดเลข) · WORLD_MODEL/human_bias (กับดักความคิด)"""
import pytest

from core.engine_bridge import analyze
from core.kernel_voice import assess, compose
from tests.conftest import FAKE_LLM


# ── ภัยที่กำลังเจอ ───────────────────────────────────────────────────
@pytest.mark.parametrize("text, name", [
    ("น้ำท่วมบ้าน ตอนนี้น้ำถึงเอวแล้ว", "น้ำท่วม"),
    ("แผ่นดินไหว ตึกสั่นมาก", "แผ่นดินไหว"),
    ("ไฟไหม้ห้องข้างๆ ควันเต็มทางเดิน", "ไฟไหม้"),
    ("ได้ยินเสียงปืนแถวนี้", "เหตุยิงหรือระเบิด"),
])
def test_disaster_raises_risk_and_puts_safety_first(text, name):
    a = assess(text)
    assert a["disaster"]["name"] == name and a["text_risk"] >= 50      # เดิม Risk 0
    r = compose(text)
    assert r.startswith("ตอนนี้ความปลอดภัยของร่างกายมาก่อน") and "1784" in r


@pytest.mark.parametrize("text", ["ความรักแบบไฟไหม้ฟาง", "รถติดน้ำท่วมขัง", "เห็นข่าวน้ำท่วมภาคเหนือ",
                                  "ถ้าน้ำท่วมควรเตรียมอะไรบ้าง", "ดูหนังแผ่นดินไหวมา สนุกดี"])
def test_no_alarm_for_idioms_news_or_plans(text):
    a = assess(text)
    assert a["disaster"] is None and a["text_risk"] < 50


def test_flood_plan_question_still_gets_a_plan():
    lines = analyze("ถ้าน้ำท่วมควรเตรียมอะไรบ้าง")["lines"]
    assert lines[0].startswith("แผนเตรียมรับน้ำท่วม") and "1784" in lines[-1]


def test_run_disaster_goes_to_survival_route(client):
    d = client.post("/run", json={"input": "น้ำท่วมบ้าน ตอนนี้น้ำถึงเอวแล้ว"}).json()
    assert d["route"] == "survival" and d["risk_score"] >= 50
    prompt = FAKE_LLM["prompts"][-1]
    assert "ผู้ใช้กำลังเจอน้ำท่วม" in prompt and "เบรกเกอร์" in prompt


def test_disaster_note_never_reaches_the_user():
    from core.llm_gemini import scrub_internal
    assert scrub_internal("ขึ้นที่สูงก่อนนะคะ\n[ผู้ใช้กำลังเจอน้ำท่วม: ตอบสั้น]") == "ขึ้นที่สูงก่อนนะคะ"


# ── คิดเลข ───────────────────────────────────────────────────────────
@pytest.mark.parametrize("text, line", [
    ("ผ่อนเดือนละ 3,500 x 12 งวด รวมเท่าไหร่", "คิดเลข: 3,500 × 12 = 42,000"),
    ("1500+2300+800 เท่าไร", "คิดเลข: 1500 + 2300 + 800 = 4,600"),
    ("ห้อง 3x4 เมตร พื้นที่เท่าไหร่", "คิดเลข: 3 × 4 = 12"),
    ("100 ÷ 3 ได้เท่าไหร่", "คิดเลข: 100 ÷ 3 = 33.33"),
])
def test_calculation(text, line):
    assert line in analyze(text)["lines"]


@pytest.mark.parametrize("text", ["ร้านเปิด 24/7 ไหม", "ทำงาน 1-2 วัน ได้เท่าไหร่", "50/50 ดีไหม",
                                  "3x4 เมตร", "9**9**9 เท่าไหร่"])
def test_not_a_calculation(text):
    assert "calc" not in analyze(text)["data"]


# ── กับดักความคิดตอนตัดสินใจ ─────────────────────────────────────────
def test_sunk_cost_note_when_deciding():
    lines = analyze("ลงทุนไปแล้ว 2 แสน เสียดายมาก ควรไปต่อไหม")["lines"]
    assert any("ถ้าเริ่มจากศูนย์วันนี้" in l for l in lines)


@pytest.mark.parametrize("text", ["เสียดายเสื้อตัวนั้น", "ต้องรีบตัดสินใจ แน่นอนว่าดี"])
def test_no_bias_note_outside_decisions_or_for_broad_words(text):
    assert "bias" not in analyze(text)["data"]


def test_spent_money_is_not_money_left():
    """เดิม "ลงทุนไปแล้ว 2 แสน" ได้ "200,000 ÷ 150 ≈ 1,333 วัน" เหมือนเป็นเงินที่ยังมี"""
    assert "1,333 วัน" not in compose("ลงทุนไปแล้ว 2 แสน เสียดายมาก ควรไปต่อไหม")
    assert "≈" in compose("ตกงาน มีเงินเหลือ 30,000 บาท")
