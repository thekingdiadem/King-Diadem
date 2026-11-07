"""เจตนาของข้อความที่ไม่เข้าหัวข้อ (core/intent.py) — แทนคำตอบกลาง "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน"

วัดจากประโยคในเทสต์ 5,674 ประโยค: 41% เคยได้คำตอบกลาง ("เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว — ปัญหาที่แท้จริงคืออะไร")
แม้ข้อความนั้นจะเป็นการบอกฝันดี แบ่งปันเรื่องดี ห่วงคนอื่น หรือตั้งเป้าหมาย
"""
import pytest

from core import intent
from core.kernel_voice import assess, compose

GENERIC = ("ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน", "Let's lay this out step by step.")


@pytest.mark.parametrize("text,kind,must", [
    ("ready to crash, goodnight", "closing_night", "Good night"),
    ("ง่วงแล้ว ไปนอนก่อนนะ", "closing_night", "ฝันดี"),
    ("ok bye for now", "closing_bye", "Take care"),
    ("this song slaps so hard", "share_good", "sounds really nice"),
    ("ไปเที่ยวทะเลมา สนุกมาก", "share_good", "ฟังแล้วดีจัง"),
    ("my mom is not ok", "worry_other", "danger signs"),
    ("แม่ดูไม่ค่อยโอเคช่วงนี้", "worry_other", "1323"),
    ("I want to wake up early", "goal", "smallest version"),
    ("อยากตื่นเช้า", "goal", "15 นาที"),
    ("สแกนคิวอาร์จ่ายเงินร้านกาแฟปลอดภัยไหม", "safety_q", "1441"),
    ("is it safe to use public wifi for banking?", "safety_q", "official channel"),
])
def test_intent_replaces_the_generic_answer(text, kind, must):
    assert intent.detect(text) == kind
    out = compose(text)
    assert not out.startswith(GENERIC) and must in out


@pytest.mark.parametrize("text", [
    "อยากตาย ไปนอนก่อนนะ",               # วิกฤตต้องได้คำตอบวิกฤต ไม่ใช่ "ฝันดี"
    "goodbye forever, good night",      # บอกลาตลอดไป ห้ามตอบแบบคุยเล่น
    "เพิ่งรู้ว่าแฟนมีคนอื่น",             # ปัญหาที่ไม่มีคำลบ ห้ามได้ "ฟังแล้วดีจัง"
])
def test_grave_or_problem_messages_never_get_small_talk(text):
    out = compose(text)
    assert not any(x in out for x in ("ฝันดี", "Good night", "ฟังแล้วดีจัง", "sounds really nice"))


def test_intent_never_overrides_a_detected_topic():
    # มีหัวข้อแล้ว (ความรัก/เงิน) — คำตอบของหัวข้อมาก่อน
    a = assess("ทะเลาะกับแฟน ไปนอนก่อนนะ")
    assert a["topics"]
    assert "ฝันดี" not in compose("ทะเลาะกับแฟน ไปนอนก่อนนะ")


@pytest.mark.parametrize("text,topic,risk", [
    ("i took 30 paracetamol", "overdose", 85),            # เดิม Risk 0 คำตอบกลาง
    ("I've taken like 12 tylenol", "overdose", 85),
    ("กินพาราไป 20 เม็ด", "overdose", 85),
    ("กินพาราเกิน 8 เม็ดต่อวันอันตรายไหม", "kp_paracetamol", 45),   # ถามขนาดยา → คำตอบขนาดยา
    ("how many tylenol can i take a day", "kp_paracetamol", 45),
])
def test_paracetamol_dose_questions_and_overdoses(text, topic, risk):
    a = assess(text)
    assert a["topics"][0] == topic and a["text_risk"] >= risk


@pytest.mark.parametrize("text", ["took 2 tylenol for my headache", "i took 1 advil", "ซื้อพาราที่ร้านยา"])
def test_normal_doses_are_not_an_emergency(text):
    a = assess(text)
    assert "overdose" not in a["topics"] and a["text_risk"] < 50
