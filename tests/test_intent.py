"""ขั้น "จับเจตนา" (AI/intent_engine.py)"""
import pytest

from AI.intent_engine import analyze_intent

CASES = [
    ("ตกงาน ไม่มีเงิน อยากตาย", "crisis"), ("ตกงาน ไม่มีเงิน หนี้ท่วม อยากตาย", "crisis"),
    ("ธุรกิจเจ๊ง ลูกค้าหาย อยากจบชีวิต", "crisis"), ("ไม่อยากอยู่แล้ว", "crisis"),
    ("ไม่มีความรู้สึกอะไรแล้ว", "general"), ("เริ่มมีความรู้สึกกับเพื่อนร่วมงาน", "love"),
    ("เป็นแฟนบอลแมนยู", "general"), ("ทะเลาะกับแฟน", "relationship"),
    ("สัญญาณมือถือไม่ดี", "general"), ("เซ็นสัญญาเช่าบ้าน", "civil"),
    ("ไม่มีเงินซื้อไอโฟน", "general"), ("ไม่มีเงินซื้อข้าว", "survival"),
    ("ไม่อยากอยู่แล้วที่ทำงานนี้", "civil"), ("ได้งานแล้ว ดีใจมาก", "work_win"),
    ("วิเคราะห์ระบบระยะยาว", "vega"), ("ควรทำยังไงดี", "question"), ("วันนี้อากาศดี", "general"),
    ("ถูกไล่ออกจากงาน", "survival"), ("ไม่ยินดีเลย", "general"), ("ไม่ตื่นเต้นเลย", "general"),
    ("มีความสุขมาก", "joy"), ("ยินดีด้วยนะ", "joy"), ("ตกหลุมรักเขาแล้ว", "love"),
]


@pytest.mark.parametrize("text,intent", CASES)
def test_intent(text, intent):
    assert analyze_intent(text)["intent"] == intent


def test_crisis_confidence_floor():
    r = analyze_intent("ตกงาน ไม่มีเงิน หนี้ท่วม อยากตาย")
    assert r["intent"] == "crisis" and r["confidence"] >= 0.9
