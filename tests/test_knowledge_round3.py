"""รอบ 3: ผู้สูงอายุ · แรงงานข้ามชาติ · เด็ก — ทุกข้อในนี้เคยได้คำตอบกลาง หรือได้คำตอบผิดเรื่อง

เช่น "พ่ออายุ 80 จู่ๆ สับสน" (0/100) · "ลูก 2 ขวบชักตอนไข้สูง" (0/100) · "เด็กถูกลืมไว้ในรถ" (0/100) ·
"มีคนแปลกหน้าแชทกับลูกสาวขอรูป" (0/100) · "ถูกหลอกมาทำงาน บังคับไม่ให้ออก" (ได้ขั้นตอนขอเงินคืน)
"""
import pytest

from core.kernel_voice import assess, compose

CASES = [
    # ผู้สูงอายุ
    ("พ่ออายุ 80 จู่ๆ สับสน พูดไม่รู้เรื่อง ตั้งแต่เมื่อวาน", "kp_delirium", "ติดเชื้อ", 80),
    ("ยายกินยาซ้ำ ลืมว่ากินไปแล้ว", "kp_double_dose", "1367", 60),
    ("my grandmother took her blood pressure pills twice by mistake", "kp_double_dose", "pill organiser", 60),
    ("เบี้ยผู้สูงอายุ สมัครยังไง", "kp_elder_allowance", "สมุดบัญชี", 0),
    ("someone is taking my grandfather's pension and neglecting him", "elder_abuse", "", 75),
    ("my dad with dementia wandered off and is missing", "missing", "24 hours", 80),
    # แรงงานข้ามชาติ
    ("แรงงานพม่า นายจ้างยึดพาสปอร์ตไว้", "labor", "บังคับใช้แรงงาน", 0),
    ("ถูกหลอกมาทำงาน บังคับให้ทำงานไม่ให้ออกไปไหน", "trafficking", "การค้ามนุษย์", 80),
    ("i'm a migrant worker and haven't been paid for 2 months", "kp_migrant_wages_en", "same wage rights", 45),
    ("แรงงานต่างด้าวเจ็บจากงาน นายจ้างไม่พาไปหาหมอ", "kp_work_injury", "กองทุนเงินทดแทน", 45),
    ("i got injured at work and my boss won't pay", "kp_work_injury", "workers' compensation", 45),
    # เด็ก
    ("เด็กถูกลืมไว้ในรถ", "kp_child_in_car", "ทุบกระจก", 85),
    ("my toddler was left in the hot car", "kp_child_in_car", "break the window", 85),
    ("ลูกตกน้ำ ช่วยขึ้นมาแล้ว ไอ", "kp_near_drowning", "8 ชั่วโมง", 85),
    ("my kid almost drowned in the pool and is coughing", "kp_near_drowning", "rescue breaths", 85),
    ("ลูก 2 ขวบชักตอนไข้สูง", "kp_febrile_seizure", "ห้ามงัดปาก", 85),
    ("my baby had a seizure with fever", "kp_febrile_seizure", "time it", 85),
    ("ลูกท้องเสีย ถ่ายเป็นน้ำ ไม่ฉี่", "kp_child_dehydration", "ORS", 80),
    ("my baby has diarrhea and no wet diapers", "kp_child_dehydration", "teaspoon", 80),
    ("มีคนแปลกหน้าแชทกับลูกสาวขอรูป", "kp_grooming_th", "เก็บหลักฐาน", 75),
    ("i think my neighbor's kid is being abused", "kp_child_abuse_report_en", "don't need proof", 75),
    ("ลูกเล่นเกมทั้งวัน ไม่ยอมนอน", "child_gaming", "ตกลงกติกา", 0),
]


@pytest.mark.parametrize("text,topic,must,risk", CASES)
def test_round3_specific_answer(text, topic, must, risk):
    a = assess(text)
    assert a["topics"][0] == topic, a["topics"]
    assert a["text_risk"] >= risk
    assert must in compose(text)


@pytest.mark.parametrize("text", [
    "ลูกชอบชักว่าวตอนหน้าร้อน", "ลูกชักชวนเพื่อนมาเล่นที่บ้าน", "ลืมกระเป๋าไว้ในรถ", "ลูกนั่งรถไปโรงเรียน",
    "ยายอายุ 85 แข็งแรงดี วันนี้ไปตลาด", "แม่สับสนเรื่องแอปธนาคาร", "เบี้ยผู้สูงอายุเข้าแล้ว",
    "นายจ้างเอาพาสปอร์ตไปต่อวีซ่าให้ แล้วคืนแล้ว", "ลูกเคยไข้ชักตอนเด็ก ตอนนี้โตแล้วไม่เป็นแล้ว", "ลูกเล่นเกมวันละชั่วโมง", "ลูกท้องเสียนิดหน่อย ยังฉี่ปกติ กินได้",
    "my kid loves swimming in the pool", "we left the car at home", "i took my vitamins this morning",
    "the migrant worker exhibition was interesting", "my grandma is a bit forgetful but fine",
])
def test_round3_no_false_alarm(text):
    a = assess(text)
    assert a["text_risk"] < 50 and not any(t.startswith("kp_") or t in ("trafficking", "missing") for t in a["topics"]), a["topics"]
