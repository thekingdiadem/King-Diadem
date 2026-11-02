"""ความคิดของ AI หลุดถึงผู้ใช้ทั้งก้อน (หน้าจอจริง พ.ย. 2569 — "สูงไหมความเสี่ยง")
โมเดลเขียนแผนเป็นภาษาอังกฤษธรรมดา: "My task is to assess…" "According to the LYLA persona…"
"The `[ก่อนตอบ: …]` is an internal instruction…" แล้วต่อคำตอบจริงติดท้าย "…empathetic but direct).ความเสี่ยงจะ…"
ตัวตัดเดิมไม่รู้จักประโยคพวกนี้ เลยไม่ตัดอะไรเลย"""
from pathlib import Path

import pytest

from core.llm_gemini import salvage_answer, scrub_internal, strip_notes, strip_reasoning

LEAK = (Path(__file__).parent / "reasoning_leak_nov2026.txt").read_text(encoding="utf-8")


def _clean(t):
    return scrub_internal(strip_notes(salvage_answer(strip_reasoning(t))))


def test_only_the_answer_to_the_user_is_left():
    out = _clean(LEAK)
    assert out.startswith("ความเสี่ยงจะสูงหรือไม่นั้น")
    assert "ประเมินให้ได้ชัดเจนขึ้นค่ะ" in out
    for bad in ("the user", "LYLA persona", "internal instruction", "ก่อนตอบ", "My task", "emojis", "clarifying"):
        assert bad not in out, bad
    assert out.count("ความเสี่ยงจะสูงหรือไม่นั้น") == 1          # ไม่เอาร่างคำตอบในเครื่องหมายคำพูดมาซ้ำ


def test_english_plan_with_no_answer_falls_back_to_the_kernel():
    """ผู้ใช้ภาษาอังกฤษ (หรืออักษรละติน) แล้วโมเดลส่งมาแต่ความคิด → "" ให้ระบบตอบจากสมการแทน"""
    t = ("My task is to assess the risk. According to the LYLA persona, the user wants clarity.\n"
         "I should ask a clarifying question. The question should be gentle.")
    assert _clean(t) == ""


def test_english_answer_keeps_lines_meant_for_the_person():
    t = ("The user's current message is a worry about debt. My task is to reassure.\n"
         "I should ask one clarifying question.\n"
         "That sounds really heavy. What is the monthly payment you can manage right now?")
    assert _clean(t) == "That sounds really heavy. What is the monthly payment you can manage right now?"


@pytest.mark.parametrize("t", [
    "เข้าใจเลยค่ะว่าเรื่องนี้หนักใจ\n\n1) เขียนสิ่งที่เกิดขึ้น 3 บรรทัด\n2) เลือกก้าวเล็กที่สุดวันนี้\n\nตอนนี้อะไรหนักที่สุดคะ",
    "You should call your bank today and ask them to freeze the account. Then report it at 1441.",
    "I hear you. You don't have to decide tonight — what would help you sleep a little first?",
    "LYLA อยู่ตรงนี้นะคะ ถ้าอยากเล่าเพิ่ม LYLA พร้อมฟังค่ะ",
])
def test_normal_answers_are_untouched(t):
    assert salvage_answer(t) == t
