"""canon gate (core/cosmic_latte_canon) และต้นเหตุ/เวทนา (ENGINE/paticcasamuppada_engine)"""
import pytest

from core.cosmic_latte_canon import validate_output
from core.kernel_voice import compose
from ENGINE.paticcasamuppada_engine import detect_root_cause
from tests.conftest import FAKE_LLM

HARD = {"choice_collapse", "forced_identity"}


def _violations(text):
    return set(validate_output({"ai_response": text}).get("canon_violations", []))


# ── canon: คำตอบดีต้องไม่ถูก hard block ─────────────────────────────
@pytest.mark.parametrize("text", [
    "เราเลือกไม่ได้ว่าเขาจะคิดยังไง แต่เราเลือกได้ว่าจะดูแลใจตัวเองแบบไหน",
    "ถ้ายังเลือกไม่ได้ก็ไม่เป็นไรนะ ค่อยๆ คิด",
    "พ่อแม่เป็นสิ่งที่เราเลือกไม่ได้ แต่ชีวิตต่อจากนี้เลือกได้",
    "ยอมจำนนต่อความจริงบ้างก็ได้",
])
def test_canon_allows_good_replies(text):
    assert not _violations(text) & HARD


@pytest.mark.parametrize("text", [
    "ความรู้สึกนี้จะไม่อยู่ตลอดไป",
    "คุณไม่ได้ติดอยู่ตรงนี้ตลอดไป",
    "ให้เวลาตัวเองก่อนส่งข้อความที่ย้อนกลับไม่ได้",
])
def test_canon_no_exit_notice_for_reassurance(text):
    assert "exit_removed" not in _violations(text)


@pytest.mark.parametrize("text, v", [
    ("คุณไม่มีทางเลือก ต้องทำตามนี้", "choice_collapse"),
    ("You have no choice. Do it.", "choice_collapse"),
    ("เลือกไม่ได้หรอก ไม่มีทางเลือกอื่นแล้ว", "choice_collapse"),
    ("ต้องยอมจำนนต่อเขา", "forced_identity"),
    ("ติดอยู่ตรงนี้ตลอดไป", "exit_removed"),
])
def test_canon_still_flags_real_violations(text, v):
    assert v in _violations(text)


@pytest.mark.parametrize("msg", ["อยากตาย", "แฟนบอกเลิก", "ทะเลาะกับแม่", "ควรลาออกไหม", "หนี้เยอะ", "ตกงาน"])
def test_kernel_answers_pass_canon(msg):
    assert not _violations(compose(msg))


def test_canon_block_still_answers(client):
    """AI ตอบปิดทางเลือก → ถูกระงับ แต่ผู้ใช้ยังได้คำตอบจากสมการ"""
    FAKE_LLM["text"] = "คุณไม่มีทางเลือก ต้องทำตามนี้"
    d = client.post("/run", json={"input": "ควรลาออกไหม"}).json()
    assert d["status"] == "CANON_BLOCKED"
    assert d["answer_source"] == "kernel"
    assert "ถูกระงับ" not in d["ai_response"] and len(d["ai_response"]) > 40


# ── ปฏิจจสมุปบาท: ต้นเหตุ + เวทนา ──────────────────────────────────
@pytest.mark.parametrize("text", ["อยากตาย", "ไม่อยากอยู่แล้ว", "อยากฆ่าตัวตาย", "อยากหายไปจากโลกนี้"])
def test_death_wish_is_unpleasant_not_craving(text):
    r = detect_root_cause(text)
    assert r["root"] == "non_existence" and r["feeling"] == "unpleasant"


@pytest.mark.parametrize("text, root", [
    ("ไม่อยากไปทำงาน", "aversion"),
    ("ไม่อยากเจอหน้าใคร", "aversion"),
    ("ไม่อยากเสียเขาไป", "clinging"),
    ("อยากได้ไอโฟนใหม่มาก", "craving"),
    ("อยากให้เขากลับมา", "craving"),
    ("เกาะติดแฟนตลอด", "clinging"),
    ("กลัวตกงาน", "fear"),
])
def test_root_cause(text, root):
    assert detect_root_cause(text)["root"] == root


@pytest.mark.parametrize("text", ["อยากกินข้าว", "ต้องการเงินด่วนค่ารักษาแม่", "ไปเที่ยวเกาะสมุย", "ธนาคารจะยึดรถ"])
def test_needs_and_places_are_not_craving_or_clinging(text):
    assert detect_root_cause(text)["root"] not in ("craving", "clinging")
