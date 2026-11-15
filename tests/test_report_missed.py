"""ปุ่มรายงาน "ระบบไม่เห็นว่าเรื่องนี้ด่วน/อันตราย" + แนบประโยคที่พิมพ์ (ผู้ใช้เลือกเอง)"""
import time
from pathlib import Path

import pytest

from core import answer_reports as ar

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _db(monkeypatch, tmp_path):
    import DATABASE.db as db
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"), raising=False)
    monkeypatch.setattr(ar, "_ready", False)
    yield


def test_question_kept_only_when_sent_and_scrubbed():
    assert ar.record("missed", "คำตอบ", question="เบอร์ฉัน 081-234-5678 อีเมล a.b@x.com แค่คิดว่าพรุ่งนี้คงไม่ต้องตื่น โทร 1323")["ok"]
    q = ar.recent(1)[0]["question"]
    assert "081" not in q and "a.b@x.com" not in q and "[ตัวเลข]" in q and "[อีเมล]" in q
    assert "1323" in q and "ไม่ต้องตื่น" in q                 # เบอร์สายด่วนสั้นๆ และเนื้อหายังอยู่
    assert ar.missed_questions()[0]["question"] == q


def test_question_forgotten_after_90_days():
    ar.record("missed", "คำตอบ", question="ประโยคเก่า")
    assert ar.forget_old_questions(time.time() + 91 * 86400) == 1
    assert ar.recent(1)[0]["question"] == "" and ar.recent(1)[0]["answer"] == "คำตอบ"


def test_server_ignores_question_unless_user_ticked():
    src = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'data.get("question") if data.get("include_question") is True else None' in src


def test_dialog_checkbox_is_off_by_default_and_reset_each_time():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'value="missed"' in html and '<input type="checkbox" id="rp-incq">' in html     # ไม่มี checked
    assert "$('#rp-incq').checked = false;" in js
    assert "question: $('#rp-incq').checked ? askedBefore(m)" in js


def test_housekeeping_runs_the_90_day_purge():
    from core import housekeeping
    assert "report_questions" in dict(housekeeping.STEPS)


def test_privacy_line_matches_what_is_sent():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'id="rp-priv"' in html and 'id="rp-priv-q" hidden' in html
    assert "$('#rp-incq').addEventListener('change', rpPriv);" in js
