"""👍/👎 ใต้คำตอบ → core/feedback_loop (DATABASE/decision_history · AI/reality_feedback · AI/reality_learning)"""
import pathlib

import pytest

from core import feedback_loop


def test_vote_is_saved_and_counted(client):
    before = client.get("/api/feedback/stats").json()["votes"]
    r = client.post("/api/feedback", json={"vote": "up", "route": "survival", "risk": 64})
    assert r.status_code == 200 and r.json() == {"ok": True, "saved": True}
    s = client.get("/api/feedback/stats").json()
    assert s["votes"] == before + 1 and any(x["route"] == "survival" for x in s["routes"])


def test_only_route_risk_and_vote_are_stored(client):
    """ไม่เก็บข้อความผู้ใช้ แม้ client จะส่งมา"""
    client.post("/api/feedback", json={"vote": "down", "route": "risk", "risk": 80, "text": "ความลับของฉัน"})
    from DATABASE.decision_history import get_recent_decisions
    row = get_recent_decisions(limit=1, domain="feedback")[0]
    assert row["route"] == "risk" and row["strategy"] == "down" and row["risk_level"] == "critical"
    assert "ความลับ" not in str(row)


@pytest.mark.parametrize("payload", [{"vote": "maybe"}, {}, {"vote": ["up"]}])
def test_bad_vote_rejected(client, payload):
    assert client.post("/api/feedback", json=payload).status_code == 400


def test_unknown_route_and_odd_risk_are_cleaned():
    assert feedback_loop._clean("UP", "<script>", "nan") == ("up", "general", 0)
    assert feedback_loop._clean("down", "vega", 1e9) == ("down", "vega", 100)


def test_votes_survive_restart():
    """เดิม feedback อยู่ในหน่วยความจำ — deploy ใหม่แล้วหายหมด"""
    from AI import reality_feedback
    feedback_loop.record("up", "general", 10)
    reality_feedback._STORE.clear()
    assert feedback_loop.warm() >= 1 and reality_feedback.feedback_stats()["samples"] >= 1


def test_health_shows_feedback(client):
    assert "votes" in client.get("/health").json()["feedback"]


def test_page_sends_no_message_text():
    page = pathlib.Path(__file__).resolve().parent.parent.joinpath("static", "index.html").read_text(encoding="utf-8")
    body = page[page.index("function vote(m, v, el)"):][:700]
    assert "fetch('/api/feedback'" in body
    assert "JSON.stringify({ vote:v, route:t.route || 'general', risk:num(t.risk, 0) })" in body
    assert "v: (m.v === 'up' || m.v === 'down')" in page          # โหวตแล้วยังจำได้หลังรีโหลด
