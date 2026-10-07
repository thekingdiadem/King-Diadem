"""หน้าจอจริง: เคสได้ยินเสียงผู้หญิงกรีดร้อง (Risk 70) LYLA ใส่ 🥺 ท้ายคำตอบ"""


def test_emoji_removed_when_risk_high(client):
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = "เป็นห่วงมากเลยนะคะ 🥺 โทร 191 ได้เลยค่ะ ✨"
    try:
        d = client.post("/run", json={"input": "ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง"}).json()
    finally:
        FAKE_LLM["text"] = None
    assert d["risk_score"] >= 60
    assert "🥺" not in d["ai_response"] and "✨" not in d["ai_response"] and "191" in d["ai_response"]


def test_emoji_kept_in_everyday_chat(client):
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = "ยินดีด้วยนะคะ 🎉"
    try:
        d = client.post("/run", json={"input": "สอบผ่านแล้ว"}).json()
    finally:
        FAKE_LLM["text"] = None
    assert d["risk_score"] < 60 and "🎉" in d["ai_response"]


def test_system_symbols_survive():
    import app
    assert app._strip_emoji("— LYLA ◈ ✦ ☸ ▲ 🤍") == "— LYLA ◈ ✦ ☸ ▲"
