"""หลักจากแกนกำกับดูแลเชิงจริยธรรมของเจ้าของโปรเจกต์ ที่แปลงเป็นกฎตรวจได้
  · ความเงียบคือความสำเร็จเมื่อมีทางเลือกแล้ว → ขอบคุณ/รับทราบ ได้คำตอบสั้น ไม่ใช่แผน 3 ขั้นชุดใหม่
  · ชั้นชะลอ → เรื่องหนัก หน้าจอไม่เร่งไม่ขาย"""
import pytest

from core.thai_signals import small_talk
from tests._front import front_page

PAGE = front_page()


@pytest.mark.parametrize("text", ["ขอบคุณค่ะ", "thanks, that helps", "โอเค เข้าใจแล้ว", "ok got it thank you", "Thank you so much!"])
def test_acknowledgement_is_recognised(text):
    assert small_talk(text) == "thanks"


@pytest.mark.parametrize("text", ["ขอบคุณ แต่ยังนอนไม่หลับ", "thanks but I still can't pay rent", "got it, what about my debt?",
                                  "เข้าใจแล้วว่าต้องเลิก", "ok"])
def test_acknowledgement_with_a_remaining_problem_is_not_silenced(text):
    assert small_talk(text) != "thanks"


@pytest.mark.parametrize("text", ["thanks, that helps", "โอเค เข้าใจแล้ว"])
def test_reply_to_thanks_is_short_and_has_no_plan(text):
    from core.kernel_voice import compose
    r = compose(text)
    assert "1)" not in r and len(r) < 220, r


def test_screen_goes_quiet_for_heavy_topics_and_recovers():
    assert "heavy = d.route === 'crisis' || num(d.risk_score, 0) >= 70" in PAGE
    assert "calm = d.route !== 'crisis' && num(d.risk_score, 0) < 50" in PAGE
    assert "body.kd-gentle #upgrade-pill,body.kd-gentle #starters" in PAGE and "display:none!important" in PAGE


def test_living_crest_respects_reduced_motion():
    assert "animation:kd-crest-turn 90s linear infinite" in PAGE
    assert "html.kd-calm .crest i" in PAGE and "@media (prefers-reduced-motion:reduce){ .crest i{animation:none} }" in PAGE
