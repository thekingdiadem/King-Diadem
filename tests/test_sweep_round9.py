"""รอบหาบั๊ก 9: หัวข้อใหม่ต้องบอก LLM ด้วย ไม่ใช่แค่คำตอบจากสมการ"""
import pytest
from tests.conftest import FAKE_LLM


@pytest.mark.parametrize("text, must", [
    ("ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง", "191"),
    ("ลูกเอาเงินบำนาญแม่ไปหมด ไม่ให้กินข้าว", "1300"),
    ("ตำรวจเรียกรับเงิน", "1567"),
    ("หมดเงิน อาหารเหลือมื้อเดียว", "1300"),
])
def test_llm_gets_the_steps(client, text, must):
    """หน้าจอจริง: "ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง" ได้ Risk 70 แต่ LLM ถามกลับว่าเสียงดังแค่ไหน ไม่บอก 191"""
    client.post("/run", json={"input": text})
    assert must in FAKE_LLM["prompts"][-1]
