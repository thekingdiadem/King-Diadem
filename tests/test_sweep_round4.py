"""รอบหาบั๊ก 4: ประโยคที่คนพิมพ์จริง — สัญญาณกินยาเพื่อไม่ตื่น · สำนวนที่ถูกนับเป็นภัยพิบัติ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("text", ["อยากกินยาให้หลับไม่ตื่น", "อยากกินยานอนทั้งแผง", "อยากหลับไม่ตื่นอีกเลย"])
def test_pills_to_not_wake_up_is_a_crisis(text):
    """เดิมได้ Risk 0 — มีคำว่ายาคั่น เลยไม่ติดรูป "อยากหลับไม่ตื่น" """
    a = assess(text)
    assert a["crisis"] and a["text_risk"] >= 90


def test_whole_strip_taken_is_overdose():
    a = assess("กินยานอนทั้งแผงไปแล้ว")
    assert "overdose" in a["topics"] and a["text_risk"] >= 80


@pytest.mark.parametrize("text", ["ยานอนหลับช่วยให้หลับไม่ตื่นกลางดึกไหม", "กินยาแก้ปวดหมดแผงในอาทิตย์เดียว",
                                  "อยากกินยาให้หลับไปเลย"])
def test_sleep_and_pill_questions_are_not_crises(text):
    a = assess(text)
    assert not a["crisis"] and "overdose" not in a["topics"]


@pytest.mark.parametrize("text", ["น้ำท่วมปอดเลย ดีใจมาก", "แผ่นดินไหวในใจ", "ไฟป่าในใจ", "ใจเหมือนแผ่นดินไหว",
                                  "ชีวิตเหมือนโดนน้ำท่วม", "น้ำท่วมหัวเอาตัวไม่รอด"])
def test_idioms_are_not_disasters(text):
    a = assess(text)
    assert a["disaster"] is None and a["text_risk"] == 0


@pytest.mark.parametrize("text, kind", [("น้ำท่วมบ้าน ตอนนี้น้ำถึงเอวแล้ว", "flood"), ("แผ่นดินไหว ตึกสั่นมาก", "quake"),
                                        ("บ้านเหมือนจะพังเพราะแผ่นดินไหว", "quake")])
def test_real_disasters_still_detected(text, kind):
    assert assess(text)["disaster"]["kind"] == kind
