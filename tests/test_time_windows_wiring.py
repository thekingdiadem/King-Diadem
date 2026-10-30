"""time_windows ต่อเข้าแชท (/run · /api/waterline) และแดชบอร์ด (/dashboard)
Choice ≈ Waterline ÷ 20 · Drift/วัน = ความชันขาลงของ waterline ÷ 20"""
from core.choice_dynamics import waterline_windows
from tests.conftest import FAKE_LLM


def _pts(*pairs):
    return [{"waterline": w, "at": at} for w, at in pairs]


def test_falling_waterline_gives_days():
    r = waterline_windows(_pts((60, "2026-10-10 10:00:00"), (70, "2026-10-05 10:00:00"), (80, "2026-10-01 10:00:00")))
    assert r["waterline_per_day"] < 0
    assert r["time_to_intervention_days"] == 10 and r["time_to_failure_days"] == 18     # 60 → 40 ราว 9–10 วัน
    assert r["status"] == "WATCH"


def test_rising_or_too_little_data():
    assert waterline_windows(_pts((80, "2026-10-10 10:00:00"), (50, "2026-10-01 10:00:00")))["status"] == "STABLE"
    assert waterline_windows(_pts((60, "2026-10-10 10:00:00"), (50, "2026-10-10 09:00:00")))["status"] == "NOT_ENOUGH_DATA"
    assert waterline_windows(None)["status"] == "NOT_ENOUGH_DATA"
    assert waterline_windows(_pts(("x", "2026-10-10"), (50, "bad-date")))["status"] == "NOT_ENOUGH_DATA"


def _seed(email, rows):
    from DATABASE.db import get_conn
    conn = get_conn()
    try:
        for w, at in rows:
            conn.execute("INSERT INTO waterline_log (user_email, waterline, state, created_at) VALUES (?,?,?,?)",
                         (email, w, "", at))
        conn.commit()
    finally:
        conn.close()


def _falling(days_ago_list=(9, 5, 1), start=80):
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return [(start - 10 * i, (now - timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")) for i, d in enumerate(days_ago_list)]


def test_api_waterline_and_chat_show_decision_window(user):
    _seed(user.email, _falling())
    tw = user.get("/api/waterline").json()["time_windows"]
    assert tw["status"] in ("WATCH", "EARLY_WARNING") and tw["time_to_intervention_days"] is not None
    FAKE_LLM["mode"] = "fail"
    r = user.post("/run", json={"input": "ช่วงนี้เหนื่อยมาก"}).json()
    assert r["time_windows"]["time_to_intervention_days"] == tw["time_to_intervention_days"]
    assert "inputs" not in r["time_windows"]           # ส่งเฉพาะที่หน้าเว็บใช้


def test_anonymous_chat_has_no_time_windows(client):
    FAKE_LLM["mode"] = "fail"
    assert "time_windows" not in client.post("/run", json={"input": "เหนื่อยมาก"}).json()


def test_memory_off_hides_time_windows(user):
    _seed(user.email, _falling())
    user.post("/api/memory", json={"action": "off"})
    FAKE_LLM["mode"] = "fail"
    assert "time_windows" not in user.post("/run", json={"input": "เหนื่อย"}).json()


def test_dashboard_counts_only(client, app_module):
    _seed("dash_tw@test.co", _falling())
    app_module._dw_cache.update(t=0.0, v={})
    d = client.get("/dashboard").json()["decision_windows"]
    assert set(d) >= {"EARLY_WARNING", "WATCH", "STABLE", "COLLAPSE", "NOT_ENOUGH_DATA"}
    assert all(isinstance(v, int) for v in d.values())
    assert sum(d[k] for k in ("WATCH", "EARLY_WARNING")) >= 1
    assert "dash_tw@test.co" not in client.get("/dashboard").text


def test_chat_page_renders_the_row():
    from pathlib import Path
    html = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")
    assert "d.time_windows" in html and "ช่วงตัดสินใจ" in html and "core/choice_dynamics.py" in html
