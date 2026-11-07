"""โหมดสงคราม/ความขัดแย้ง — พี่ขอให้ "รองรับสงครามโลกครั้งที่ 3"

เดิม "ได้ยินไซเรนเตือนภัยทางอากาศ" "สงครามเกิดแล้ว ต้องอพยพ" "air raid sirens are going off" ได้ Risk 0
และ "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน" · ขั้นตอนจากแนวทางป้องกันภัยพลเรือน (Ready.gov · กาชาด · ปภ.)
"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text,must", [
    ("ได้ยินไซเรนเตือนภัยทางอากาศ ทำไงดี", "ที่หลบภัย"),
    ("ปืนใหญ่ตกใกล้หมู่บ้าน ต้องทำอะไร", "ห้ามแตะวัตถุที่ยังไม่ระเบิด"),
    ("มีโดรนทิ้งระเบิดแถวบ้าน", "ผนังกั้น"),
    ("air raid sirens are going off right now", "inner room"),
    ("missiles incoming what do we do", "attacks often come in waves"),
    ("ระเบิดนิวเคลียร์ลงแล้ว ต้องทำอะไร", "24 ชั่วโมง"),
    ("there was a nuclear explosion in the city", "potassium iodide"),
    ("สงครามเกิดแล้ว ต้องอพยพ เตรียมอะไรบ้าง", "จุดนัดพบ"),
    ("ปะทะกันที่ชายแดน ทหารให้อพยพ", "คำสั่งอพยพ"),
    ("war has broken out in my country", "evacuation orders"),
])
def test_active_war_situations_get_civil_defence_steps(text, must):
    a = assess(text)
    assert a["text_risk"] >= 60 and a["disaster"] and a["disaster"]["active"]
    assert must in compose(text)


@pytest.mark.parametrize("text,must", [
    ("ถ้าเกิดสงครามโลกครั้งที่ 3 ต้องเตรียมตัวยังไง", "กระเป๋าฉุกเฉิน"),
    ("how do i prepare for world war 3", "family plan"),
    ("ถ้าน้ำท่วมต้องเตรียมอะไร", "3 วันแรก"),
    ("how do i prepare for an earthquake", "battery radio"),
])
def test_preparing_ahead_gets_a_calm_kit_and_plan(text, must):
    a = assess(text)
    assert a["text_risk"] < 50 and not (a["disaster"] and a["disaster"]["active"])
    assert must in compose(text)


@pytest.mark.parametrize("text", [
    "สงครามโลกครั้งที่ 2 เกิดขึ้นเพราะอะไร", "สงครามราคามือถือ ซื้อตอนไหนดี", "อารมณ์ระเบิด ทะเลาะกับแฟน",
    "the war movie was great", "i hate war", "เกมสงครามสนุกมาก",
])
def test_history_idioms_and_games_are_not_an_attack(text):
    a = assess(text)
    assert a["text_risk"] < 50 and not (a["disaster"] and a["disaster"]["active"])


def test_wounded_person_during_attack_still_gets_cpr_first():
    out = compose("โดนระเบิด มีคนหมดสติ ไม่หายใจ")
    assert "กดหน้าอก" in out
