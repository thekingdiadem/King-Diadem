"""WORLD_MODEL — แบบจำลองโลกของการตัดสินใจ (เจ้าของโปรเจกต์: "อัพเกรดเวิร์ลโมดูล เราควรเพิ่มโมดูลมากกว่านี้แล้ว")
เดิมมี 3 โมดูล · human_bias จับได้ 4 แบบจากคำกว้างๆ และไม่มีใครเอาไปใช้ในสภา
ตอนนี้ 5 โมดูลใหม่/อัปเกรด เรียกผ่าน observe() จุดเดียว และสภา/VEGA/AI ใช้ร่วมกัน"""
import pytest

from WORLD_MODEL import observe
from WORLD_MODEL.human_bias import detect_bias_context, detect_biases


@pytest.mark.parametrize("text,kind", [
    ("ลงทุนคริปโตไปตั้งแสนแล้ว ขาดทุนอยู่", "sunk_cost"), ("we've already invested two years into this", "sunk_cost"),
    ("เพื่อนๆ ลงกันหมดแล้ว กลัวตกรถ", "fomo"), ("everyone is buying it right now", "fomo"),
    ("ธุรกิจนี้ไม่มีทางเจ๊ง", "overconfidence"), ("ยูทูบเบอร์คนดังแนะนำให้ซื้อ", "authority"),
    ("ช่วยบอกว่าควรทำทีเถอะ ขอแค่คนเห็นด้วย", "confirmation"), ("รูดไปก่อน ค่อยว่ากันทีหลัง", "present_bias"),
    ("เสียมาหลายรอบแล้ว รอบนี้ต้องได้คืน จะกู้มาทบ", "gambler"), ("เขาให้เวลาแค่วันนี้ ต้องโอนภายในคืนนี้", "panic"),
    ("อยู่แบบนี้มานานแล้ว เคยชินแล้ว", "status_quo"), ("หุ้นเคยขึ้นไปถึง 50 รอให้กลับไปเท่าเดิม", "anchoring"),
])
def test_ten_thinking_traps_each_with_a_debias_question(text, kind):
    found = {b.kind: b for b in detect_biases(text)}
    assert kind in found and found[kind].question.endswith("?"), (text, list(found))


@pytest.mark.parametrize("text", ["วันนี้อากาศดี ไปเดินเล่นกับลูก", "รีบไปทำงาน", "แน่นอนว่าฉันรักแม่", "ซื้อกาแฟให้เพื่อน"])
def test_ordinary_words_are_not_thinking_traps(text):
    assert not detect_biases(text)


def test_old_api_still_works_for_engine_bridge():
    assert detect_bias_context("เสียดายเงินที่ลงไป") == "loss" and detect_bias_context("สวัสดี") == "normal"


def test_observe_sees_locks_concentration_ripples_and_horizon():
    w = observe("เงินเก็บ 300,000 ทั้งหมด จะลาออกไปเปิดร้าน ลูกยังเล็ก ต้องตัดสินใจวันนี้")
    assert {lk.kind for lk in w.locks} >= {"quit", "all_in"} and w.concentration[0].kind == "all_savings"
    assert w.ripples[0].who == "children" and w.horizon == "short" and "3 ปี" in w.horizon_prompt
    note = w.note()
    assert note.startswith("[WORLD MODEL:") and "ลาออกจากงานประจำ" in note
    assert observe("กู้มาเทรดหุ้น").concentration[0].kind == "leverage"


def test_council_voices_use_the_world_model():
    from core.kernel_voice import compose
    out = compose("เงินเดือน 35,000 เงินเก็บ 300,000 ทั้งหมด จะลาออกไปเปิดร้านกาแฟ เพื่อนๆ ลงกันหมดแล้ว ลูกยังเล็ก ควรทำไหม", voice_mode="council")
    assert "กลัวตกขบวน" in out                    # PATICCA ← human_bias
    assert "ทำให้ถอยได้" in out                    # VEGA ← reversibility / concentration
    assert "ลูกต้องย้ายโรงเรียน" in out             # CIVIL ← consequences
    assert "6 เดือนแรก" in out or "3 ปี" in out     # COSMOS ← time_horizon


def test_ai_context_includes_the_world_model():
    from core import decision_brief as db
    line = db.facts_line(db.analyze("ลงทุนคริปโตไปตั้งแสนแล้ว จะกู้มาทบเพิ่มดีไหม"))
    assert "[WORLD MODEL:" in line and "เสียดายสิ่งที่ลงไปแล้ว" in line
