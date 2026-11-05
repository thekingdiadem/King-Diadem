"""สัญญาณการพึ่งพา — FATE™ Ethical Kernel ข้อ 5
คนที่คุยเรื่องหนักใจเรื่องเดิมทุกวัน LYLA ช่วยได้ แต่ไม่ควรเป็นที่พึ่งเดียว → ชวนให้มีคนจริงข้างๆ วันละครั้ง"""
import uuid

from core import companion as cp

T = "2026-11-05"


def test_four_days_of_the_same_heavy_topic_in_a_week_raises_the_signal():
    hist = {"2026-11-01": {"lonely": 1}, "2026-11-02": {"lonely": 2}, "2026-11-04": {"lonely": 1}, T: {"lonely": 1}}
    sig = cp.signal(hist, T)
    assert sig == {"topic": "lonely", "kind": "days", "days": 4}
    msg = cp.message(sig)
    assert "4 วัน" in msg["th"] and "คนที่ไว้ใจ" in msg["th"] and "1323" in msg["th"] and "1323" in msg["en"]


def test_three_days_is_ordinary_not_dependency():
    assert cp.signal({"2026-11-03": {"stress": 1}, "2026-11-04": {"stress": 1}, T: {"stress": 1}}, T) is None


def test_many_times_in_one_day_also_counts():
    sig = cp.signal({T: {"relationship": cp.BURST_MIN}}, T)
    assert sig["kind"] == "burst" and "1323" not in cp.message(sig)["th"]   # เรื่องความรักไม่ต้องยัดสายด่วนสุขภาพจิต


def test_everyday_topics_never_count():
    assert cp.heavy_topics(["money", "study", "business", "positive"]) == []
    assert cp.signal({d: {"money": 9} for d in ("2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04", T)}, T) is None


def test_only_once_a_day():
    hist = {d: {"grief": 1} for d in ("2026-11-01", "2026-11-02", "2026-11-03", T)}
    assert cp.signal(hist, T)
    hist[T][cp.SHOWN] = 1
    assert cp.signal(hist, T) is None


def test_run_invites_a_real_person_once_and_stores_no_text(client, app_module, monkeypatch):
    from DATABASE.db import get_conn, topic_days_add
    monkeypatch.setenv("KD_AI", "off")
    ident = "ip:" + client.headers["cf-connecting-ip"]
    who = app_module._mkey("companion", ident)
    for d in ("2026-11-01", "2026-11-02", "2026-11-03"):                    # สามวันก่อนหน้าคุยเรื่องเหงา
        topic_days_add(d, who, ["lonely"], "2026-10-20")
    monkeypatch.setattr(app_module, "_today", lambda: "2026-11-04")
    text = "รู้สึกเหงามากเลย ไม่มีใครคุยด้วย " + uuid.uuid4().hex[:6]
    first = client.post("/run", json={"input": text}).json()
    assert "คนที่ไว้ใจ" in first["companion"]["th"]
    again = client.post("/run", json={"input": "ยังเหงาอยู่เลย"}).json()
    assert "companion" not in again                                          # วันละครั้ง ไม่ตามตื๊อ
    conn = get_conn()
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(topic_days)").fetchall()]
        stored = " ".join(str(v) for r in conn.execute("SELECT * FROM topic_days").fetchall() for v in tuple(r))
    finally:
        conn.close()
    assert cols == ["day", "who", "topic", "n"] and text not in stored and "@" not in stored and ident not in stored


def test_crisis_messages_get_hotlines_not_this_card(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    assert "companion" not in client.post("/run", json={"input": "อยากตาย"}).json()


def test_card_is_saved_with_the_chat_and_rendered():
    from tests._front import front_page
    page = front_page()
    assert "c: d.companion" in page and "companionCard(m.c)" in page and "function companionCard(c)" in page
