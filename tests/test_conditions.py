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


# ── รอบ 6: พื้นอาหาร · ฝากคนที่ต้องดูแล · ยกของรัก · แผนเฉพาะเจาะจง · ค่าใช้จ่ายใกล้ครบกำหนด ──
@pytest.mark.parametrize("text,rule", [
    ("ข้าวสารหมดบ้านแล้ว ลูกยังไม่ได้กินอะไรเลย", "food_floor"),
    ("เหลือไข่ฟองสุดท้ายในตู้", "food_floor"),
    ("we ran out of rice and the kids are hungry", "food_floor"),
    ("พ่อส่งข้อความมาว่าไม่ไหวแล้ว ฝากดูแลแม่ด้วย", "entrust_giveup"),
    ("please look after my cat, i can't go on anymore", "entrust_giveup"),
    ("แจกเสื้อผ้าไปหมดแล้ว ไม่ต้องใช้อีกแล้ว", "giveaway_final"),
    ("gave away my guitar, i won't need it", "giveaway_final"),
    ("i have already chosen the spot and the night", "plan_specific"),
    ("ค่ารักษาแม่ครบกำหนดพรุ่งนี้ แต่ยังไม่มีเงิน", "bill_due"),
])
def test_round6_conditions_catch(text, rule):
    from core.conditions import check
    assert rule in [h.rule for h in check(text)]


@pytest.mark.parametrize("text", [
    "ลูกเอาเงินบำนาญแม่ไปหมด ไม่ให้กินข้าว",          # เรื่องเงิน ไม่ใช่ข้าวหมด
    "ไข่หมดตู้แล้ว ต้องไปซื้อ",
    "ลดน้ำหนักอยู่ มื้อสุดท้ายของวันคือสลัด",
    "ฝากดูแลหมาด้วยนะ ไปเที่ยวทะเล ไม่ไหวแล้วร้อนมาก",
    "ย้ายหอใหม่ห้ามเลี้ยง เลยยกแมวให้น้า ดีที่สุดแล้ว",
    "เลือกที่กับวันจัดงานวันเกิดไว้แล้ว",
    "ค่าเทอมจ่ายพรุ่งนี้ เตรียมเงินไว้แล้ว",
])
def test_round6_conditions_do_not_overfire(text):
    from core.conditions import check
    assert not [h for h in check(text) if h.rule in ("food_floor", "entrust_giveup", "giveaway_final", "plan_specific", "bill_due")]


def test_third_party_speaker_gets_someone_topic():
    from core.kernel_voice import assess
    assert assess("พ่อส่งข้อความมาว่าไม่ไหวแล้ว ฝากดูแลแม่ด้วย")["topics"][0] == "someone"
    assert assess("ไม่ไหวแล้ว ฝากดูแลลูกด้วยนะ")["topics"][0] == "warning"


# ── มิจฉาชีพแบบโครงสร้าง 8 แบบ (จ่ายก่อนถึงจะได้ · รู้จักแค่ออนไลน์ · ลิงก์อ้างหน่วยงาน · บัตรของขวัญ
#    ญาติเดือดร้อนห้ามบอกใคร · โอนแล้วหาย · งานกดไลค์ต้องเติมเงิน · เจ้าหน้าที่สั่งอยู่ในสาย) ──
@pytest.mark.parametrize("text,rule,flag", [
    ("สินเชื่อผ่านแล้วค่ะ รบกวนชำระค่าดำเนินการก่อนเงินเข้า", "pay_first", "story"),
    ("you've won a prize, just pay a small fee to release it", "pay_first", "story"),
    ("คุยกับหนุ่มในติ๊กต็อกมาเดือนนึง ไม่เคยเจอตัว เขาให้ช่วยโอนค่าตั๋วเครื่องบิน", "online_only_money", "romance"),
    ("we never met in person but she wants me to try her crypto platform", "online_only_money", "romance"),
    ("ได้ข้อความจากไปรษณีย์ว่าพัสดุติด ให้คลิกลิงก์ชำระค่าธรรมเนียม", "link_pressure", "story"),
    ("got an email from paypal saying my account is suspended, click the link to verify", "link_pressure", "story"),
    ("สรรพากรโทรมาให้จ่ายค่าปรับด้วยบัตรเติมเงิน", "gift_card", "impersonation"),
    ("the irs said to pay the fine with google play cards", "gift_card", "impersonation"),
    ("มีคนโทรมาบอกว่าเป็นหลาน ชนคนอยู่โรงพยาบาล ขอให้โอนด่วนอย่าบอกพ่อแม่", "family_emergency", "impersonation"),
    ("โอนค่าบัตรคอนเสิร์ตไปแล้ว คนขายปิดเพจหนี", "paid_vanished", "lost"),
    ("paid for a puppy online and the seller blocked me", "paid_vanished", "lost"),
    ("งานพาร์ทไทม์ทำภารกิจรีวิวร้าน ได้ค่าคอม แต่ต้องวางเงินก่อน", "task_job", "job"),
    ("ตำรวจไซเบอร์โทรมา สั่งห้ามวางสายและให้ไปเปิดห้องอยู่คนเดียว", "isolate_official", "impersonation"),
])
def test_structural_scams_caught(text, rule, flag):
    from core.conditions import check
    from core.kernel_voice import assess
    assert rule in [h.rule for h in check(text)]
    a = assess(text)
    assert a["topics"][0] == "scam" and flag in a["scam"]


@pytest.mark.parametrize("text", [
    "ค่าไฟเดือนนี้แพงมาก จะประหยัดยังไงดี", "ซื้อบัตรของขวัญให้แม่วันเกิด", "หลานประสบอุบัติเหตุ ตอนนี้อยู่โรงพยาบาล ต้องไปเยี่ยม",
    "โอนค่าห้องให้เจ้าของหอแล้ว", "ลูกค้าต้องโอนมัดจำก่อนถึงจะทำของให้ ร้านเราควรตั้งกี่เปอร์เซ็นต์", "ธนาคารส่ง SMS แจ้งยอดโอนเข้า",
    "แฟนที่รู้จักกันในเฟซตอนนี้แต่งงานกันแล้ว 5 ปี", "ได้รับรางวัลพนักงานดีเด่น", "ร้านรีวิวอาหารอร่อยมาก", "วิดีโอคอลกับแม่ทุกคืน",
    "รีวิวโรงแรมให้หน่อย เติมเงินในแอปจองยังไง", "เจ้าหน้าที่ธนาคารบอกว่าเป็นความลับของลูกค้า ไม่เปิดเผยให้ใคร", "ตำรวจมาตรวจที่หมู่บ้าน",
])
def test_structural_scams_do_not_overfire(text):
    from core.conditions import check
    assert not [h for h in check(text) if h.topic == "scam"]
