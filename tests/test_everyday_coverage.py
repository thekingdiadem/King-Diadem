"""เรื่องบ้านๆ ถึงระดับโลก ตอนไม่มี AI ต้องตอบตรงเรื่อง — เดิมผ่าน 13/26
("แมวหาย 2 วัน" "ถ้าเกิดสงครามครอบครัวควรเตรียมอะไร" "ไฟดับ 2 วัน" ได้ "เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว")
ชุดคำถามอยู่ tests/everyday_questions.py · ดูภาพรวม: python scripts/eval_everyday.py"""
import pytest

from core.kernel_voice import _everyday, compose
from scripts.eval_everyday import check
from tests.everyday_questions import CASES, NOT_EVERYDAY


@pytest.mark.parametrize("q,want", CASES)
def test_answer_is_on_topic(q, want):
    ok, why = check(q, want)
    assert ok, f"{q} → {why}"


@pytest.mark.parametrize("q", NOT_EVERYDAY)
def test_lookalike_words_do_not_trigger(q):
    assert _everyday(q) is None


def test_urgent_signs_still_win():
    assert "1669" in compose("ยายเป็นลมแดด หมดสติ ไม่หายใจ")
    assert "1441" in compose("ตำรวจโทรมาบอกว่าบัตรประชาชนหายถูกเอาไปเปิดบัญชีม้า ให้โอนเงินไปตรวจสอบ")
