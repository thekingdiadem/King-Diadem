"""หน้าเว็บส่ง context ทุกครั้ง (client_voice, tone_notes, route_ui) — ไม่ได้แปลว่าผู้ใช้กรอก "สถานะของฉัน"

เดิมเช็กแค่ว่า context ไม่ว่าง: คนที่ไม่เคยกรอกสถานะถูกบันทึก waterline 100 / STABLE ทุกข้อความ
(แม้จะพิมพ์ว่า "ไม่มีข้าวกิน 3 วันแล้ว") และคำตอบแบบไม่มี AI แสดง W จากค่าเริ่มต้นแทน "W —"
"""
UI_CTX = {"client_voice": "auto", "tone_notes": "", "route_ui": "general"}


def test_has_user_state(app_module):
    f = app_module._has_user_state
    assert not f(UI_CTX) and not f({}) and not f(None) and not f([1])
    assert f({**UI_CTX, "energy": 30}) and f({"food_access": False})


def test_ui_context_alone_does_not_log_waterline(user, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    user.post("/run", json={"input": "ไม่มีข้าวกิน 3 วันแล้ว", "context": UI_CTX})
    pts = user.get("/api/waterline").json()
    pts = pts.get("points", pts) if isinstance(pts, dict) else pts
    assert not pts


def test_real_state_is_logged(user, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    user.post("/run", json={"input": "เหนื่อยมาก", "context": {**UI_CTX, "energy": 20, "sleep_hours": 3,
                                                               "mental_state": "stressed", "food_access": True,
                                                               "safe_place": True, "days_in_crisis": 2}})
    pts = user.get("/api/waterline").json()
    pts = pts.get("points", pts) if isinstance(pts, dict) else pts
    assert pts


def test_offline_reply_shows_unknown_w_without_state(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": "ไม่มีข้าวกิน 3 วันแล้ว", "context": UI_CTX}).json()
    assert "W 100" not in d["ai_response"]
