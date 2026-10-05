"""waterline รายคน — เก็บเฉพาะตอนผู้ใช้เล่าสถานะเอง · ดูได้แค่ของตัวเอง · ผูกกับสวิตช์/ล้างความจำ"""

LOW  = {"energy": 10, "money": 0, "food_access": "none", "sleep_hours": 2, "safe_place": False}
HIGH = {"energy": 90, "money": 5000, "food_access": "good", "sleep_hours": 8, "safe_place": True}


def _wl(user):
    return user.get("/api/waterline").json()


def test_waterline_is_tracked_per_user_with_trend(user):
    for ctx in (LOW, LOW, HIGH, HIGH):
        user.post("/run", json={"input": "ช่วงนี้เป็นยังไงบ้าง", "context": ctx})
    out = _wl(user)
    assert len(out["points"]) == 4
    assert out["points"][0]["waterline"] > out["points"][-1]["waterline"]
    assert out["trend"] == "rising"


def test_default_state_is_not_recorded(user):
    """ทักทายเฉยๆ ไม่มี context — ไม่ใช่สภาพจริงของผู้ใช้ ห้ามบันทึก"""
    user.post("/run", json={"input": "สวัสดี"})
    assert _wl(user) == {"points": [], "latest": None, "trend": "unknown"}


def test_waterline_needs_login(client):
    assert client.get("/api/waterline").status_code == 401


def test_waterline_is_not_shared_between_users(user, client):
    user.post("/run", json={"input": "เหนื่อยมาก", "context": LOW})
    victim = user.email
    client.cookies.clear()
    client.post("/register", json={"email": "other_wl@test.co", "password": "secret12"})
    assert client.get(f"/api/waterline?email={victim}").json()["points"] == []


def test_memory_off_and_clear_cover_waterline(user):
    user.post("/run", json={"input": "เหนื่อย", "context": LOW})
    user.post("/api/memory", json={"action": "clear"})
    assert _wl(user)["points"] == []
    user.post("/api/memory", json={"action": "off"})
    user.post("/run", json={"input": "เหนื่อย", "context": LOW})
    user.post("/api/memory", json={"action": "on"})
    assert _wl(user)["points"] == []
