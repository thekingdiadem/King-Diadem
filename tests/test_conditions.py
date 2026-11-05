"""ตัวตรวจแบบเงื่อนไข (core/conditions.py) — ใคร × ทำอะไร × กับอะไร แทนรายการวลี
เจ้าของโปรเจกต์: "มันต้องเป็นเงื่อนไขนะ ไม่งั้นเดี๋ยวคนมันก็มีแอปโกงใหม่ หรือวิธีโกงแบบใหม่อีก"
เทสต์นี้ใช้ของ/แอป/วิธีที่ไม่มีชื่ออยู่ในโค้ด เพื่อพิสูจน์ว่าจับจาก "ประเภท" ได้จริง และไม่เตือนผิดกับเรื่องปกติที่คล้ายกัน"""
import pytest

from core import conditions as cd
from core.kernel_voice import assess, compose
from scripts.blind_score import detected


@pytest.mark.parametrize("text,cls", [
    # เด็ก × กลืน/กัด/เลีย × สิ่งที่ไม่ใช่อาหาร (ชื่อสินค้าใหม่ก็จับได้จากประเภท)
    ("ลูกสามขวบกัดก้อนซักผ้าแตก", "emergency"), ("หลานเลียน้ำยาบุหรี่ไฟฟ้า", "emergency"),
    ("my son drank lamp oil from the shelf", "emergency"), ("my 2 year old ate some of grandma's blood pressure pills", "emergency"),
    ("เด็กกินยาความดันของยายไปหลายเม็ด", "emergency"), ("baby chewed a laundry capsule", "emergency"),
    # เตรียมตัวเผื่อตัวเองไม่อยู่ (ส่วนตัว + ซ้ำๆ)
    ("แอบอัดคลิปถึงลูกไว้ เผื่อฉันไม่อยู่แล้ว", "self_harm"), ("I've been writing letters to my kids for when I'm gone", "self_harm"),
    # ค้นหาว่าต้อง "แค่ไหน" ถึงพอ
    ("อยากรู้ว่าตึกกี่ชั้นถึงจะไม่รอด", "self_harm"), ("been googling how many pills is a lethal dose", "self_harm"),
    # มิจฉาชีพตามพฤติกรรม — แอป/แพลตฟอร์มไหนก็ได้
    ("มีคนโอนเงินเข้ามาเองแล้วโทรมาขอให้โอนคืนเข้าอีกบัญชี", "scam"),
    ("a loan app deposited money i never applied for and now they're demanding interest", "scam"),
    ("เพื่อนชวนลงทุนคริปโต กำไร 3% ต่อวัน", "scam"), ("guaranteed 2x returns in 30 days on gold trading", "scam"),
    # ความจำเป็นพื้นฐาน × ขาด/ถูกตัด/ถูกไล่
    ("ค้างค่าน้ำสามเดือน การประปาจะมาตัด", "distress"), ("ไม่มีเงินซื้อนมผงให้ลูก", "distress"),
    ("เจ้าของห้องไล่ออกสิ้นเดือนนี้ ไม่มีที่ไป", "distress"), ("the power company is shutting off our electricity friday", "distress"),
    ("we've been staying in our car since we lost the apartment, nowhere to sleep", "distress"),
])
def test_conditions_catch_new_cases_by_type(text, cls):
    assert cls in detected(assess(text)), (text, assess(text)["topics"])


@pytest.mark.parametrize("text", [
    "ลูกกินข้าวเก่งมาก", "ลูกกินยาแก้ไข้ตามหมอสั่งแล้วหายดี", "ซื้อน้ำยาล้างจานยี่ห้อไหนดี", "my son ate a lot of pizza",
    "ควรเขียนพินัยกรรมยังไงเผื่อวันที่ฉันไม่อยู่", "เขียนจดหมายถึงแม่ทุกคืนตอนเรียนต่างประเทศ", "how high a fall can an iphone survive",
    "อยากรู้ว่าตึกใบหยกสูงกี่ชั้น", "เพื่อนโอนเงินคืนที่ยืมไปแล้ว", "double the recipe for tomorrow", "I want to double my workout reps in a week",
    "หุ้นตัวนี้ขึ้นมาสองเท่าในห้าปี", "ค่าไฟเดือนนี้แพงจัง", "เดือนนี้ค่าเช่าขึ้น 500", "we slept in the car on our road trip, so fun", "ไปซื้อกับข้าวมาแล้ว",
])
def test_similar_ordinary_sentences_raise_no_new_alarm(text):
    assert not cd.check(text), (text, cd.check(text))


def test_each_rule_needs_all_its_parts():
    assert not cd.check("ลูกกัด")                        # มีแค่ใคร × ทำอะไร
    assert not cd.check("ก้อนซักผ้าแตก")                  # มีแค่สิ่งของ
    assert not cd.check("โอนเงินเข้ามาเอง")               # เงินเข้า แต่ยังไม่มีการทวง
    assert not cd.check("กำไร 3% ต่อวัน")                 # ไม่มีเรื่องเงิน/ลงทุน... มี "กำไร" แต่ไม่มีคำว่าเงินลงทุน
    assert cd.check("กำไร 3% ต่อวัน ลงทุนแค่หมื่นเดียว")[0].scam == "guarantee"


def test_conditions_never_downgrade_a_crisis():
    a = assess("อยากตาย ลูกกินยาความดันไปหลายเม็ดด้วย")
    assert a["crisis"]


def test_child_ingestion_answer_gives_poison_center_and_ems():
    out = compose("ลูกสามขวบกัดก้อนซักผ้าแตก")
    assert "1367" in out or "1669" in out
