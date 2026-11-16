"""DriftZero รอบสุ่ม 3: คนจริงตอบไม่ตรงลำดับ — ข้ามข้อ · ตอบทีละข้อ · เล่ารวดเดียว · "ข้อ 2 … ข้อ 4 …" """
import pytest
from ENGINE.driftzero import audit, follow_up, assign

PLAN = "จะเปิดร้านกาแฟสาขาสองใช้เงิน 5 แสน"


def _keys(a):
    return [q["key"] for q in a["asks"]]


def test_skipping_the_first_question_still_lands_on_the_right_ones():
    a = audit(PLAN)
    r = follow_up(a["text"], _keys(a), "1. ถ้าพลาดเสียเงินเก็บครึ่งนึง 2. ขั้นต่ำต้องเหลือ 2 แสน 3. ค่าเช่าวันละ 1500 4. ผมเป็นเจ้าของ")
    assert {"downside", "floor", "dhd", "owner"}.isdisjoint(_keys(r))


def test_everything_in_one_sentence():
    a = audit(PLAN)
    got = assign("ถ้าพลาดก็เสียเงินเก็บ ต้องเหลืออย่างน้อย 2 แสน เงินออกวันละ 1500 ผมรับผิดชอบเอง", _keys(a))
    assert {"downside", "floor", "dhd", "owner"} <= set(got)


def test_one_answer_at_a_time_is_never_asked_again():
    a = audit(PLAN)
    r = a
    for ans in ("เสียเงินเก็บ", "2 แสน", "วันละ 1500", "ผมเอง"):
        r = follow_up(r["text"], _keys(r), ans)
    assert {"downside", "floor", "dhd", "owner"}.isdisjoint(_keys(r))


def test_explicit_question_numbers_in_any_order():
    a = audit(PLAN)
    got = assign("ข้อ 2 ขั้นต่ำ 2 แสน ข้อ 4 ผมเอง", _keys(a))
    assert got.get("floor") and got.get("owner")


def test_dont_know_is_not_recorded_as_an_answer():
    a = audit(PLAN)
    assert assign("ไม่รู้เหมือนกัน", _keys(a)) == {}
