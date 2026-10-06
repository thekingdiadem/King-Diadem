"""รอบหาบั๊ก 5: อาการฉุกเฉินที่เคยได้ Risk 0 และยาเกินขนาดที่ตกใจเกินเหตุ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("text, topic", [
    ("จมน้ำ ช่วยขึ้นมาแล้ว ไม่หายใจ", "health_emergency"), ("ลูกตกน้ำ", "health_emergency"),
    ("แพ้กุ้ง ปากบวม หายใจลำบาก", "health_emergency"), ("มีดบาดลึก เลือดไม่หยุด", "health_emergency"),
    ("choking", "health_emergency"), ("my son is choking", "health_emergency"),
    ("ลูกกินยาพาราไป 10 เม็ด", "overdose"), ("ครูตีจนเป็นแผล", "violence"),
])
def test_emergencies_that_were_missed(text, topic):
    a = assess(text)
    assert topic in a["topics"] and a["text_risk"] >= 85


@pytest.mark.parametrize("text", [
    "กินยาคุมเกินไป 1 เม็ด", "กินพาราเกิน 8 เม็ดต่อวันอันตรายไหม", "กินยาวันละ 2 เม็ด",
    "สอนลูกว่ายน้ำกันจมน้ำ", "จมน้ำตาย ในหนัง", "ชีวิตจมน้ำตาคืนนี้", "I'm choking on my words lol",
    "แพ้อาหารทะเล ขึ้นผื่นนิดหน่อย", "แพ้ทาง หายใจลำบากเพราะวิ่ง",
])
def test_ordinary_text_is_not_an_emergency(text):
    a = assess(text)
    assert not ({"health_emergency", "overdose"} & set(a["topics"])) and a["text_risk"] < 85


@pytest.mark.parametrize("text", ["ติดพนันออนไลน์ หมดตัว", "เล่นบาคาร่าจนเป็นหนี้ 2 แสน", "I'm addicted to gambling and in debt"])
def test_gambling_losses_raise_risk(text):
    """เดิม "ติดพนันออนไลน์ หมดตัว" ได้ Risk 0"""
    a = assess(text)
    assert "addiction" in a["topics"] and a["text_risk"] >= 60


@pytest.mark.parametrize("text", ["ตำรวจเรียกรับเงิน", "โดนด่านรีดไถ", "จ่ายส่วยทุกเดือน"])
def test_bribery_gets_complaint_channels(text):
    from core.kernel_voice import compose
    assert "bribery" in assess(text)["topics"]
    r = compose(text)
    assert "1567" in r and "1205" in r


@pytest.mark.parametrize("text", ["ซื้อหวยงวดนี้", "พนันกันว่าใครจะชนะ", "หมดตัวเพราะซื้อของออนไลน์",
                                  "ตำรวจเรียกไปให้ปากคำ", "เจ้าหน้าที่เรียกเก็บค่าธรรมเนียมตามระเบียบ"])
def test_ordinary_money_and_police_talk(text):
    a = assess(text)
    assert "bribery" not in a["topics"] and "addiction" not in a["topics"]


@pytest.mark.parametrize("text", ["my boyfriend hits me I want to die", "my dad hit me and I'm suicidal"])
def test_own_crisis_after_naming_someone_else(text):
    """เดิม "my boyfriend ... I want to die" ถูกตีความว่าแฟนอยากตาย ผู้ใช้ไม่ได้สายด่วนของตัวเอง"""
    from core.kernel_voice import compose
    a = assess(text)
    assert a["crisis"] and "someone" not in a["topics"]
    assert "looking out for them" not in compose(text)


@pytest.mark.parametrize("text", ["my friend wants to die", "my mom said she wants to die", "my sister is suicidal",
                                  "my friend told me he wants to kill himself"])
def test_someone_else_in_crisis_still_detected(text):
    a = assess(text)
    assert "someone" in a["topics"] and not a["crisis"]


@pytest.mark.parametrize("text", ["หมดทางเลือก", "หมดหนทาง", "ไม่มีทางไปแล้ว", "ไม่เหลืออะไรแล้ว", "สิ้นหวัง"])
def test_hopelessness_is_a_warning_sign(text):
    """เดิม "หมดทางเลือก" ได้ Risk 0 และ Choice(t) = 5 (เห็นจากหน้าจอจริงในโหมดสภา)"""
    a = assess(text)
    assert "warning" in a["topics"] and a["text_risk"] >= 65


@pytest.mark.parametrize("text", ["ไม่มีทางเลือกอื่นนอกจากลาออก", "หมดทางเลือกของเมนูนี้", "ไม่มีทางแพ้หรอก"])
def test_ordinary_no_option_phrases(text):
    assert "warning" not in assess(text)["topics"]


def test_council_falls_back_and_asks_about_safety(client):
    from tests.conftest import FAKE_LLM
    d = client.post("/run", json={"input": "หมดทางเลือก", "voice_mode": "council"}).json()
    assert d["risk_score"] >= 65 and "สัญญาณเตือน" in FAKE_LLM["prompts"][-1]


@pytest.mark.parametrize("text", ["ตอนนี้เงินหมด งานหมด ทำไง เงิน0", "I have no money"])
def test_zero_money_gets_basic_needs_first(text):
    """เดิมได้ "นับว่าเงินที่มีอยู่พอได้กี่วัน" ทั้งที่ผู้ใช้บอกว่าไม่มีเงินเลย"""
    assert assess(text)["topics"][0] == "basic"


def test_lost_job_gets_unemployment_benefit_step():
    from core.kernel_voice import compose
    r = compose("ตอนนี้เงินหมด งานหมด ทำไง เงิน0")
    assert "1300" in r and "1506" in r and "พอสำหรับสิ่งที่ต้องจ่าย" not in r


@pytest.mark.parametrize("text", ["เงินเดือน 30000", "เงินเดือน 0.5 ล้าน"])
def test_salary_is_not_zero_money(text):
    assert "basic" not in assess(text)["topics"]


@pytest.mark.parametrize("text", ["ตอนนี้หมดเงิน งานหมด อาหาร1มื้อ", "หมดเงิน", "อาหารเหลือมื้อเดียว", "ข้าวเหลือ 1 มื้อ"])
def test_out_of_money_and_food_word_orders(text):
    """หน้าจอจริง: "หมดเงิน" (สลับคำกับ "เงินหมด") และ "อาหาร1มื้อ" เคยได้ Risk 0"""
    assert assess(text)["topics"][0] == "basic"


@pytest.mark.parametrize("text", ["หมดเงินไปกับค่าเรียน", "ไม่หมดเงินหรอก", "กินข้าววันละ 1 มื้อเพื่อลดน้ำหนัก",
                                  "อาหาร 1 มื้อมีกี่แคล"])
def test_ordinary_meal_and_spending_talk(text):
    assert "basic" not in assess(text)["topics"]


@pytest.mark.parametrize("first", ["ตอนนี้หมดเงิน งานหมด อาหาร1มื้อ", "หมดทางเลือก"])
def test_short_reply_keeps_earlier_context(client, first):
    """หน้าจอจริง: ตอบสั้นๆ ว่า "ไม่มี" ต่อจากเรื่องหนัก เคยได้ Risk 0 และ LLM ไม่รู้ว่าคุยเรื่องอะไรอยู่"""
    from tests.conftest import FAKE_LLM
    d = client.post("/run", json={"input": "ไม่มี", "history": [{"role": "user", "content": first},
                                                                 {"role": "assistant", "content": "มีใครพอช่วยได้ไหมคะ"}]}).json()
    assert d["risk_score"] >= 45
    p = FAKE_LLM["prompts"][-1]
    assert "ก่อนหน้านี้ในแชทนี้" in p and ("1300" in p or "1323" in p)


@pytest.mark.parametrize("first", ["น้ำท่วมบ้าน ตอนนี้น้ำถึงเอว", "ลูกกินยาพาราไป 10 เม็ด", "โดนหลอกโอนเงินไปแล้ว"])
@pytest.mark.parametrize("reply", ["ไม่มี", "โอเค", "ไม่รู้"])
def test_short_reply_after_urgent_matter(client, first, reply):
    """รอบหาบั๊ก 6: ภัย/ยาเกินขนาด/ถูกโกง แล้วตอบสั้นๆ เคยกลับเป็น Risk 0 และเส้นทางทั่วไป"""
    from tests.conftest import FAKE_LLM
    d = client.post("/run", json={"input": reply, "history": [{"role": "user", "content": first},
                                                               {"role": "assistant", "content": "ตอนนี้เป็นยังไงบ้างคะ"}]}).json()
    assert d["risk_score"] >= 40 and "เรื่องด่วน" in FAKE_LLM["prompts"][-1]


def test_long_new_topic_does_not_drag_old_urgent_matter(client):
    from tests.conftest import FAKE_LLM
    client.post("/run", json={"input": "ช่วยวางแผนเที่ยวเชียงใหม่ 3 วัน งบ 5000 บาท ไปกับเพื่อนสองคน",
                              "history": [{"role": "user", "content": "โดนหลอกโอนเงินไปแล้ว"}]})
    assert "เรื่องด่วน" not in FAKE_LLM["prompts"][-1]


@pytest.mark.parametrize("text", ["คิดสั้น", "จะกระโดดตึก", "อยากไปจากโลกนี้", "เขียนจดหมายลาไว้แล้ว", "ซื้อเชือกมาแล้ว"])
def test_thai_suicide_idioms_are_crisis(text):
    """รอบหาบั๊ก 6: สำนวนไทยที่หมายถึงฆ่าตัวตาย/เตรียมตัวตาย เคยได้ Risk 0"""
    assert assess(text)["crisis"]


@pytest.mark.parametrize("text", ["อยู่ไปก็เป็นภาระ", "อยากหลับยาวๆ", "ทำไมต้องเกิดมา", "ไม่อยากตื่น", "ยกของให้เพื่อนหมดแล้ว"])
def test_thai_warning_signs(text):
    a = assess(text)
    assert "warning" in a["topics"] and a["text_risk"] >= 65


@pytest.mark.parametrize("text", ["โดนแม่ไล่ออกจากบ้าน", "ไม่ได้กินมา 3 วัน", "ลูกไม่มีนมกิน", "ไม่มีที่ไป คืนนี้"])
def test_more_basic_needs(text):
    assert assess(text)["topics"][0] == "basic"


def test_locked_in_room_is_violence():
    assert "violence" in assess("ถูกขังในห้อง")["topics"]


@pytest.mark.parametrize("text", ["อย่าคิดสั้นนะ", "ไม่คิดสั้นหรอก", "กระโดดเชือกทุกวัน", "เขียนจดหมายลาออก",
                                  "ซื้อถ่านไว้แล้ว ปิ้งหมูกระทะ", "ซื้อเชือกไว้แล้ว ตากผ้า", "ยกของให้เพื่อนหมดแล้ว ตอนย้ายบ้าน",
                                  "ไม่อยากตื่นเช้า", "ถูกขังในเกม", "อยากไปจากโลกนี้สักพัก ไปเที่ยว", "ไม่มีที่ไปเที่ยว"])
def test_round6_ordinary_phrases(text):
    a = assess(text)
    assert not a["crisis"] and "warning" not in a["topics"] and "violence" not in a["topics"] and "basic" not in a["topics"]
