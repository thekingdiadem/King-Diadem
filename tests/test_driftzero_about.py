"""ผู้ใช้จริงคนแรกงงกับหน้าจอ DriftZero แล้วพิมพ์ถามในโหมดนั้นว่า "what does drift zero do?"
เดิมระบบเอาคำถามนั้นไปตรวจด่านเหมือนเป็นการตัดสินใจ แล้วถามคำถามเดิมกลับมาอีกรอบ"""
from fastapi.testclient import TestClient

from ENGINE.driftzero import audit, follow_up, is_about
from tests._front import front_page

ADS = "spend 10k on facebook ads"


def test_asking_what_it_does_gets_an_explanation():
    for q in ("what does drift zero do?", "DriftZero คืออะไร", "i'm confused :/", "how do i use this", "ใช้ยังไง", "help"):
        r = audit(q)
        assert r["verdict"] == "about" and r["asks"] == [] and r["gates"] == [], q
        assert "rules, not AI" in r["summary"]["en"] and "ตรวจด้วยกฎ" in r["summary"]["th"]


def test_question_in_the_middle_keeps_the_pending_asks():
    a = audit(ADS)
    keys = [q["key"] for q in a["asks"]]
    r = follow_up(a["text"], keys, "what does drift zero do?")
    assert r["verdict"] == "about" and [q["key"] for q in r["asks"]] == keys and r["text"] == ADS
    # อ่านคำอธิบายแล้วตอบต่อได้เลย ไม่ต้องเริ่มใหม่
    r2 = follow_up(r["text"], [q["key"] for q in r["asks"]], "1 i do it 2. i can't pay rent 3 1k")
    assert r2["verdict"] == "ask" and r2["waterline"]["floor"] == 1000


def test_real_decisions_and_answers_are_not_mistaken_for_questions():
    for t in (ADS, "1 i do it 2. i can't pay rent 3 1k", "บริษัทจะขยายสาขา", "งบ 2 ล้าน", "โรงงานจะปล่อยน้ำเสียลงคลองเพื่อลดต้นทุน",
              "we do not understand our customers so we will hire 5 researchers and spend 2M on it"):
        assert not is_about(t), t


def test_api_and_front_end():
    import app as appmod
    c = TestClient(appmod.app)
    d = c.post("/api/driftzero", json={"input": "what does drift zero do?"}).json()["audit"]
    assert d["verdict"] == "about" and d["talk"] is True
    assert "about: ['วิธีใช้', 'ask']" in front_page()
