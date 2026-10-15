"""ตัวเลขจากเรื่องที่ผู้ใช้เล่า: หนี้ที่บอกค่างวด · เงินที่มีอยู่จริง · กำไรร้านที่มีต้นทุนหลายรายการ

พบจากการไล่หาบั๊ก:
- "หนี้บ้าน 1,200,000 ผ่อนเดือนละ 12,000" — ทิ้งทั้งก้อนเพราะเห็นคำว่าเดือนละ แล้วเอายอดหนี้ไปคิดเป็นเงินพอใช้ 8,000 วัน
- คำตอบแบบไม่มี AI เอาตัวเลขเงินตัวแรก (เงินเดือน ค่าเช่า ราคารถ) ไปคิดเป็น "เงินที่เหลือ"
- กำไรร้านนับต้นทุนแค่รายการแรก: ยอดขาย 50,000 ต้นทุน 30,000 ค่าส่ง 15,000 ค่าแอด 10,000 = "กำไร 20,000"
"""
import pytest

from core.engine_bridge import _business, parse_debts
from core.kernel_voice import compose


@pytest.mark.parametrize("text,name,balance,rate", [
    ("หนี้บ้าน 1,200,000 บาท ผ่อนเดือนละ 12,000 เงินเดือน 40,000 ไหวไหม", "หนี้บ้าน", 1_200_000, 6),
    ("กู้ซื้อรถ 500,000 บาท ผ่อนเดือนละ 9,000 ทำไงดี", "หนี้รถ", 500_000, 6),
    ("หนี้ 1.5 ล้าน ผ่อนเดือนละ 15,000 เงินเดือน 40,000 ใช้จ่าย 20,000", "หนี้ก้อนที่ 1", 1_500_000, 18),
    ("ผ่อนบ้านเดือนละ 12,000 เหลือหนี้ 1,200,000 เงินเดือน 50,000 รายจ่าย 30,000", "หนี้บ้าน", 1_200_000, 6),
    ("หนี้รถ 300,000 จ่าย 7,000/เดือน", "หนี้รถ", 300_000, 6),
])
def test_installment_does_not_hide_the_debt(text, name, balance, rate):
    d = parse_debts(text)
    assert len(d) == 1 and d[0]["name"] == name and d[0]["balance"] == balance and d[0]["annual_rate"] == rate


@pytest.mark.parametrize("text", ["ผ่อนบ้านเดือนละ 8,000", "อยากซื้อบ้านราคา 2 ล้าน ผ่อนเดือนละ 15,000", "อยากซื้อรถ 500,000 ผ่อนไหวไหม"])
def test_installment_or_purchase_alone_is_not_a_debt(text):
    assert parse_debts(text) == []


@pytest.mark.parametrize("text", [
    "เงินเดือน 15,000 บาท ไม่พอใช้ ทำไงดี",
    "ค่าเช่าห้อง 5,000 บาท เงินไม่พอจ่าย",
    "อยากซื้อรถราคา 800,000 บาท เงินเดือน 25,000 คุ้มไหม",
])
def test_salary_rent_or_price_is_not_cash_on_hand(text, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    assert "เวลาที่มีจริง" not in compose(text)


def test_savings_use_stated_monthly_expense(monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    r = compose("มีเงินเก็บ 2 แสน รายจ่ายเดือนละ 20,000 ตกงาน")
    assert "200,000 ÷ 667 ≈ 300 วัน" in r and "10.0 เดือน" in r


@pytest.mark.parametrize("text,expect", [
    ("ขายของออนไลน์ ยอดขาย 50,000 ต้นทุน 30,000 ค่าส่ง 15,000 ค่าแอด 10,000", "ขาดทุน 5,000"),
    ("ร้านกาแฟ ยอดขายเดือนละ 1.2 แสน ต้นทุน 9.5 หมื่น ค่าเช่า 3 หมื่น", "ขาดทุน 5,000"),
    ("ร้านกาแฟ รายได้เดือนละ 120,000 ต้นทุน 95,000", "กำไร 25,000"),
    ("ร้าน ยอดขาย 100,000 ค่าใช้จ่ายรวม 70,000 ค่าเช่า 20,000", "กำไร 30,000"),      # บอกยอดรวมแล้ว ไม่บวกซ้ำ
    ("ขายแก้วละ 50 ต้นทุนแก้วละ 20", "กำไร 30 บาทต่อชิ้น"),
])
def test_business_counts_every_cost(text, expect):
    r = _business(text)
    assert r and any(expect in line for line in r["lines"]), r
