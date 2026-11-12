"""DriftZero: คำตอบของผู้ใช้ต้องถูกนำไปคำนวณจริง และตอบครบแล้วต้องได้ "ใบสรุปการตัดสินใจ" กลับไป

ลองเคสของผู้ใช้จริงคนแรก (Haydn: "spend 10k on facebook ads") ซ้ำหลัง PR #180 แล้วยังเจอ 3 อย่าง:
  1) ข้อความแรกโดนบอกว่า "ดูเหมือนเป็นเรื่องส่วนตัว" ทั้งที่เป็นงบโฆษณาของกิจการ
  2) ตอบเส้นขั้นต่ำว่า "1k" แล้วตัววัด Waterline ไม่ได้ใช้เลขนั้น เพราะคำตอบถูกต่อท้ายแบบไม่มีป้ายบอกว่าเป็นคำตอบของข้อไหน
  3) ตอบครบแล้วได้แค่ "ผ่านทุกด่าน" ไม่มีอะไรให้เอาไปใช้ต่อ"""
from ENGINE.driftzero import audit, follow_up
from tests._front import front_page

ADS = "spend 10k on facebook ads"
HAYDN = "1 i do it 2. i can't pay rent 3 1k"


def _keys(r):
    return [q["key"] for q in r["asks"]]


def test_ad_budget_is_a_business_decision_not_personal():
    for t in (ADS, "จะยิงแอดเดือนละ 2 หมื่น", "raise our pricing by 20%"):
        a = audit(t)
        assert a["talk"] is False and a["note"] is None, t
    assert audit("ฉันควรเลิกกับแฟนไหม")["talk"] is True


def test_floor_answer_feeds_the_waterline_gauge():
    a = audit(ADS)
    r = follow_up(a["text"], _keys(a), HAYDN)
    assert r["waterline"]["floor"] == 1000 and r["waterline"]["spend"] == 10000
    # รู้เส้นขั้นต่ำแล้ว ข้อถัดไปที่ต้องถามคือ "ตอนนี้มีเท่าไหร่" และไม่ถามข้อที่ตอบแล้วซ้ำ
    assert _keys(r)[0] == "current"
    assert not {"detail", "downside", "floor"} & set(_keys(r))


def test_answers_turn_into_a_computed_stop():
    a = audit(ADS)
    r = follow_up(a["text"], _keys(a), HAYDN)
    r2 = follow_up(r["text"], _keys(r), "1 3k 2 cost per lead 3. me")
    assert r2["verdict"] == "stop" and r2["asks"] == []
    assert r2["waterline"]["after"] == -7000 and r2["waterline"]["level"] == "below"
    rule = r2["brief"]["rule"]
    assert "2,000" in rule["en"] and "2,000" in rule["th"]          # ทำได้มากสุดเท่าไหร่โดยไม่หลุดเส้น
    rows = {x["k"]: x["v"] for x in r2["brief"]["rows"]}
    assert rows == {"decision": ADS, "downside": "i can't pay rent", "floor": "1k", "current": "3k",
                    "dhd": "cost per lead", "owner": "me", "detail": "i do it"}


def test_enough_cash_passes_with_a_stop_rule():
    a = audit(ADS)
    r = follow_up(a["text"], _keys(a), HAYDN)
    r2 = follow_up(r["text"], _keys(r), "1 30k 2 cost per lead 3. me")
    assert r2["verdict"] == "pass"
    assert "20,000" in r2["brief"]["rule"]["en"] and "Stop rule" in r2["brief"]["rule"]["en"]


def test_no_brief_before_any_answer_and_same_text_same_result():
    assert audit(ADS)["brief"] is None
    a = audit(ADS)
    assert follow_up(a["text"], _keys(a), HAYDN) == follow_up(a["text"], _keys(a), HAYDN)


def test_multiline_answer_stays_on_its_own_line():
    a = audit(ADS)
    r = follow_up(a["text"], _keys(a), "1 me\nand my partner 2 lose the shop 3 5k")
    rows = {x["k"]: x["v"] for x in r["brief"]["rows"]}
    assert rows["detail"] == "me and my partner" and rows["floor"] == "5k"


def test_examples_in_questions_fit_a_small_business_too():
    asks = {q["key"]: q for q in audit(ADS)["asks"]}
    assert "money going out per day" in asks["dhd"]["en"] and "เงินออกวันละ" in asks["dhd"]["th"]
    assert "a name or a role" in asks["owner"]["en"]


def test_front_end_renders_brief_without_inline_handlers():
    page = front_page()
    assert "dzBrief(a.brief)" in page and "data-dz-copy" in page and ".dz-brief" in page
    assert "ใบสรุปการตัดสินใจ" in page
