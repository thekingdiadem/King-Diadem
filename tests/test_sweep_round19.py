"""รอบหาบั๊ก 19: สัตว์เลี้ยงกินของมีพิษ — เคยกลายเป็นยาเกินขนาดของคน/โดนแมวกัด/ไม่เห็นเลย"""
import pytest

from core.kernel_voice import assess, compose
from ENGINE.risk_engine import evaluate_risk


@pytest.mark.parametrize("t", ["หมากินยาเบื่อหนู", "แมวกินยาพาราของฉัน", "หมาที่บ้านกินช็อกโกแลตไปเยอะ",
                               "น้องหมากินองุ่นไป 10 ลูก", "แมวกัดดอกลิลลี่", "my dog ate chocolate"])
def test_pet_poisoning(t):
    a = assess(t)
    assert "pet_poison" in a["topics"]
    assert not {"overdose", "first_aid", "health"} & set(a["topics"])
    assert a["text_risk"] >= 55


def test_pet_poison_is_not_human_overdose_in_risk_engine():
    assert not evaluate_risk("หมากินยาเบื่อหนู")["overdose"]


@pytest.mark.parametrize("t", ["ลูกกับหมากินยาเบื่อหนูไปทั้งคู่", "หมากับลูกกินยาเบื่อหนู",
                               "หมากินยาเบื่อหนู แล้วฉันก็กินยานอนหลับไปทั้งแผง"])
def test_a_person_also_poisoned_stays_overdose(t):
    assert "overdose" in assess(t)["topics"]


@pytest.mark.parametrize("t", ["หมากินช็อกโกแลตได้ไหม", "แมวกินอาหารเม็ดไม่ยอมกินข้าว"])
def test_questions_and_food_are_not_emergencies(t):
    assert "pet_poison" not in assess(t)["topics"]


def test_dog_bite_is_still_first_aid():
    a = assess("โดนหมากัด")
    assert "first_aid" in a["topics"] and "pet_poison" not in a["topics"]


def test_reply_sends_to_vet_first_without_rodent_advice():
    out = compose("หมากินยาเบื่อหนู", voice_mode="vega")
    assert "1)" in out and out.index("โรงพยาบาลสัตว์") < out.index("2)")
    assert "เรื่องหนู" not in out
    assert "1669" not in out


def test_cat_gets_cat_specific_warning():
    assert "แมวไวต่อพิษ" in compose("แมวกินยาพาราของฉัน")


# ── เหตุด่วนที่เคยได้ Risk 0 ──────────────────────────────────────────
@pytest.mark.parametrize("t,topic", [
    ("เด็กติดอยู่ในรถตากแดด", "health_emergency"), ("ลืมลูกไว้ในรถ", "health_emergency"),
    ("เพื่อนเมาหลับไม่ปลุกไม่ตื่น อ้วกด้วย", "health_emergency"),
    ("แม่เป็นเบาหวาน หน้ามืดจะเป็นลม", "health_emergency"),
    ("พ่อเมาแล้วไล่ฟันแม่", "violence"),
    ("โดนแฟนเก่าแอบติดตามแอบดูมือถือ", "threat"), ("มีผู้ชายแปลกหน้าตามมาถึงหน้าบ้าน", "threat"),
    ("แฟนบังคับให้ส่งรูปโป๊", "sextortion"),
    ("แม่ทิ้งลูกไว้คนเดียวสามวัน", "witness"),
])
def test_urgent_cases_detected(t, topic):
    a = assess(t)
    assert topic in a["topics"]
    assert a["text_risk"] >= 55


@pytest.mark.parametrize("t", ["ลูกอยู่ในรถกับพ่อ", "เมื่อคืนเมาจนหลับไม่รู้สึกตัว ตื่นมาปวดหัว",
                               "เล่นเกมไล่ยิงซอมบี้", "เอามีดหั่นผัก", "ทิ้งลูกไว้กับยายสามวัน"])
def test_everyday_sentences_stay_calm(t):
    a = assess(t)
    assert (a["text_risk"] or 0) < 55 and not a.get("disaster")


@pytest.mark.parametrize("t,needle", [("เด็กติดอยู่ในรถตากแดด", "ทุบกระจก"),
                                      ("เพื่อนเมาหลับไม่ปลุกไม่ตื่น อ้วกด้วย", "นอนตะแคง"),
                                      ("แม่เป็นเบาหวาน หน้ามืดจะเป็นลม", "น้ำตาลต่ำ")])
def test_specific_first_steps(t, needle):
    assert needle in compose(t)
