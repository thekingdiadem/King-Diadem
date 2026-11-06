"""คุณแม่ตั้งครรภ์ (core/pregnancy_guide.py) — สัญญาณอันตรายต้องไปถึงคำตอบด่วนเสมอ · อยู่คนเดียวได้แผนที่ใช้ได้จริง

เดิม "i am 30 weeks pregnant and alone, my water just broke" ได้คำตอบเรื่องท้องไม่พร้อม
และ "ลูกดิ้นน้อยลง" ได้คำตอบกลาง ทั้งที่ต้องไปโรงพยาบาลเดี๋ยวนี้
"""
import pytest

from core import pregnancy_guide as pg
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text,kind,must", [
    ("ตั้งครรภ์ 32 สัปดาห์ ลูกดิ้นน้อยลงตั้งแต่เมื่อวาน", "movement", "10 ครั้งใน 2 ชั่วโมง"),
    ("i am 30 weeks pregnant and alone, my water just broke", "water", "labour ward"),
    ("ท้อง 8 เดือน ปวดหัวมาก ตาพร่า เท้าบวม", "preeclampsia", "ครรภ์เป็นพิษ"),
    ("ท้อง 6 เดือน มีเลือดออกนิดหน่อย", "bleeding", "ไม่ว่าจะมากหรือน้อย"),
    ("ตั้งครรภ์ 34 สัปดาห์ เจ็บท้องถี่ทุก 5 นาที", "labor", "37 สัปดาห์"),
    ("คนท้องชัก หมดสติ", "seizure", "1669"),
])
def test_danger_signs_get_urgent_answer(text, kind, must):
    assert kind in pg.dangers(text)
    a = assess(text)
    # หมดสติ: คำตอบฉุกเฉินทั่วไป (CPR + จับนอนตะแคง) มาก่อนได้ — สำคัญกว่าเรื่องครรภ์ในนาทีนั้น
    top = ("preg_danger", "health_emergency") if kind == "seizure" else ("preg_danger",)
    assert a["topics"][0] in top and "preg_danger" in a["topics"] and a["text_risk"] >= 85
    assert must in compose(text)


@pytest.mark.parametrize("text", ["ปวดท้องมาก กินอะไรไม่ได้", "ท้องเสีย มีไข้", "my stomach hurts after lunch"])
def test_belly_pain_is_not_pregnancy(text):
    """ "ท้อง" แปลว่าพุงด้วย — ต้องไม่ถูกตีความเป็นการตั้งครรภ์"""
    assert not pg.is_pregnant(text) and "preg_danger" not in assess(text)["topics"]


def test_alone_gets_a_real_plan_not_loneliness():
    t = "ท้อง 7 เดือน อยู่คนเดียว ไม่มีใครช่วยเลย"
    assert assess(t)["topics"][0] == "preg_alone"
    r = compose(t)
    assert "1669" in r and "1300" in r and "กระเป๋าคลอด" in r


def test_unplanned_pregnancy_keeps_its_answer():
    assert assess("ท้องไม่พร้อม อายุ 16 กลัวบอกพ่อแม่")["topics"][0] == "pregnancy"


def test_care_questions_get_basics():
    a = assess("ตั้งครรภ์ได้ 20 สัปดาห์ อยากรู้ว่ากินอะไรดี")
    assert a["topics"][0] == "preg_care" and "โฟลิก" in compose("ตั้งครรภ์ได้ 20 สัปดาห์ อยากรู้ว่ากินอะไรดี")


def test_guide_page_and_sitemap(app_module):
    from fastapi.testclient import TestClient
    c = TestClient(app_module.app)
    r = c.get("/pregnancy")
    assert r.status_code == 200 and "<script" not in r.text                     # ไม่มีสคริปต์ เปิดได้แม้เน็ตช้า
    for must in ("สัญญาณอันตราย", "ถ้าอยู่คนเดียว", "tel:1669", "10 ครั้งใน 2 ชั่วโมง", "WHO"):
        assert must in r.text, must
    assert "/pregnancy</loc>" in c.get("/sitemap.xml").text


def test_guide_never_quotes_a_book():
    # เขียนเองจากแนวทางสาธารณะ — อ้างอิงเป็นหน่วยงาน ไม่ใช่หนังสือที่มีลิขสิทธิ์
    assert all(any(k in s for k in ("WHO", "กรมอนามัย", "ACOG", "AAP")) for s in pg.SOURCES)


# ── หลังคลอดและทารกแรกเกิด ── เดิม "ลูกอายุ 1 เดือน ไข้ 38.2" "ลูกแรกเกิดตัวเหลือง ไม่ดูดนม" และ
#    "I just had a baby and I feel like I could hurt her" ได้คำตอบกลาง ความเสี่ยง 0/100
@pytest.mark.parametrize("text,topic,must", [
    ("คลอดได้ 5 วัน เลือดออกเยอะมาก ชุ่มผ้าอนามัยทุกชั่วโมง", "post_danger", "ตกเลือดหลังคลอด"),
    ("หลังผ่าคลอด เจ็บหน้าอก หายใจไม่อิ่ม", "post_danger", "ลิ่มเลือด"),
    ("gave birth last week, heavy bleeding and fever", "post_danger", "Soaking a pad"),
    ("ลูกอายุ 1 เดือน ไข้ 38.2", "newborn_danger", "อย่าให้ยาลดไข้เอง"),
    ("ลูกแรกเกิด 4 วัน ตัวเหลืองมาก ไม่ค่อยดูดนม", "newborn_danger", "ฝ่ามือฝ่าเท้า"),
    ("my 3 week old has a fever", "newborn_danger", "under 3 months"),
    ("I just had a baby and I feel like I could hurt her", "post_harm", "safe place"),
    ("หลังคลอด กลัวจะเขย่าลูก ร้องไม่หยุดเลย", "post_harm", "1323"),
])
def test_after_birth_and_newborn_dangers(text, topic, must):
    a = assess(text)
    assert a["topics"][0] == topic and a["text_risk"] >= 85
    assert must in compose(text)


@pytest.mark.parametrize("text", ["เด็กมีไข้ 3 วันแล้ว", "ลูก 5 ขวบ มีไข้", "ลูกสาว 12 เดือน ไข้"])
def test_older_child_fever_is_not_newborn(text):
    """ "3 วัน" ที่หมายถึงป่วยมา 3 วัน ไม่ใช่อายุ 3 วัน"""
    assert not pg.newborn_dangers(text) and "newborn_danger" not in assess(text)["topics"]


def test_postnatal_low_mood_keeps_its_answer():
    assert assess("หลังคลอดร้องไห้ทุกวัน ไม่อยากอุ้มลูก")["topics"][0] == "postpartum"
