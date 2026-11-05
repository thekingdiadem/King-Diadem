"""จุดพักก่อนลงมือ (WORLD_MODEL/pause_point.py) — วัดได้ ตายตัว ไม่ใช้ศัพท์ทางศาสนา"""
import re
from pathlib import Path

import pytest

from WORLD_MODEL import observe
from WORLD_MODEL.pause_point import QUESTIONS, read

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("text,wait", [
    ("โกรธมาก เขาด่าฉันกลางที่ประชุม จะโพสต์ประจานคืนนี้เลยให้มันรู้", 60),
    ("ดีใจสุดๆ โอกาสทอง จะเอาเงินเก็บทั้งหมดลงทุนวันนี้เลย", 1440),
    ("หุ้นตกหนัก กลัวมาก จะเทขายหมดทันที", 10),
    ("ฉันมันโง่ ต้องเอาคืนให้ได้ จะรีบลาออกพรุ่งนี้", 1440),
    ("I'm furious, I'm going to text him right now and tell him off", 60),
])
def test_pause_when_feeling_meets_urge(text, wait):
    p = read(text)
    assert p.pause and p.wait_min == wait
    assert "ชวนพัก" in p.note()


@pytest.mark.parametrize("text", [
    "อยากถามเรื่องการทำบัญชีร้านค้า",
    "เสียใจมาก แฟนบอกเลิก",             # ความรู้สึกอย่างเดียว ไม่เร่ง = ฟังก่อน ไม่ต้องพัก
    "ขายหน้ามาก",                        # "ขายหน้า" ไม่ใช่การขาย
    "รีบส่งงานให้ทันวันนี้เลย",            # รีบแต่ไม่มีความรู้สึกแรง
])
def test_no_pause(text):
    p = read(text)
    assert not p.pause and p.note() == ""


def test_other_persons_action_is_not_users_action():
    assert read("เสียใจมาก แฟนบอกเลิก").acting == ""


def test_deterministic_and_capped():
    t = "โกรธมาก โมโห แค้น เกลียด ทันที เดี๋ยวนี้ รีบ คืนนี้เลย จะโพสต์"
    a, b = read(t), read(t)
    assert a == b and a.feeling <= 3 and a.urge <= 3


def test_world_model_carries_pause():
    w = observe("ฉันมันโง่ ต้องเอาคืนให้ได้ จะรีบลาออกพรุ่งนี้")
    assert w.pause.pause and "ควรพักก่อนลงมือ=24 ชั่วโมง" in w.note()
    assert not observe("สวัสดีค่ะ").pause.pause


_RELIGIOUS = re.compile(r"อวิชชา|สังขาร|วิญญาณ|นามรูป|สฬายตนะ|ผัสสะ|เวทนา|ตัณหา|อุปาทาน|ชาติ\s|ชรา|มรณะ|นิพพาน|"
                        r"นิโรธ|สมุทัย|ปฏิจจ|มรรค|ธรรม(?!ดา)|สติ|เมตตา|ปัญญา|กรรม|พุทธ")


def test_plain_language_no_religious_terms():
    doc = (ROOT / "docs" / "PAUSE_POINT.md").read_text(encoding="utf-8")
    assert not _RELIGIOUS.search(doc), _RELIGIOUS.search(doc)
    for q in QUESTIONS:
        assert not _RELIGIOUS.search(q)
        assert q in doc
    assert not _RELIGIOUS.search(read("โกรธมาก จะโพสต์ประจานคืนนี้เลย").note())
