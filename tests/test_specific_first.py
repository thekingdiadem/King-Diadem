"""หัวข้อกว้างทับหัวข้อเฉพาะ — ไล่จากประโยคทั้งหมดในเทสต์ (4,930 ประโยค) หาจุดที่คำตอบผิดเรื่อง

หลักตัดสินจากพิมพ์เขียว LYLA: ชีวิตรอดมาก่อน (คนไม่หายใจ > ภัยรอบตัว) · ทางเลือกที่จริงและเจาะจงที่สุด · ไม่เร่งโดยไม่จำเป็น
ข้อที่ร้ายแรงที่สุด: "ยายเป็นลมแดด หมดสติ ไม่หายใจ" เคยได้คำแนะนำคลื่นความร้อน (ย้ายเข้าร่ม เช็ดตัว) ไม่มี CPR
"""
import pytest

from core.kernel_voice import assess, compose

CPR = ("กดหน้าอก", "CPR", "compressions")


@pytest.mark.parametrize("text", [
    "ยายเป็นลมแดด หมดสติ ไม่หายใจ",
    "grandma has heatstroke, she collapsed and is not breathing",
    "my kid almost drowned and is not breathing",
])
def test_not_breathing_gets_cpr_before_anything_else(text):
    assert assess(text)["topics"][0] == "health_emergency"
    assert any(c in compose(text) for c in CPR)


@pytest.mark.parametrize("text,topic,must", [
    ("ฝุ่นPM2.5หนักมาก ลูกหอบกำเริบ หายใจไม่ออก ยาพ่นไม่ช่วย", "kp_child_breath", "ปากเขียว"),
    ("น้ำท่วม ลูกตกน้ำ ช่วยขึ้นมาแล้ว ไอไม่หยุด", "kp_near_drowning", "8 ชั่วโมง"),
    ("กินเหล้าเถื่อนเมื่อวาน วันนี้ตาพร่ามัว ปวดท้อง", "kp_methanol", "ขวดเดียวกัน"),
    ("ลุงกินเหล้าต้มเอง ตอนนี้มองไม่เห็น หายใจหอบ", "kp_methanol", "1367"),
    ("เพื่อนดื่มเหล้าแล้วหมดสติ ปลุกไม่ตื่น", "kp_alcohol_poisoning", "ห้ามอาบน้ำเย็น"),
    ("ยายกินยาผิด กินยาความดันไปสองรอบ", "kp_double_dose", "1367"),
    ("ติดลิฟต์อยู่ ลิฟต์ค้างระหว่างชั้น ไฟดับ อากาศเริ่มอึดอัด", "kp_elevator", "199"),
    ("jellyfish sting my kid screaming and red welts all over", "kp_jellyfish", "vinegar"),
    ("I'm addicted to gambling and in debt", "kp_gambling", "1-800-GAMBLER"),
])
def test_specific_topic_answers_instead_of_broad_one(text, topic, must):
    assert assess(text)["topics"][0] == topic
    assert must in compose(text)


def test_calm_topic_keeps_a_calm_score_unless_there_are_danger_signs():
    assert assess("ยายกินยาผิด กินยาความดันไปสองรอบ")["text_risk"] == 60
    assert assess("ยายกินยาความดันไปสองรอบ ตอนนี้หน้ามืดจะเป็นลม")["text_risk"] >= 85
    assert assess("ติดลิฟต์ หายใจไม่ออก จะเป็นลม")["text_risk"] >= 85
    assert assess("กินยานอนหลับซ้ำสองรอบ อยากหลับไม่ตื่น")["crisis"]


def test_counting_word_luuk_is_not_a_child():
    # "ลูกโป่ง" "หลายลูก" — ไม่ใช่ลูก (เด็ก) ชักจากไข้
    assert "kp_febrile_seizure" not in assess("เพื่อนสูดลูกโป่งไนตรัสไปหลายลูก ตอนนี้ล้มชัก")["topics"]
    assert assess("ลูก 2 ขวบชักตอนไข้สูง")["topics"][0] == "kp_febrile_seizure"


@pytest.mark.parametrize("text,broad", [
    # ที่หัวข้อกว้างควรชนะ — ปลอดภัยหรือปัจจัยสี่มาก่อน
    ("my friend is trafficked and her passport was taken", "trafficking"),
    ("my teacher touched me", "sexual_abuse"),
    ("พ่อรู้ว่าเราเป็นเกย์ ไล่ออกจากบ้าน ตอนนี้นอนข้างถนน", "basic"),
    ("แฟนตบหน้าแล้วยึดโทรศัพท์ ไม่ให้เจอเพื่อน", "violence"),
    ("หลานเลียน้ำยาบุหรี่ไฟฟ้า", "overdose"),
])
def test_broad_topic_still_wins_when_it_is_the_safer_answer(text, broad):
    assert assess(text)["topics"][0] == broad
