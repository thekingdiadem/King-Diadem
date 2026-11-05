"""ความรู้การเรียนที่ลงลึก — core/knowledge_edu.py
รอบแรก: ทุนรายประเทศ 75% · การศึกษาพิเศษ 14% · สายอาชีพ 7% · ครูและผู้ปกครอง 35%
ใช้ประโยคที่ "ไม่อยู่ใน" ชุดวัดผล และตรวจว่าเรื่องใกล้เคียงไม่ถูกดึงมาผิดหมวด"""
import pytest

from core.kernel_voice import compose
from core.knowledge_edu import EDU
from core.knowledge_th import KNOWLEDGE


def _key(text):
    for key, rx, _ in KNOWLEDGE:
        if rx.search(text):
            return key
    return None


@pytest.mark.parametrize("text,must", [
    ("มีทุนต่อเอกที่เกียวโตไหม", "MEXT"), ("อยากศึกษาต่อที่ปูซาน", "GKS"),
    ("ขอทุนเรียนที่ไทเป", "Taiwan Scholarship"), ("เรียนต่อโทเมลเบิร์นใช้เงินเท่าไหร่", "IELTS"),
    ("เรียนฟรีที่มิวนิกจริงไหม", "Blocked Account"), ("อยากต่อโทที่ปารีส", "Campus France"),
    ("อยากต่อโทลอนดอนแบบมีทุน", "Chevening"), ("ทุนเรียนต่อที่สหรัฐ", "Fulbright"),
    ("ลูกอยากต่อตรีที่สิงคโปร์", "ASEAN Undergraduate Scholarship"),
])
def test_country_scholarships(text, must):
    assert must in compose(text)


@pytest.mark.parametrize("text,must", [
    ("หลานอยู่ไม่นิ่งเลย ครูบอกว่าอาจสมาธิสั้น", "จิตแพทย์เด็ก"), ("ลูกเขียนตัว ด กับ ค สลับตลอด", "IEP"),
    ("ร.ร.ปฏิเสธไม่รับเพราะลูกเป็นออทิสติก", "เลือกปฏิบัติ"), ("ลูกสาวหูตึงสองข้าง", "ภาษามือ"),
    ("ลูกสายตาเลือนรางมาก", "เบรลล์"), ("ลูกสองขวบยังไม่พูด", "DSPM"),
    ("อยากรู้สิทธิคนพิการเรื่องเรียน", "1479"), ("ลูกฉลาดเกินวัยแต่ไม่มีเพื่อน", "อารมณ์"),
    ("ผมเป็นดิสเลกเซีย สอบเข้ามหาลัยได้ไหม", "เพิ่มเวลาสอบ"),
])
def test_special_education(text, must):
    assert must in compose(text)


@pytest.mark.parametrize("text,must", [
    ("ต่อ ปวช หรือ ม.4 ดี", "ปวช."), ("ระบบทวิภาคีได้เงินไหม", "เบี้ยเลี้ยง"),
    ("จบปวส.ช่างกล อยากต่อตรี", "เทียบโอน"), ("อยากสอบมาตรฐานฝีมือช่างเชื่อม", "กรมพัฒนาฝีมือแรงงาน"),
    ("ที่บ้านห้ามเรียนสายช่าง", "รายได้"), ("เรียนปวส.เสาร์อาทิตย์ได้ไหม", "เทียบโอน"),
])
def test_vocational(text, must):
    assert must in compose(text)


@pytest.mark.parametrize("text,must", [
    ("นักเรียน ม.2 เสียงดังทั้งคาบ", "กติกา"), ("ผู้ปกครองขู่จะร้องเรียนครู", "ผู้บริหาร"),
    ("สงสัยเด็กในห้องโดนตีที่บ้าน มีรอยช้ำ", "1300"), ("ลูกสาวไม่ยอมทำการบ้านทุกวัน", "ตาราง"),
    ("ลูกชายร้องไห้ทุกเช้าไม่อยากไปโรงเรียน", "ครู"), ("ลูกติดยูทูบมาก", "กติกา"),
    ("ครูบรรจุใหม่ เตรียมสอนไม่ทัน", "ครูพี่เลี้ยง"),
])
def test_teachers_and_parents(text, must):
    assert must in compose(text)


@pytest.mark.parametrize("text,not_key", [
    ("อยากเรียนภาษาจีน", "abroad_china"),                 # เรียนภาษาที่ไทย ≠ ไปเรียนต่อจีน
    ("อยากเรียนภาษาญี่ปุ่นด้วยตัวเอง", "abroad_japan"),
    ("ไปเที่ยวญี่ปุ่นเดือนหน้า", "abroad_japan"),
    ("ลูกสอบตกคณิต ม.2 ทำไงดี", "parent_grades_tutor"),  # สอบตกยังได้คำตอบเรื่องสอบตก
    ("แฟนเป็นครู", "teacher_burnout"),
])
def test_neighbours_are_not_pulled_in(text, not_key):
    assert _key(text) != not_key


def test_specific_knowledge_comes_before_general_study():
    keys = [k for k, _, _ in KNOWLEDGE]
    assert keys.index("parent_grades_tutor") < keys.index("exam_fail")
    assert keys.index("abroad_japan") < keys.index("scholarship_abroad")


def test_every_answer_respects_the_three_path_canon():
    for key, _, d in EDU:
        assert 1 <= len(d["paths"]) <= 3, key
        assert d["ask"].endswith("?"), key
    assert len({k for k, _, _ in KNOWLEDGE}) == len(KNOWLEDGE)    # ไม่มี key ซ้ำกับความรู้เดิม
