"""เครื่องยนต์ 4 ตัวที่เพิ่งต่อสาย (core/engine_bridge): หนี้ · เวลาที่มีจริง · ความสัมพันธ์ · เรียงทางเลือก"""
import pytest

from core.engine_bridge import analyze, parse_debts, rank_options
from core.kernel_voice import assess, compose, simulate
from tests.conftest import FAKE_LLM

DEBTS = "หนี้บัตรเครดิต 50,000 ดอก 16% และสินเชื่อบุคคล 1.2 แสน ดอก 25% เงินเดือน 18,000 รายจ่าย 12,000"


# ── หนี้ ────────────────────────────────────────────────────────────
def test_parse_debts_keeps_thousand_separators():
    """เดิมแบ่งด้วยลูกน้ำ ทำให้ 50,000 ขาดเป็นสองท่อน"""
    d = parse_debts(DEBTS)
    assert [(x["balance"], x["annual_rate"]) for x in d] == [(50000, 16), (120000, 25)]


def test_debt_plan_from_income_and_expense():
    lines = " ".join(analyze(DEBTS)["lines"])
    assert "170,000" in lines and "6,000 บาท/เดือน" in lines and "เดือน" in lines


def test_debt_without_income_asks_for_it_and_marks_assumed_rate():
    lines = analyze("มีหนี้บัตร 3 หมื่น กับกยศ 80,000")["lines"]
    assert "2 ก้อน" in lines[0] and "*" in lines[0]
    assert any("รายได้และรายจ่าย" in l for l in lines)


def test_informal_loan_monthly_rate_and_legal_cap():
    lines = " ".join(analyze("กู้นอกระบบ 20,000 ดอก 20% ต่อเดือน เงินเดือน 15000 ค่าใช้จ่าย 14000")["lines"])
    assert "240%" in lines and "15% ต่อปี" in lines and "ไม่พอแม้แต่ดอกเบี้ย" in lines


def test_installment_is_not_a_balance():
    assert parse_debts("ผ่อนบ้านเดือนละ 8,000 ไม่ไหวแล้ว") == []


# ── เวลาที่มีจริง ───────────────────────────────────────────────────
def test_runway_names_what_runs_out_first():
    lines = analyze("เหลือเงิน 500 บาท ข้าวเหลือ 2 มื้อ")["lines"]
    assert "2.94 วัน" in lines[0] and "0.67 วัน" in lines[0]
    assert "อาหาร" in lines[1]


def test_runway_without_shelter_points_to_1300():
    assert any("1300" in l for l in analyze("เหลือเงิน 300 บาท ไม่มีที่อยู่")["lines"])


# ── ความสัมพันธ์ ────────────────────────────────────────────────────
def test_abuse_puts_safety_first():
    text = "แฟนตบหน้าแล้วยึดโทรศัพท์ ไม่ให้เจอเพื่อน"
    a = assess(text)
    assert a["relationship"] == "collapse_risk" and a["text_risk"] >= 90
    r = compose(text)
    assert r.startswith("ความปลอดภัยของคุณมาก่อนทุกอย่าง")
    assert "191" in r and "24–72" not in r            # เดิมแนะนำให้รอ 24–72 ชม.


@pytest.mark.parametrize("text", ["แฟนบอลไทยดีใจมาก", "แม่ทำกับข้าวอร่อย", "วันนี้อากาศดี"])
def test_no_relationship_flags_for_ordinary_talk(text):
    assert "relationship" not in analyze(text)["data"]


def test_run_abuse_raises_route_and_risk(client):
    d = client.post("/run", json={"input": "สามีทุบตีทุกวัน ไม่ให้ออกจากบ้าน"}).json()
    assert d["route"] in ("risk", "survival", "collapse") and d["risk_score"] >= 80
    assert "ตัวเลขที่ระบบคำนวณ" in FAKE_LLM["prompts"][-1]


# ── เรียงทางเลือก ───────────────────────────────────────────────────
def test_reversible_option_ranks_first():
    r = rank_options(["ลาออกไปทำร้านกาแฟ", "ทำงานเดิมแล้วขายกาแฟวันหยุด"], waterline=30)
    assert r[0]["action"] == "ทำงานเดิมแล้วขายกาแฟวันหยุด" and not r[1]["reversible"]


def test_simulate_recommends_reversible_path():
    out = simulate("ลังเลเรื่องงาน", ["ลาออกไปเปิดร้าน", "ขอลดเวลางานแล้วลองขายออนไลน์"])
    assert "แนะนำเริ่มจาก B" in out


# ── ไม่ทำให้เรื่องอื่นเพี้ยน ────────────────────────────────────────
@pytest.mark.parametrize("text", ["วันนี้อากาศดี", "อยากเปิดร้านกาแฟ ลงทุน 200,000", "อยากตาย"])
def test_no_bridge_output_without_signals(text):
    assert analyze(text)["lines"] == []


# ── อ่านเฉพาะสิ่งที่ผู้ใช้บอกจริง (รอบหาบั๊ก) ──────────────────────────
@pytest.mark.parametrize("text", [
    "ผมมีเงินเดือน 15,000 แต่ใช้ไม่พอ",     # เงินเดือน ≠ เงินที่เหลือ
    "เหลืออยู่ 3 วันก่อนสอบ",               # วัน ≠ บาท
    "มีเงินเก็บ 50,000 ควรลงทุนอะไร",
])
def test_no_runway_from_salary_or_days(text):
    assert "runway" not in analyze(text)["data"]


def test_meals_are_not_money():
    lines = analyze("ข้าวเหลือแค่ 2 มื้อ")["lines"]
    assert lines == ["เวลาที่มีจริง: อาหาร 2 มื้อ ≈ 0.67 วัน"]


@pytest.mark.parametrize("text", ["ซื้อบัตรคอนเสิร์ต 3,500 บาท ดีไหม", "อยากซื้อรถ 500,000 ดีไหม", "บ้านราคา 2 ล้าน น่าซื้อไหม"])
def test_prices_are_not_debts(text):
    assert parse_debts(text) == []


def test_friend_loan_has_no_assumed_interest():
    d = parse_debts("ยืมเงินเพื่อนมา 2,000 ยังไม่คืน")
    assert d[0]["name"] == "เงินยืม" and d[0]["annual_rate"] == 0


@pytest.mark.parametrize("text, hit", [("พ่อตีหัวผมเพราะสอบตก", True), ("โดนแฟนตีจนช้ำ", True), ("ไปตีกอล์ฟกับแฟน", False)])
def test_hitting_words(text, hit):
    assert ("relationship" in analyze(text)["data"]) is hit


def test_register_needs_8_characters(client):
    r = client.post("/register", json={"email": "short@test.co", "password": "abc1234"})
    assert r.status_code == 400 and "8" in r.json()["message"]


def test_abuse_disclosure_asks_llm_for_calm_tone(client):
    """LYLA เคยเปิดด้วย "ฉันตกใจมาก" กับคนที่เล่าว่าพ่อตีหัว"""
    client.post("/run", json={"input": "พ่อตีหัวผมเพราะสอบตก"})
    prompt = FAKE_LLM["prompts"][-1]
    assert "ไม่แสดงความตกใจ" in prompt and "ไม่ตัดสินหรือโทษใคร" in prompt


def test_no_abuse_guidance_for_ordinary_talk(client):
    client.post("/run", json={"input": "แม่ทำกับข้าวอร่อยมาก"})
    assert "ไม่แสดงความตกใจ" not in FAKE_LLM["prompts"][-1]
