"""ไฟล์ที่เพิ่งต่อเข้าระบบ (ผ่าน core/engine_bridge):
DOMAINS/survival_engine (ภัยที่กำลังเจอ) · ENGINE/tool_executor (คิดเลข) · WORLD_MODEL/human_bias (กับดักความคิด)"""
import pytest

from core.engine_bridge import analyze
from core.kernel_voice import assess, compose
from tests.conftest import FAKE_LLM


# ── ภัยที่กำลังเจอ ───────────────────────────────────────────────────
@pytest.mark.parametrize("text, name", [
    ("น้ำท่วมบ้าน ตอนนี้น้ำถึงเอวแล้ว", "น้ำท่วม"),
    ("แผ่นดินไหว ตึกสั่นมาก", "แผ่นดินไหว"),
    ("ไฟไหม้ห้องข้างๆ ควันเต็มทางเดิน", "ไฟไหม้"),
    ("ได้ยินเสียงปืนแถวนี้", "เหตุยิงหรือระเบิด"),
])
def test_disaster_raises_risk_and_puts_safety_first(text, name):
    a = assess(text)
    assert a["disaster"]["name"] == name and a["text_risk"] >= 50      # เดิม Risk 0
    r = compose(text)
    assert r.startswith("ตอนนี้ความปลอดภัยของร่างกายมาก่อน") and "1784" in r


@pytest.mark.parametrize("text", ["ความรักแบบไฟไหม้ฟาง", "รถติดน้ำท่วมขัง", "เห็นข่าวน้ำท่วมภาคเหนือ",
                                  "ถ้าน้ำท่วมควรเตรียมอะไรบ้าง", "ดูหนังแผ่นดินไหวมา สนุกดี"])
def test_no_alarm_for_idioms_news_or_plans(text):
    a = assess(text)
    assert a["disaster"] is None and a["text_risk"] < 50


def test_flood_plan_question_still_gets_a_plan():
    lines = analyze("ถ้าน้ำท่วมควรเตรียมอะไรบ้าง")["lines"]
    assert lines[0].startswith("แผนเตรียมรับน้ำท่วม") and "1784" in lines[-1]


def test_run_disaster_goes_to_survival_route(client):
    d = client.post("/run", json={"input": "น้ำท่วมบ้าน ตอนนี้น้ำถึงเอวแล้ว"}).json()
    assert d["route"] == "survival" and d["risk_score"] >= 50
    prompt = FAKE_LLM["prompts"][-1]
    assert "ผู้ใช้กำลังเจอน้ำท่วม" in prompt and "เบรกเกอร์" in prompt


def test_disaster_note_never_reaches_the_user():
    from core.llm_gemini import scrub_internal
    assert scrub_internal("ขึ้นที่สูงก่อนนะคะ\n[ผู้ใช้กำลังเจอน้ำท่วม: ตอบสั้น]") == "ขึ้นที่สูงก่อนนะคะ"


# ── คิดเลข ───────────────────────────────────────────────────────────
@pytest.mark.parametrize("text, line", [
    ("ผ่อนเดือนละ 3,500 x 12 งวด รวมเท่าไหร่", "คิดเลข: 3,500 × 12 = 42,000"),
    ("1500+2300+800 เท่าไร", "คิดเลข: 1500 + 2300 + 800 = 4,600"),
    ("ห้อง 3x4 เมตร พื้นที่เท่าไหร่", "คิดเลข: 3 × 4 = 12"),
    ("100 ÷ 3 ได้เท่าไหร่", "คิดเลข: 100 ÷ 3 = 33.33"),
])
def test_calculation(text, line):
    assert line in analyze(text)["lines"]


@pytest.mark.parametrize("text", ["ร้านเปิด 24/7 ไหม", "ทำงาน 1-2 วัน ได้เท่าไหร่", "50/50 ดีไหม",
                                  "3x4 เมตร", "9**9**9 เท่าไหร่"])
def test_not_a_calculation(text):
    assert "calc" not in analyze(text)["data"]


# ── กับดักความคิดตอนตัดสินใจ ─────────────────────────────────────────
def test_sunk_cost_note_when_deciding():
    lines = analyze("ลงทุนไปแล้ว 2 แสน เสียดายมาก ควรไปต่อไหม")["lines"]
    assert any("ถ้าเริ่มจากศูนย์วันนี้" in l for l in lines)


@pytest.mark.parametrize("text", ["เสียดายเสื้อตัวนั้น", "ต้องรีบตัดสินใจ แน่นอนว่าดี"])
def test_no_bias_note_outside_decisions_or_for_broad_words(text):
    assert "bias" not in analyze(text)["data"]


def test_spent_money_is_not_money_left():
    """เดิม "ลงทุนไปแล้ว 2 แสน" ได้ "200,000 ÷ 150 ≈ 1,333 วัน" เหมือนเป็นเงินที่ยังมี"""
    assert "1,333 วัน" not in compose("ลงทุนไปแล้ว 2 แสน เสียดายมาก ควรไปต่อไหม")
    assert "≈" in compose("ตกงาน มีเงินเหลือ 30,000 บาท")


# ── ปุ่มหาความช่วยเหลือใกล้ตัว (ENGINE/map_bridge) ───────────────────────
from core.engine_bridge import nearby


def _labels(links):
    return [l["label"] for l in links]


def test_flood_gets_shelter_and_hospital_buttons(client):
    d = client.post("/run", json={"input": "น้ำท่วมบ้าน ตอนนี้น้ำถึงเอวแล้ว"}).json()
    assert _labels(d["help_links"]) == ["ศูนย์พักพิง/อพยพ", "โรงพยาบาล"]
    assert all(l["url"].startswith("https://www.google.com/maps/search/?api=1&query=") for l in d["help_links"])


@pytest.mark.parametrize("text, labels", [
    ("พ่อเจ็บหน้าอก หายใจไม่ออก", ["โรงพยาบาล"]),
    ("ร้านขายยาใกล้ฉันอยู่ตรงไหน", ["ร้านขายยา"]),
    ("รถเสียกลางทาง แถวนี้มีอู่ไหม", ["อู่ซ่อมรถ"]),
])
def test_nearby_buttons(text, labels):
    assert _labels(nearby(text)) == labels


def test_abuse_gets_police_button():
    a = assess("แฟนตบหน้าแล้วยึดโทรศัพท์ ไม่ให้เจอเพื่อน")
    assert "สถานีตำรวจ" in _labels(nearby("แฟนตบหน้า", a["disaster"], a["relationship"]))


@pytest.mark.parametrize("text", ["วันนี้อากาศดี", "หมอบอกว่าโรงพยาบาลนี้ดี", "เห็นข่าวน้ำท่วมภาคเหนือ"])
def test_no_buttons_for_ordinary_talk(client, text):
    assert "help_links" not in client.post("/run", json={"input": text}).json()


def test_location_never_sent_to_server():
    """ลิงก์ไม่มีพิกัด — แผนที่ในเครื่องผู้ใช้หาเอง"""
    url = nearby("ร้านขายยาใกล้ฉัน")[0]["url"]
    assert "@" not in url and "lat" not in url


def test_help_card_only_trusts_google_maps_links():
    import pathlib
    page = pathlib.Path(__file__).resolve().parent.parent.joinpath("static", "index.html").read_text(encoding="utf-8")
    assert "function helpCard" in page and "l.url.indexOf('https://www.google.com/maps/') === 0" in page
    assert "l: d.help_links" in page
    assert "l: Array.isArray(m.l)" in page          # เปิดแชทใหม่อีกครั้งแล้วปุ่มยังอยู่


# ── แผ่นดินไหวแต่ละที่ทำต่างกัน ──────────────────────────────────────────
# เดิมทุกคนได้ "หมอบ ป้องศีรษะ เกาะโต๊ะ" — ใช้ไม่ได้กับคนที่ขับรถ อยู่ริมทะเล หรือติดในลิฟต์
@pytest.mark.parametrize("text,place,must,must_not", [
    ("แผ่นดินไหว ตอนนี้ขับรถอยู่บนทางด่วน", "ในรถ", "จอดชิดซ้าย", "เกาะโต๊ะ"),
    ("อยู่ภูเก็ต แผ่นดินไหวแรงมาก", "ริมทะเล", "ขึ้นที่สูง", "เกาะโต๊ะ"),
    ("ติดในลิฟต์ แผ่นดินไหว", "ในลิฟต์", "กดปุ่มทุกชั้น", "เกาะโต๊ะ"),
    ("อยู่คอนโดชั้น 30 ตึกโยก", "ตึกสูง", "อย่าวิ่งลงบันได", "จอดชิดซ้าย"),
    ("แผ่นดินไหว อยู่ข้างนอกบนถนน", "ข้างนอก", "อย่าวิ่งเข้าไปในตึก", "เกาะโต๊ะ"),
    ("แผ่นดินไหว อยู่บนดอย", "เชิงเขา/บนดอย", "ดินถล่ม", "เกาะโต๊ะ"),
    ("แผ่นดินไหวตอนอยู่ในห้าง", "ที่คนเยอะ", "อย่าวิ่งไปที่ประตู", "จอดชิดซ้าย"),
    ("แผ่นดินไหว อยู่ในบ้าน", "ในบ้าน", "ปิดแก๊ส", "จอดชิดซ้าย"),
])
def test_quake_steps_depend_on_place(text, place, must, must_not):
    a = assess(text)
    d = a["disaster"]
    assert d["kind"] == "quake" and d["place"] == place and d["active"] and a["text_risk"] >= 60
    r = compose(text)
    assert must in r and must_not not in r and f"อยู่{place}" in r


def test_quake_without_place_asks_where():
    d = assess("แผ่นดินไหว")["disaster"]
    assert d["place"] is None and "ในรถ" in d["ask"]
    assert "ตอนนี้อยู่ที่ไหน" in compose("แผ่นดินไหว")


def test_run_tells_llm_the_place(client):
    client.post("/run", json={"input": "แผ่นดินไหว ตอนนี้ขับรถอยู่"})
    p = FAKE_LLM["prompts"][-1]
    assert "อยู่ในรถ" in p and "จอดชิดซ้าย" in p
