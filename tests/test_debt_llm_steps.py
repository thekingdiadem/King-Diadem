"""หนี้ผ่อนไม่ไหว: LLM ต้องได้คำสั่งให้ตอบเป็นทางที่ทำได้จริง ไม่ใช่แค่ปลอบใจ

หน้าจอจริง: "หนี้บัตรเครดิต 50000 บาท ผ่อนไม่ไหวแล้ว" ได้คำตอบว่าเข้าใจความกังวล แล้วถามรายรับรายจ่าย
ไม่มีทางเลือกเลยสักข้อ ทั้งที่คำตอบจากสมการของระบบมี 3 ทางที่ทำได้ทันที
"""
from tests.conftest import FAKE_LLM


def _prompt(client, text):
    r = client.post("/run", json={"input": text})
    assert r.status_code == 200
    return FAKE_LLM["prompts"][-1] if FAKE_LLM["prompts"] else ""


def test_debt_message_asks_llm_for_concrete_steps(client):
    p = _prompt(client, "หนี้บัตรเครดิต 50000 บาท ผ่อนไม่ไหวแล้ว")
    assert "ผู้ใช้เดือดร้อนเรื่องหนี้" in p and "ห้ามตอบแค่ปลอบใจ" in p
    assert "1443" in p and "1213" in p
    assert "50,000" in p                                   # ตัวเลขที่ระบบคำนวณยังไปถึง LLM


def test_non_debt_message_has_no_debt_instruction(client):
    assert "ผู้ใช้เดือดร้อนเรื่องหนี้" not in _prompt(client, "อยากเปลี่ยนงานไปเป็นนักออกแบบ")
