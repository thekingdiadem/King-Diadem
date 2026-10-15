"""บั๊กเล็กจากรอบไล่หาบั๊ก: การจำลองทางเลือก · Choice(t) ภาษาอังกฤษ · หน้าเว็บ · คำถามที่ขาด"""
import re
from pathlib import Path

import pytest

from core.engine_bridge import analyze
from core.kernel_voice import compose, simulate

HTML = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def test_simulate_does_not_call_irreversible_path_reversible():
    """เดิมทุกทางย้อนกลับยาก แต่ยังพูดว่า "แนะนำเริ่มจาก A — ทางที่ย้อนกลับได้" """
    r = simulate("อยากย้ายงาน", ["ลาออกทันที", "เซ็นสัญญางานใหม่", "ปิดร้าน"])
    assert "ทางที่ย้อนกลับได้" not in r and "ทุกทางในนี้ย้อนกลับยาก" in r


def test_simulate_answers_in_english():
    r = simulate("I lost my job", ["quit and travel", "find new job"])
    assert "Start with" in r and "Downside: reversible" in r and "ย้อน" not in r


@pytest.mark.parametrize("text", ["My husband hits me, I'm hiding in the bathroom", "I feel stuck at work", "I want to die"])
def test_english_choice_count_matches_printed_steps(text, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    r = compose(text)
    m = re.search(r"Choice\(t\) = (\d+)", r)
    steps = len(re.findall(r"(?m)^\d+\)\s", r))
    if m and steps:
        assert int(m.group(1)) == steps


def test_ui_council_keyword_and_path_cap():
    assert r"สภา\s*[56]\s*เสียง" in HTML and "ให้ 6 มุมมอง" in HTML
    assert "if(n >= 7) return;" in HTML


def test_debt_reply_asks_only_for_what_is_missing():
    lines = analyze("หนี้บัตรเครดิต 80,000 เงินเดือน 25,000")["lines"]
    assert any("บอกรายจ่ายต่อเดือน" in l for l in lines) and not any("บอกรายได้" in l for l in lines)
