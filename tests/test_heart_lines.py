"""คำตอบที่ได้ใจ — ตอบความรู้สึกที่ผู้ใช้เล่า ไม่ใช่แค่ขั้นตอน (core/heart_lines.py)
หลัก: เราไม่ได้ต้องการคำตอบที่สมบูรณ์แบบ เราแค่ต้องการรู้ว่ายังมีทางเลือกอยู่"""
import pytest
from core.kernel_voice import compose


@pytest.mark.parametrize("q,must", [
    ("โดนหลอกโอนเงินไปหมดตัว รู้สึกโง่มาก", ["เขาเก่งเรื่องโกหก", "ยังมีทางเลือก", "1323"]),
    ("แฟนทุบหนูอีกแล้ว ไม่รู้จะไปไหน", ["ไม่ได้แปลว่าไม่มีทางเลือก", "1300", "ไม่ใช่ความผิดของคุณ"]),
    ("I lost all my savings to a scam and I'm so ashamed", ["skilled liars", "still have choices"]),
    ("my husband hit me again and I have nowhere to go", ["doesn't mean having no options", "not your fault"]),
])
def test_reply_answers_the_feeling(q, must):
    r = compose(q)
    for m in must:
        assert m in r, (m, r)
    assert r.count("\n") < 40


@pytest.mark.parametrize("q", ["มีคนอ้างเป็นตำรวจให้โอนเงิน", "อยากตาย", "สามีตบหนู"])
def test_no_extra_lines_when_feeling_not_said(q):
    r = compose(q)
    assert "เขาเก่งเรื่องโกหก" not in r and "ไม่ได้แปลว่าไม่มีทางเลือก" not in r


@pytest.mark.parametrize("q,must", [
    ("หนี้ท่วมหัว อายจนไม่กล้าออกจากบ้าน", ["ไม่ได้วัดค่าของคน"]),
    ("ตกงานมาสามเดือน ไม่กล้าบอกที่บ้าน", ["ไม่ได้วัดค่าของคน"]),
    ("I lost my job and I'm ashamed to tell my family", ["doesn't measure your worth"]),
    ("แม่เพิ่งเสีย หนูไม่ได้อยู่ข้างแม่ตอนสุดท้าย รู้สึกผิดมาก", ["ไม่ได้ลบทุกวันที่คุณรักเขามา", "เสียใจด้วยนะ"]),
    ("my dad died and I wasn't there, I feel so guilty", ["doesn't erase all the days you loved them", "I'm so sorry"]),
])
def test_shame_and_guilt_get_a_line_for_the_heart(q, must):
    r = compose(q)
    for m in must:
        assert m in r, (m, r)


def test_grief_opens_with_condolence_not_step_by_step():
    r = compose("แม่เพิ่งเสีย หนูไม่ได้อยู่ข้างแม่ตอนสุดท้าย รู้สึกผิดมาก")
    assert r.startswith("เสียใจด้วย") and "ขอเรียงทางให้ทีละขั้น" not in r


@pytest.mark.parametrize("q", ["แม่เสียใจที่หนูสอบตก", "พ่อเสียงดังมาก", "my son passed the exam"])
def test_not_grief(q):
    from core.kernel_voice import assess
    assert "grief" not in assess(q)["topics"]


@pytest.mark.parametrize("q,must", [
    ("ดูแลพ่อติดเตียงคนเดียว บางทีหงุดหงิดใส่พ่อแล้วก็เกลียดตัวเองที่เป็นแบบนี้", "ไม่ได้แปลว่าคุณรักเขาน้อยลง"),
    ("I look after my mom alone and I snapped at her today", "doesn't mean you love them less"),
    ("เลิกกับแฟนแล้ว รู้สึกว่าตัวเองไร้ค่า", "ความรักที่จบลงไม่ได้วัดค่าของคุณ"),
    ("สอบตก รู้สึกว่าตัวเองไม่ได้เรื่อง", "ไม่ใช่ป้ายที่บอกว่าคุณเป็นคนแบบไหน"),
])
def test_caregiver_breakup_exam_feelings(q, must):
    assert must in compose(q)


def test_no_worth_line_without_the_feeling():
    assert "ความรักที่จบลงไม่ได้วัดค่าของคุณ" not in compose("เลิกกับแฟนแล้ว แต่ก็โอเค")
