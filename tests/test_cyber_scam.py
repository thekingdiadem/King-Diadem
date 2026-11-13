"""กลโกงไซเบอร์ที่ผู้ใช้พิมพ์มาเล่า (core/cyber_scam.py)

ที่มา: โพสต์ของตำรวจไซเบอร์ที่เจ้าของโปรเจกต์แคปมา (ต.ค.–พ.ย. 2569) — กรองเหลือเฉพาะสถานการณ์ที่คนทั่วไปเจอ
และหลักที่จริงเสมอ (เจ้าหน้าที่จริงไม่มารับเงินถึงบ้าน · หน้าไม่ใช่หุ่นยนต์ไม่ได้พิสูจน์ว่าเว็บจริง · ถามกลับทางเดิมไม่ใช่การยืนยัน)
เดิม "SMS ใบสั่งจราจรให้กดลิงก์" ได้คำตอบเรื่องหนี้ "ตำรวจให้ถอนเงินไปซื้อทอง" ได้คำแนะนำการลงทุน และส่วนใหญ่ได้ความเสี่ยงศูนย์

FIRST = ชุดแรกที่ใช้ออกแบบรูปประโยค · MORE = ชุดที่เขียนทีหลังด้วยสำนวนและการสะกดอื่น ("ลิ้งค์" "ลิงค์")
LIGHT = เรื่องปกติที่คำคล้ายกัน ต้องไม่ถูกมองว่าโดนหลอก ("ถอนเงินไปซื้อทองเก็บไว้เอง" "ครูส่งลิงก์ดูเกรด")
"""
import re
import uuid

import pytest

from core.kernel_voice import assess, compose
from tests.conftest import FAKE_LLM

FIRST = ['ได้ SMS ว่ามีใบสั่งจราจรค้างจ่าย ให้กดลิงก์ชำระค่าปรับด่วน', 'มีข้อความให้กดลิงก์ไปโหลดแอปกรมที่ดิน เป็นไฟล์ apk', 'ลงแอปจากลิงก์ไปแล้ว มันขอสิทธิ์การช่วยเหลือการเข้าถึง กดอนุญาตไปแล้ว', 'มีคนโทรมาอ้างเป็นตำรวจ บอกให้ถอนเงินไปซื้อทอง แล้วจะส่งเจ้าหน้าที่มารับที่บ้าน', 'เจ้าหน้าที่บอกให้ไปซื้อบัตรของขวัญแล้วส่งรหัสให้เพื่อเคลียร์คดี', 'เขาให้เอาเงินสดไปฝากตู้บิตคอยน์', 'เพื่อนส่งเมลมายืมเงิน ฉันถามกลับไปทางเมล เขาตอบว่าจริง', 'มีแอปจ่ายเงินให้ครั้งละ 3 บาท แค่ให้มันใช้ซิมเราส่ง SMS', 'เว็บให้กดยืนยันว่าไม่ใช่หุ่นยนต์ แล้วให้กรอก OTP', 'มีข่าวว่าธนาคารที่ใช้โดนแฮ็ก ควรรีบไปถอนเงินออกหมดไหม', 'ญาติชวนลงทุนวงนี้ จ่ายปันผลจริงมา 3 ปีแล้ว ให้ชวนคนอื่นต่อได้ค่าคอม', 'โหลดแอปดูหนังฟรี แล้วโฆษณาให้ติดตั้งไฟล์เพิ่ม', 'got a text about an unpaid toll, link to pay the fine', 'a guy claiming to be from the FBI told me to withdraw cash and buy gold, a courier will pick it up', 'they want me to pay with gift cards to avoid arrest', 'the app asked for accessibility permission and i allowed it', "my friend emailed asking for money, i replied to check and he said yes it's me"]
MORE = ['มีเอสเอ็มเอสบอกว่าพัสดุตกค้าง ให้คลิกลิงก์ยืนยันที่อยู่', 'ไลน์มาบอกว่าบัญชีถูกระงับ ให้กดลิ้งค์', 'ข้อความแจ้งคืนภาษี กดลิงค์รับเงิน', 'คนโทรมาบอกเป็น DSI สั่งให้ไปถอนเงินสดแล้วจะมีคนมารับที่หน้าบ้าน', 'มือถือค้างไปเลยหลังติดตั้งแอปจากลิงก์', 'แอปกู้เงินให้โหลดผ่านลิงก์ในเฟซ', 'แม่ทักไลน์มาขอให้โอนเงินด่วน', 'ตำรวจให้ไปซื้อบัตรเติมเงินแล้วถ่ายรูปรหัสส่งให้', 'กดตกลงให้แอปควบคุมเครื่องไปแล้ว', 'มีแอปให้เปิดเครื่องทิ้งไว้แล้วได้เงินวันละ 50', 'text says my package is held, click the link to reschedule delivery', 'someone from customs said to pay the fee at a bitcoin atm', 'my phone froze after i installed the app from the link', 'i downloaded an apk the bank guy sent', 'the page had a captcha then asked for my otp']
LIGHT = ['ถอนเงินไปซื้อทองเก็บไว้ลงทุนเองดีไหม', 'ไปซื้อทองที่ร้านมา', 'ได้ SMS จากธนาคารว่ามีเงินเข้า', 'ไรเดอร์โทรมาบอกพัสดุมาส่งแล้ว', 'เพื่อนยืมเงินไปแล้วไม่คืน', 'ช่วยสอนวิธีป้องกันแอป apk หน่อย', 'แอปขอสิทธิ์เข้าถึงรูปภาพ ให้ได้ไหม', 'ซื้อบัตรของขวัญให้แฟนวันเกิดดี', 'เมลจากหัวหน้าส่งงานมาให้แก้', 'ครูส่งลิงก์มาในไลน์กลุ่มให้กดดูเกรด', 'how do i build an apk for my app', 'the courier will pick up my package from home tomorrow', 'i installed the app from the play store', 'bought a gift card for my mom', 'my friend texted me to say happy birthday', 'ลงทุนกองทุนรวมได้ปันผลมา 3 ปี', 'ข่าวธนาคารออกบัตรใหม่']


@pytest.mark.parametrize("text", FIRST + MORE)
def test_cyber_scam_is_recognised(text):
    a = assess(text)
    assert a["cyber"] and a["text_risk"] >= 50 and "scam" in a["topics"], a


@pytest.mark.parametrize("text", LIGHT)
def test_everyday_money_and_links_stay_light(text):
    a = assess(text)
    assert not a["cyber"] and a["text_risk"] < 35, a


@pytest.mark.parametrize("text", [x for x in FIRST + MORE])
def test_reply_is_about_the_scam_with_the_cyber_police_number(text):
    r = compose(text)
    assert "1441" in r, r
    assert not r.startswith(("หนี้เป็นตัวเลข", "เงินที่มีอยู่", "ขอเรียงเรื่องนี้", "Let's lay this out", "I'm sorry this happened")), r[:60]


def test_police_asking_for_gold_says_real_officers_never_collect_at_home():
    r = compose("มีคนโทรมาอ้างเป็นตำรวจ บอกให้ถอนเงินไปซื้อทอง แล้วจะส่งเจ้าหน้าที่มารับที่บ้าน")
    assert "ไม่ส่งคนมารับเงินหรือทองที่บ้าน" in r


def test_accessibility_permission_is_the_most_urgent():
    a = assess("ลงแอปจากลิงก์ไปแล้ว มันขอสิทธิ์การช่วยเหลือการเข้าถึง กดอนุญาตไปแล้ว")
    assert a["cyber"] == "accessibility" and a["text_risk"] >= 85
    assert "โหมดเครื่องบิน" in compose("ลงแอปจากลิงก์ไปแล้ว มันขอสิทธิ์การช่วยเหลือการเข้าถึง กดอนุญาตไปแล้ว")


def test_vega_voice_keeps_its_own_ending():
    r = compose("ได้ SMS ว่ามีใบสั่งจราจรค้างจ่าย ให้กดลิงก์ชำระค่าปรับด่วน", voice_mode="vega")
    assert "ครับ" in r and "ค่ะ" not in r and r.rstrip().splitlines()[-2].startswith("— VEGA")


def test_ai_reply_without_numbers_gets_the_scam_line(client):
    FAKE_LLM.update(text="ลองแบ่งเป็นสามขั้น 1) จด 2) แยก 3) เลือก\n— LYLA ◈")
    ip = "10.66.%d.%d" % tuple(uuid.uuid4().bytes[:2])
    r = client.post("/run", json={"input": "เขาให้เอาเงินสดไปฝากตู้บิตคอยน์", "history": []}, headers={"cf-connecting-ip": ip}).json()
    assert "1441" in r["ai_response"] and "1323" not in r["ai_response"], r["ai_response"]
