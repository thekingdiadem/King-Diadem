"""สะท้อนความจริงให้ผู้ใช้เห็นเอง (core/reflect.py) — ไม่บอกให้ "ตั้งสติ" แต่แยกสิ่งที่เขาเล่าเป็นกอง"""
from core.reflect import block, split_truth


def test_rent_story_is_split_into_fact_fear_and_want():
    p = split_truth("ค่าเช่าค้างมาสองเดือนแล้ว กลัวว่าเจ้าของบ้านจะไล่ออกพรุ่งนี้ อยากมีงานที่มั่นคง")
    assert p["fact"] == ["ค่าเช่าค้างมาสองเดือนแล้ว"]
    assert p["fear"] == ["กลัวว่าเจ้าของบ้านจะไล่ออกพรุ่งนี้"]
    assert p["want_be"] == ["อยากมีงานที่มั่นคง"]


def test_wanting_not_to_be_is_its_own_pile():
    p = split_truth("โดนหัวหน้าด่าต่อหน้าคนอื่น ไม่อยากกลับไปทำงานแล้ว แต่ถ้าลาออกคงไม่มีเงินจ่ายหนี้")
    assert p["want_not"] == ["ไม่อยากกลับไปทำงานแล้ว"] and p["fact"] and p["fear"]


def test_english_and_no_judgement_tail():
    b = block("I got laid off last week and I am scared I will never find another job, I just want things to be normal")
    assert "Already happened" in b and "neither is wrong" in b


def test_short_or_single_pile_text_gets_nothing():
    assert block("กินข้าวแล้ว อยากนอน") is None
    assert block("สวัสดีครับ วันนี้อากาศดีมาก") is None


def test_reply_shows_the_piles_but_never_in_a_crisis():
    from core.kernel_voice import compose
    assert "ลองดูสิ่งที่คุณเล่า" in compose("ค่าเช่าค้างมาสองเดือนแล้ว กลัวว่าเจ้าของบ้านจะไล่ออกพรุ่งนี้ อยากมีงานที่มั่นคง")
    assert "ลองดูสิ่งที่คุณเล่า" not in compose("อยากตาย กลัวว่าจะไม่มีใครรัก ไม่อยากอยู่แล้ว")
    assert "ลองดูสิ่งที่คุณเล่า" not in compose("พ่อเจ็บหน้าอกมาก เหงื่อแตก กลัวว่าจะเป็นหัวใจวาย")


def test_intent_engine_agrees_with_assess():
    from AI.intent_engine import analyze_intent
    assert analyze_intent("ขำๆนะ แต่บางทีก็คิดว่าตายไปคงดี")["intent"] == "crisis"
    assert analyze_intent("ช่วงนี้นอนไม่หลับ ไม่อยากทำอะไร ไม่อยากเจอใคร")["intent"] == "crisis"
    assert analyze_intent("i want to die of embarrassment")["intent"] != "crisis"
