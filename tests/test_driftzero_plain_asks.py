"""คำถามที่ DriftZero ถามผู้ใช้ต้องไม่มีศัพท์ระบบ — การ์ดบอกว่า "ไม่ต้องรู้ศัพท์ในการ์ดเลย"
แต่ข้อ 2 ข้อ 3 เคยขึ้นต้นด้วย "Waterline:" และ "DHD:" (หน้าจอจริง พ.ย. 2569 · ขยายกิจการด้าน AI 5 แสน)"""
import re

import pytest

from ENGINE.driftzero import audit

CASES = ["จะใช้เงิน5แสนขยายกิจการนะ ตอนนี้กำลังทำด้านAIอยู่ ขาดอุปกรณ์ฮาร์ดแวร์และค่าบำรุงเซิฟเวอร์",
         "จะเปิดร้านกาแฟสาขาสอง ใช้เงินเก็บ 3 แสน", "We plan to spend 200k expanding the AI team"]
JARGON = re.compile(r"\b(?:DHD|Waterline|SOP|L0|DriftZero)\b")


@pytest.mark.parametrize("text", CASES)
def test_questions_to_the_user_have_no_system_jargon(text):
    for q in audit(text)["asks"]:
        assert not JARGON.search(q["th"]) and not JARGON.search(q["en"]), q
