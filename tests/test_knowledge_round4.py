"""รอบ 4: คนพิการ · ระยะท้ายของชีวิต · นักเรียนนักศึกษา — ทุกข้อเคยได้ 0/100 หรือได้คำตอบผิดเรื่อง

เช่น "ลูกเป็นออทิสติก อาละวาด เอาหัวโขกพื้น" เคยได้คำตอบวิกฤตของผู้ใช้เอง (ให้พ่อแม่โทร 1323 ไปอยู่ใกล้คนอื่น) ·
"แม่ใกล้เสียแล้ว" (ยังไม่เสีย) เคยได้ "เสียใจด้วย การสูญเสีย…" · "กู้ กยศ ไม่ไหว" เคยได้เทคนิคอ่านหนังสือ ·
"ถูกหลอกเปิดบัญชีม้า" เคยได้ขั้นตอนขอเงินคืน ทั้งที่คนพิมพ์คือคนที่อาจถูกดำเนินคดี
"""
import pytest

from core.kernel_voice import assess, compose

CASES = [
    # คนพิการ
    ("ลูกเป็นออทิสติก อาละวาดทำร้ายตัวเอง", "kp_meltdown", "ลดสิ่งกระตุ้น", 60),
    ("ลูกเป็นออทิสติก อาละวาด เอาหัวโขกพื้น", "kp_meltdown", "หมอนหรือเบาะ", 60),
    ("my autistic son is having a meltdown and hitting his head", "kp_meltdown", "cushion", 60),
    ("บัตรคนพิการ ทำยังไง", "kp_disability_card", "ใบรับรองความพิการ", 0),
    ("how do i get a disability card in thailand", "kp_disability_card", "medical certificate", 0),
    ("คนพิการถูกนายจ้างเลิกจ้างเพราะพิการ", "kp_disability_discrimination", "1479", 35),
    ("i was fired because i'm deaf", "kp_disability_discrimination", "EEOC", 35),
    # ระยะท้ายของชีวิต
    ("แม่ป่วยระยะสุดท้าย หายใจเฮือก ทำไงดี", "kp_end_of_life", "ครืดคราด", 70),
    ("แม่ใกล้เสียแล้ว ญาติควรทำอะไร", "kp_end_of_life", "จับมือ", 70),
    ("my dad is dying at home and his breathing is rattling", "kp_end_of_life", "hospice", 70),
    ("ผู้ป่วยมะเร็งระยะท้าย ปวดมาก ยาไม่พอ", "kp_palliative_pain", "มอร์ฟีน", 60),
    ("my mom is in hospice and in so much pain", "kp_palliative_pain", "Morphine", 60),
    ("อยากทำหนังสือแสดงเจตนาไม่รับการรักษา", "kp_living_will", "ม.12", 0),
    ("how do i make a living will", "kp_living_will", "advance directive", 0),
    # นักเรียนนักศึกษา
    ("นักเรียนถูกรุ่นพี่รับน้องรุนแรง บังคับดื่มเหล้า", "kp_hazing", "ความสมัครใจ", 65),
    ("my roommate drank way too much and won't wake up", "kp_alcohol_poisoning", "No cold showers", 85),
    ("เพื่อนเมาหนัก ปลุกไม่ตื่น", "kp_alcohol_poisoning", "ห้ามอาบน้ำเย็น", 85),
    ("สอบตก อยากลาออกจากมหาลัย", "kp_exam_fail", "ลาพักการศึกษา", 30),
    ("i failed my exams and my parents will kill me", "kp_exam_fail", "with a plan", 30),
    ("กู้ กยศ ไม่ไหว จ่ายไม่ได้", "kp_student_loan", "ปรับโครงสร้างหนี้", 40),
    ("ครูส่งข้อความลามกให้ลูกสาว", "kp_educator_harassment", "คุรุสภา", 70),
    ("my professor is sexually harassing me", "kp_educator_harassment", "Title IX", 70),
    ("นักศึกษาถูกหลอกเปิดบัญชีม้า", "kp_money_mule", "ระงับบัญชี", 65),
    ("i was offered money to let someone use my bank account", "kp_money_mule", "money laundering", 65),
]


@pytest.mark.parametrize("text,topic,must,risk", CASES)
def test_round4_specific_answer(text, topic, must, risk):
    a = assess(text)
    assert a["topics"][0] == topic, a["topics"]
    assert a["text_risk"] >= risk
    assert must in compose(text)


def test_autistic_child_self_injury_is_not_the_parents_crisis():
    for t in ("ลูกเป็นออทิสติก อาละวาด เอาหัวโขกพื้น", "ลูกเป็นออทิสติก อาละวาดทำร้ายตัวเอง"):
        assert not assess(t)["crisis"]
        assert "ไปอยู่ใกล้คนอื่น" not in compose(t)
    assert assess("ฉันอยากทำร้ายตัวเอง")["crisis"]          # วิกฤตของผู้ใช้เองยังจับได้เหมือนเดิม


def test_near_death_is_not_answered_as_bereavement():
    out = compose("แม่ใกล้เสียแล้ว ญาติควรทำอะไร")
    assert "การสูญเสีย" not in out and "เสียใจด้วย" not in out


@pytest.mark.parametrize("text", [
    "ลูกเป็นออทิสติก เรียนเก่งมาก", "my autistic son loves trains", "บัตรคนพิการของแม่ใช้ขึ้นรถไฟฟรีได้ไหม",
    "พี่ชายตาบอด แต่ทำงานเก่งมาก", "ดูซีรีส์ตอนจบ ตัวเอกใกล้ตาย ร้องไห้เลย", "the movie was about a dying king",
    "ไปงานรับน้องสนุกมาก รุ่นพี่ใจดี", "my professor is great and very helpful", "ครูส่งข้อความแจ้งการบ้าน",
    "สอบตกวิชาเดียว แต่ไม่เป็นไร จะลงใหม่", "จ่าย กยศ ครบแล้ว", "เปิดบัญชีใหม่ที่ธนาคาร", "i opened a savings account",
    "เพื่อนเมานิดหน่อย ร้องเพลงคาราโอเกะ", "we were drinking and having fun",
])
def test_round4_no_false_alarm(text):
    a = assess(text)
    assert a["text_risk"] < 50 and not any(t.startswith("kp_") for t in a["topics"]), a["topics"]
