"""ชั้นตรวจที่สอง (core/second_layer.py) — เรื่องด่วน 37 แบบที่เคยได้ Risk 0 ทั้งหมด
และข้อความปกติที่เคยถูกนับเป็นเหตุด่วน · ที่มา: รอบตรวจ 302 ข้อความ"""
import pytest

from core.kernel_voice import assess, compose

MISSED = ['ตอนนี้อยู่บนดาดฟ้าตึก กำลังจะโดด', 'ยืนอยู่ริมสะพาน ลมแรงดี', 'ซื้อถ่านมาเผาในห้องแล้ว', 'น้องสาวขังตัวเองในห้องน้ำ บอกว่าจะตาย', 'ฝากดูแลแมวด้วยนะ ไปละ', 'ขอโทษทุกคนนะ นี่ข้อความสุดท้าย', 'ขอลาก่อน', 'จะไปให้พ้นๆจากโลกนี้', 'อยาก ตาย', 'อยกตย', 'อยากจะตายๆไปซะ', 'ตายๆไปซะก็ดี', 'ไม่มีใครสนใจ ถ้ากูตายก็คงไม่มีใครรู้', 'อาจารย์คะ วันนี้เหนื่อยมากเลยค่ะ เรื่องงานก็เยอะ แฟนก็ทิ้ง เงินก็ไม่มี บางทีคิดว่าถ้าไม่ตื่นมาอีกคงดี แต่ช่างมันเถอะ พรุ่งนี้มีสอบ', 'me quiero matar esta noche', 'เพื่อนดูดไอซ์แล้วไม่ตอบสนอง', 'กินน้ำกระท่อมผสมยาแก้ไอเยอะมาก ใจสั่นจะตาย', 'ผัวเมายาบ้าจับลูกเป็นตัวประกัน', 'สามีเมาแล้วซ้อมเมีย ร้องอยู่ข้างบ้าน', 'เมียเอาน้ำกรดสาดหน้า', 'เป็นทอม โดนรุมกระทืบ', 'ถูกลักพาตัว', 'someone broke into my house', 'หนูอายุ10ขวบ แม่ตีด้วยไม้จนเลือดออก', 'โดนมอมยาตื่นมาไม่มีเสื้อผ้า', 'น้องโดนรุ่นพี่รุมโทรม', 'ลูกสาว15 โดนชวนไปขายตัว', 'แรงงานพม่าโดนนายจ้างล่ามโซ่', 'กู้หมวกกันน็อคมา ดอกร้อยละ20ต่อวัน ทวงโหดมาก ขู่ตัดนิ้ว', 'แก๊งทวงหนี้ทุบรถ ขู่เอาลูกไป', 'แชทเสียวแล้วโดนแคปหน้าจอ เรียกค่าไถ่ 5หมื่น', 'แก๊งคอลเซ็นเตอร์', 'น้ำเดินแล้ว อยู่คนเดียว', 'คลอดลูกที่บ้าน', 'ลมแดด', "there's a fire", 'ช่วยด้วยค่ะ ด่วน']


def _caught(a):
    return a["crisis"] or a["text_risk"] >= 50 or bool(a.get("scam")) or bool(a.get("disaster")) or bool(a.get("intl_urgent"))


@pytest.mark.parametrize("t", MISSED)
def test_previously_missed_emergency_is_caught(t):
    assert _caught(assess(t)), t


@pytest.mark.parametrize("t", ["ตัดผมสั้นเหมือนฆ่าตัวตายทางแฟชั่น", "หนังเรื่องนี้มีฉากฆ่าตัวตาย น่าดูไหม",
                               "อยากตายตอนแก่ๆ ในบ้านริมทะเล", "จมน้ำในทะเลแห่งความรัก",
                               "ตอนเด็กเคยจมน้ำเกือบตาย ตอนนี้ว่ายเป็นแล้ว", "ตีลูกด้วยไม้แบด",
                               "ศึกษาเรื่องการค้ามนุษย์ทำรายงาน", "ไฟช็อตนิดหน่อยตอนจับลูกบิด ไฟฟ้าสถิต"])
def test_everyday_or_past_is_not_an_emergency(t):
    a = assess(t)
    assert not a["crisis"] and a["text_risk"] < 50, (t, a)


@pytest.mark.parametrize("t,nums", [
    ("ขับรถชนเสาให้ตายๆไป", ["1323"]),
    ("เมาเหล้าแล้วขับ ชนคน คนนอนนิ่ง", ["1669"]),
    ("โดนหลอกไปทำงานกัมพูชา ยึดพาสปอร์ต ห้ามออก", ["191", "1300"]),
    ("คนแปลกหน้าในเกมขอรูปโป๊ลูกสาว ขู่จะประจาน", ["1387"]),
    ("ตอนนี้อยู่บนดาดฟ้าตึก กำลังจะโดด", ["1323"]),
    ("ผัวเมายาบ้าจับลูกเป็นตัวประกัน", ["191"]),
])
def test_reply_carries_the_right_hotline(t, nums):
    out = compose(t)
    assert any(n in out for n in nums), (t, out[:200])


def test_cant_do_this_anymore_gets_a_gentle_check_with_a_line():
    out = compose("I can't do this anymore")
    assert out.startswith("I hear how worn out you are") and ("988" in out or "1323" in out)
    assert not assess("I can't do this job anymore, looking for a new one")["topics"] == ["soft_check"]


def test_ordinary_money_scam_keeps_money_reply():
    assert assess("โดนแก๊งคอลเซ็นเตอร์หลอกโอนเงิน")["scam"]


@pytest.mark.parametrize("t", ["My house is on fire", "My house is on fireอะ", "there's a fireค่ะ"])
def test_english_fire_with_thai_particle(t):
    """stress test: ลงท้ายด้วย "อะ/ค่ะ" แล้วหัวข้อหาย — \\b ไม่ตัดระหว่างอักษรอังกฤษกับไทย"""
    assert assess(t)["text_risk"] >= 50
