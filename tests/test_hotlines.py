"""ทะเบียนเบอร์ช่วยเหลือ (core/hotlines.py) — เจ้าของโปรเจกต์: "ไม่มั่นใจว่าเบอร์ไหนจะใช้ได้ไม่ได้"
เบอร์ที่บอกผู้ใช้ต้องมาจากทะเบียนเดียว มีแหล่งอ้างอิง — พิมพ์ผิด/เดาเบอร์ใหม่ในคำตอบ เทสต์ล้ม"""
import re
from pathlib import Path

import pytest

from core import hotlines as hl

ROOT = Path(__file__).resolve().parent.parent
ANSWER_FILES = ["core/kernel_voice.py", "core/knowledge_th.py", "core/knowledge_edu.py", "core/lang_signals.py",
                "core/world_replies.py", "core/engine_bridge.py", "core/survival_guide.py", "core/companion.py"]
# เบอร์ที่ตามหลังคำบอกให้โทร — ไม่นับตัวเลขอื่น (ปี ราคา ระยะทาง)
CALL = re.compile(r"(?:โทร|สายด่วน|\bcall\b|\bdial\b|\bhotline\b|Lifeline|Samaritans|Poison Control)\D{0,30}?"
                  r"((?<![\d.,])(?:1-800-\d{3}-\d{4}|13 ?11 ?14|116 ?123|1\d{3}|[1-9]\d{2}|000)(?![\d.,%]))", re.I)


def test_every_entry_names_its_official_source():
    for country, lines in hl.REGISTRY.items():
        for ln in lines:
            assert ln.th and ln.en and ln.kind and "." in ln.source, (country, ln)
    assert hl.REVIEWED


@pytest.mark.parametrize("path", ANSWER_FILES)
def test_numbers_told_to_users_are_in_the_registry(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    unknown = sorted({m.group(1) for m in CALL.finditer(text)} - hl.all_numbers())
    assert not unknown, f"{path}: เบอร์ที่ไม่อยู่ในทะเบียน {unknown} — ตรวจกับเว็บทางการแล้วเพิ่มใน core/hotlines.py"


def test_hotline_constants_match_the_registry():
    import core.kernel_voice as kv
    consts = {v for k, v in vars(kv).items() if k.startswith("HOTLINE_") and isinstance(v, str)}
    assert consts <= {ln.number for ln in hl.REGISTRY["TH"]}, consts - hl.all_numbers()


def test_unknown_countries_get_a_directory_not_a_guessed_number():
    assert any(d[0] == "findahelpline.com" for d in hl.DIRECTORIES)
    assert hl.get("TH", "utility") and {ln.number for ln in hl.get("TH", "utility")} == {"1130", "1129", "1125", "1662"}


def test_cut_off_answers_use_utility_numbers():
    from core.kernel_voice import compose
    assert "1130" in compose("ไม่มีเงินจ่ายค่าไฟ การไฟฟ้าจะมาตัดพรุ่งนี้")
    assert "1125" in compose("ค้างค่าน้ำสามเดือน การประปาจะมาตัด")
    en = compose("the power company is shutting off our electricity friday")
    assert "211" in en and "payment plan" in en
