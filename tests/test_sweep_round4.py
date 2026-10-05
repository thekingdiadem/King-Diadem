"""รอบหาบั๊ก 4: ประโยคที่คนพิมพ์จริง — สัญญาณกินยาเพื่อไม่ตื่น · สำนวนที่ถูกนับเป็นภัยพิบัติ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("text", ["อยากกินยาให้หลับไม่ตื่น", "อยากกินยานอนทั้งแผง", "อยากหลับไม่ตื่นอีกเลย"])
def test_pills_to_not_wake_up_is_a_crisis(text):
    """เดิมได้ Risk 0 — มีคำว่ายาคั่น เลยไม่ติดรูป "อยากหลับไม่ตื่น" """
    a = assess(text)
    assert a["crisis"] and a["text_risk"] >= 90


def test_whole_strip_taken_is_overdose():
    a = assess("กินยานอนทั้งแผงไปแล้ว")
    assert "overdose" in a["topics"] and a["text_risk"] >= 80


@pytest.mark.parametrize("text", ["ยานอนหลับช่วยให้หลับไม่ตื่นกลางดึกไหม", "กินยาแก้ปวดหมดแผงในอาทิตย์เดียว",
                                  "อยากกินยาให้หลับไปเลย"])
def test_sleep_and_pill_questions_are_not_crises(text):
    a = assess(text)
    assert not a["crisis"] and "overdose" not in a["topics"]


@pytest.mark.parametrize("text", ["น้ำท่วมปอดเลย ดีใจมาก", "แผ่นดินไหวในใจ", "ไฟป่าในใจ", "ใจเหมือนแผ่นดินไหว",
                                  "ชีวิตเหมือนโดนน้ำท่วม", "น้ำท่วมหัวเอาตัวไม่รอด"])
def test_idioms_are_not_disasters(text):
    a = assess(text)
    assert a["disaster"] is None and a["text_risk"] == 0


@pytest.mark.parametrize("text, kind", [("น้ำท่วมบ้าน ตอนนี้น้ำถึงเอวแล้ว", "flood"), ("แผ่นดินไหว ตึกสั่นมาก", "quake"),
                                        ("บ้านเหมือนจะพังเพราะแผ่นดินไหว", "quake")])
def test_real_disasters_still_detected(text, kind):
    assert assess(text)["disaster"]["kind"] == kind


@pytest.mark.parametrize("text", ["อยากลาโลก", "คิดจะลาโลกแล้ว"])
def test_la_lok_slang_is_a_crisis(text):
    """"ลาโลก" = สแลงของการฆ่าตัวตาย — เดิมได้ Risk 0"""
    assert assess(text)["crisis"]


def test_friend_la_lok_is_someone_else():
    a = assess("เพื่อนโพสต์ว่าจะลาโลก")
    assert "someone" in a["topics"] and not a["crisis"]


@pytest.mark.parametrize("text", ["จะลาโลกโซเชียลสักพัก", "ไม่อยากลาโลกหรอก แค่เหนื่อย"])
def test_la_lok_social_media_is_not_a_crisis(text):
    assert not assess(text)["crisis"] and assess(text)["text_risk"] == 0


def test_child_swallowed_detergent_is_poisoning():
    assert "overdose" in assess("ลูกกินผงซักฟอกเข้าไป")["topics"]
    assert assess("ผงซักฟอกยี่ห้อไหนดี")["text_risk"] == 0


@pytest.mark.parametrize("text", ["โดนแก๊งคอลเซ็นเตอร์หลอกโอนเงิน", "I got scammed", "I was scammed out of $2000"])
def test_scam_victims_are_recognised(text):
    """แก๊งที่ชื่อยาวกว่า 10 ตัวอักษร และภาษาอังกฤษ เคยไม่ถูกนับว่าโดนหลอก"""
    assert "scam" in assess(text)["topics"]


def test_scam_question_is_not_a_victim():
    assert "scam" not in assess("how do scammers work")["topics"]


def test_english_scam_reply_has_bank_freeze_steps():
    from core.kernel_voice import compose
    r = compose("I got scammed")
    assert "freeze" in r and "1441" in r and "ค่ะ" not in r


@pytest.mark.parametrize("text", ["มีคนพยายามงัดประตูบ้าน", "มีคนเดินตามตลอดทาง กลัวมาก",
                                  "someone is breaking into my house", "I'm being followed home",
                                  "there's an intruder in my house"])
def test_intruder_and_being_followed_are_danger(text):
    """เดิมได้ Risk 0"""
    a = assess(text)
    assert a["disaster"]["kind"] == "intruder" and a["text_risk"] >= 60


@pytest.mark.parametrize("text", ["มีคนตามมาสมทบทีหลัง", "ถ้ามีคนงัดบ้านควรทำยังไง", "the intruder movie was great",
                                  "ลืมกุญแจ ปีนหน้าต่างเข้าบ้านตัวเอง", "followers on IG"])
def test_ordinary_text_is_not_intruder(text):
    assert assess(text)["disaster"] is None


def test_intruder_button_is_police():
    from core.engine_bridge import nearby
    assert [l["label"] for l in nearby("", {"kind": "intruder", "active": True})] == ["สถานีตำรวจ"]


@pytest.mark.parametrize("text, must", [("there's a fire in my kitchen", "Get out now"),
                                        ("someone is breaking into my house", "Don't confront"),
                                        ("earthquake right now building shaking", "drop, cover")])
def test_english_hazards_get_english_steps(text, must):
    """เดิมภัยทุกชนิดที่พิมพ์ภาษาอังกฤษได้ "Let's lay this out step by step." """
    from core.kernel_voice import compose
    r = compose(text)
    assert must in r and "Let's lay this out" not in r


def test_english_plan_question_is_not_active():
    assert assess("what should I do if there's a fire in my kitchen")["disaster"] is None


def test_dementia_wandering_is_missing_person():
    assert "missing" in assess("แม่เป็นอัลไซเมอร์ เดินออกจากบ้านหาย")["topics"]


def test_prize_sms_with_link_is_scam():
    assert "scam" in assess("ได้รับ SMS ว่าได้รางวัล กดลิงก์")["topics"]
    assert "scam" not in assess("ลูกได้รางวัลที่โรงเรียน")["topics"]


@pytest.mark.parametrize("text, annual", [("เป็นหนี้นอกระบบ ดอก 20% ต่อเดือน", "240%"),
                                          ("กู้นอกระบบ ดอกร้อยละ 10 ต่อวัน", "3,650%")])
def test_informal_loan_without_principal_still_warns(text, annual):
    """ไม่ได้บอกยอดเงินต้น — เดิมเงียบ ไม่เตือนว่าดอกผิดกฎหมาย"""
    from core.engine_bridge import analyze
    lines = " ".join(analyze(text)["lines"])
    assert annual in lines and "15% ต่อปี" in lines and "1567" in lines


def test_daily_rate_is_annualised():
    """"2% ต่อวัน" เคยถูกนับเป็น 2% ต่อปี"""
    from core.engine_bridge import parse_debts
    assert parse_debts("กู้รายวัน 5000 ดอก 2% ต่อวัน")[0]["annual_rate"] == 730


def test_no_credit_check_loan_gets_law_line():
    from core.engine_bridge import analyze
    assert "1567" in " ".join(analyze("กู้เงินด่วน ไม่เช็คบูโร")["lines"])
