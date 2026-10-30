"""คำตอบแบบไม่ใช้ AI ขึ้นบรรทัดสถานะเป็นภาษาคน ไม่ใช่สูตร

เดิมทุกคำตอบมี "W — · Risk 55 · Choice(t) = 3" ซึ่งคนทั่วไปอ่านไม่ออก (แผงขวาเปลี่ยนเป็นภาษาคนไปแล้วใน PR #121)
ตอนนี้เป็น "ความเสี่ยงตอนนี้: ยังรับมือได้ (55/100)" ใช้เกณฑ์เดียวกับแผงขวา และตัวเลขยังตรงกับ risk_score
"""
import re

import pytest

from core.kernel_voice import compose, risk_phrase, shown_risk, simulate, status_line

FORMULA = re.compile(r"\bW (?:—|\d)|Choice\(t\) =|· Risk \d")


@pytest.mark.parametrize("text", [
    "หนี้บัตรเครดิต 50000 บาท ผ่อนไม่ไหวแล้ว", "เครียดเรื่องงาน", "โดนวิ่งราว มือถือหาย",
    "I can't decide whether to change jobs", "My husband hits me", "救命", "助けて", "살려주세요",
    "mi madre no respira", "Tôi muốn chết", "Ich weiß nicht weiter",
])
def test_offline_reply_has_no_formula(text, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    r = compose(text)
    assert not FORMULA.search(r), r
    assert "\n\n\n" not in r


def test_simulate_and_council_have_no_formula():
    assert not FORMULA.search(simulate("I lost my job", ["quit and travel", "find new job"]))
    assert not FORMULA.search(simulate("ตกงาน", ["ลาออกไปเที่ยว", "หางานใหม่"]))
    assert not FORMULA.search(compose("ควรลาออกหรือทำต่อ", voice_mode="council"))


def test_debt_reply_reads_plainly():
    r = compose("หนี้บัตรเครดิต 50000 บาท ผ่อนไม่ไหวแล้ว")
    assert "ความเสี่ยงตอนนี้: ยังรับมือได้ (55/100)" in r and shown_risk(r) == 55


@pytest.mark.parametrize("risk,word", [(0, "ยังรับมือได้"), (60, "ยังรับมือได้"), (61, "ควรระวัง"),
                                       (80, "ควรระวัง"), (81, "ต้องดูแลด่วน"), (100, "ต้องดูแลด่วน")])
def test_same_thresholds_as_side_panel(risk, word):
    """static/index.html riskWord: เกิน 80 ต้องดูแลด่วน · เกิน 60 ควรระวัง"""
    assert risk_phrase({"risk": risk}) == f"{word} ({risk}/100)"


def test_shown_risk_uses_shown_value_not_default():
    assert risk_phrase({"risk": 57, "risk_shown": 0}) == "ยังรับมือได้ (0/100)"


@pytest.mark.parametrize("lang", ["th", "en", "zh", "ja", "ko", "es"])
def test_every_reply_language_has_a_status_line(lang):
    line = status_line({"risk": 90}, lang)
    assert line and "(90/100)" in line


def test_language_without_translation_gets_no_line():
    assert status_line({"risk": 90}, "vi") == ""
    assert shown_risk("ไม่มีตัวเลข") is None


def test_restate_risk_changes_word_with_number():
    """คำตอบต่อเนื่องหลังเรื่องฉุกเฉินลดความเสี่ยงตามเวลา (85 → 64) — คำบอกระดับต้องเปลี่ยนตามด้วย"""
    from core.kernel_voice import restate_risk
    assert restate_risk("Risk right now: needs care now (85/100)", 64) == "Risk right now: take care (64/100)"
    assert restate_risk("ความเสี่ยงตอนนี้: ต้องดูแลด่วน (85/100)", 64.4) == "ความเสี่ยงตอนนี้: ควรระวัง (64/100)"
