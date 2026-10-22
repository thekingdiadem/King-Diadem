"""core/kernel_voice — ลงทุนส่วนตัว (ทอง หุ้น กองทุน คริปโต) ไม่ใช่เรื่องเปิดธุรกิจ"""
import pytest
from core.kernel_voice import assess
from tests.conftest import FAKE_LLM


@pytest.mark.parametrize("text, first", [
    ("มีเงิน 10000 จะลงทุนทองดีไหม", "money"),
    ("อยากซื้อหุ้นปันผล", "money"),
    ("ออมทองเดือนละ 1000 ดีไหม", "money"),
    ("จะลงทุนเปิดร้านกาแฟ 2 แสน", "business"),
    ("ลงทุนหุ้นส่วนกับเพื่อนเปิดร้าน", "business"),     # หุ้นส่วน = ธุรกิจ
])
def test_topic(text, first):
    assert assess(text)["topics"][0] == first


def test_gold_answer_is_not_business_template(client):
    FAKE_LLM["mode"] = "fail"
    out = client.post("/run", json={"input": "มีเงิน 10000 จะลงทุนทองดีไหม"}).json()["ai_response"]
    assert "จุดคุ้มทุน" not in out and "ธุรกิจตัดสินกันที่ตัวเลข" not in out
    assert "3–5 ปี" in out
    assert "มีรายได้เข้ามา" not in out           # ผู้ใช้บอกว่ามีเงิน ไม่ได้บอกรายได้


def test_lost_everything_is_money_short_not_invest_plan(client):
    FAKE_LLM["mode"] = "fail"
    out = client.post("/run", json={"input": "เล่นคริปโตขาดทุนหมดตัว"}).json()["ai_response"]
    assert "3–5 ปี" not in out
