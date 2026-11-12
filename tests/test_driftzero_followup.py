"""DriftZero ตอบต่อจากคำถามรอบก่อน — ผู้ใช้จริงคนแรก (Haydn) ตอบเป็นข้อ "1 i do it 2. i can't pay rent 3 1k"
แล้วระบบถามคำถามเดิมซ้ำครบ 5 ข้อ เพราะตรวจแค่ข้อความใหม่ และไม่รู้ว่า "จ่ายค่าเช่าไม่ไหว" เป็นความลำบากส่วนตัว"""
from fastapi.testclient import TestClient

from ENGINE.driftzero import audit, follow_up, parse_numbered, answered_keys
from tests._front import front_page

HAYDN = "1 i do it 2. i can't pay rent 3 1k"


def test_parse_numbered_answers():
    assert parse_numbered(HAYDN) == {1: "i do it", 2: "i can't pay rent", 3: "1k"}
    assert parse_numbered("1) ผมเอง\n2. ขาดทุน 3 แสน") == {1: "ผมเอง", 2: "ขาดทุน 3 แสน"}
    assert parse_numbered("ข้อ 1 บอร์ดอนุมัติ ข้อ 2 เสียลูกค้า") == {1: "บอร์ดอนุมัติ", 2: "เสียลูกค้า"}


def test_numbers_inside_a_sentence_are_not_item_numbers():
    assert parse_numbered("จ้าง 5 คน งบ 2 ล้าน") == {}
    assert parse_numbered("we hire 2 people") == {}
    # เลขข้อต้องเรียงกัน — "1 … 3 …" ไม่นับ 3 เป็นข้อใหม่
    assert parse_numbered("1 ทีมการตลาด 3 คน") == {1: "ทีมการตลาด 3 คน"}


def test_every_ask_has_a_stable_key():
    a = audit("we will expand to 5 new stores")
    keys = [q["key"] for q in a["asks"]]
    assert keys and len(keys) == len(set(keys))
    assert a["text"] == "we will expand to 5 new stores"


def test_follow_up_asks_only_what_is_still_missing():
    first = audit("we will expand to 5 new stores")
    keys = [q["key"] for q in first["asks"]]
    r = follow_up(first["text"], keys, HAYDN)
    assert set(r["answered"]) == set(keys[:3])
    left = [q["key"] for q in r["asks"]]
    # ตอบเส้นขั้นต่ำเป็นตัวเลขแล้ว ("3 1k") ข้อถัดไปจึงถามว่าตอนนี้มีเท่าไหร่ เพื่อคำนวณว่าหลุดเส้นไหม
    assert left == ["current"] + keys[3:]
    assert f"{len(left)} answer(s) are missing" in r["summary"]["en"]
    # รวมเรื่องเดิมไว้ ให้ตอบรอบต่อไปได้อีก
    assert "5 new stores" in r["text"] and "i do it" in r["text"]


def test_single_plain_answer_to_single_ask():
    assert answered_keys("คุณสมชาย ผู้จัดการ", ["owner"]) == {"owner"}
    assert answered_keys("คุณสมชาย", ["owner", "floor"]) == set()
    assert answered_keys(HAYDN, ["owner", "nonsense"]) == {"owner"}


def test_personal_hardship_in_answers_points_to_talk_mode():
    first = audit("we will expand to 5 new stores")
    r = follow_up(first["text"], [q["key"] for q in first["asks"]], HAYDN)
    assert r["talk"] is True
    assert "Talk mode" in r["note"]["en"] and "โหมดปรึกษา" in r["note"]["th"]


def test_business_answers_do_not_point_to_talk_mode():
    t = "บริษัทจะเปิดสาขาใหม่ 3 แห่ง ใช้งบ 20 ล้าน ภายในปีนี้"
    first = audit(t)
    assert first["talk"] is False
    r = follow_up(first["text"], [q["key"] for q in first["asks"]], "1 เสียเงินลงทุนทั้งหมด ลูกค้าเดิมไม่กระทบ 2 บอร์ดบริษัทเซ็นอนุมัติ")
    assert r["talk"] is False


def test_crisis_in_answer_still_goes_to_urgent():
    first = audit("we will expand to 5 new stores")
    r = follow_up(first["text"], [q["key"] for q in first["asks"]], "1 i want to kill myself")
    assert r["verdict"] == "urgent"


def test_api_accepts_prior(monkeypatch):
    import app as appmod
    c = TestClient(appmod.app)
    a = c.post("/api/driftzero", json={"input": "we will expand to 5 new stores"}).json()["audit"]
    keys = [q["key"] for q in a["asks"]]
    r = c.post("/api/driftzero", json={"input": HAYDN, "prior": {"text": a["text"], "asks": keys}}).json()["audit"]
    assert len(r["asks"]) < len(keys) and r["talk"] is True
    # prior ผิดรูปแบบ = ตรวจข้อความใหม่ตามเดิม ไม่ล้ม
    r2 = c.post("/api/driftzero", json={"input": HAYDN, "prior": {"text": 5, "asks": "x"}})
    assert r2.status_code == 200


def test_front_end_sends_prior_and_has_talk_button():
    page = front_page()
    assert "dzBody(text, prevDz)" in page and "lastDzAsk()" in page
    assert "data-dz-talk" in page and "ไปคุยในโหมดปรึกษา" in page
