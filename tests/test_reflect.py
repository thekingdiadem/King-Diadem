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
    assert "Already happened" in b and "don't have to fight it" in b


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


def test_closing_follows_the_middle_way():
    """ธัมมจักกัปปวัตตนสูตร: อยากมีอยากเป็นกับไม่อยากมีไม่อยากเป็นเป็นแรงดึงเดียวกัน · ไม่ตามและไม่ทรมานตัวเอง"""
    both = block("อยากมีงานที่มั่นคง แต่ไม่อยากกลับไปทำงานที่เดิมแล้ว กลัวว่าจะไม่มีเงิน")
    assert "แรงที่ดึงใจเราอยู่เหมือนกัน" in both and "ไม่ต้องโทษตัวเอง" in both
    fact_fear = block("แฟนบอกเลิกเมื่อวาน กลัวจะอยู่คนเดียวไปตลอด")
    assert "ยังเป็นแค่ความคิด" in fact_fear
    for b in (both, fact_fear):
        assert "ตัณหา" not in b and "ตั้งสติ" not in b      # ไม่สั่งสอน ไม่สั่งให้ตั้งสติ


def test_gemini_prompt_carries_the_same_principle_but_not_in_crisis():
    """คำตอบที่ใช้ AI ต้องพูดจากหลักเดียวกับคำตอบที่ไม่ใช้ AI — แต่ไม่ใส่ในโหมดวิกฤต"""
    from core.llm_gemini import LYLA_SYSTEM, CRISIS_SYSTEM
    assert "แรงดึงใจชนิดเดียวกัน" in LYLA_SYSTEM and "ห้ามใช้หลักนี้กับคนที่มีความคิดทำร้ายตัวเอง" in LYLA_SYSTEM
    assert "แรงดึงใจชนิดเดียวกัน" not in CRISIS_SYSTEM
