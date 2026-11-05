"""แผ่นดินไหวจริงจาก USGS — เจ้าของโปรเจกต์ตั้งใจเชื่อมตั้งแต่ PR แรกๆ (ROADMAP: Real-time disaster data · pending)
เดิมระบบรู้แค่ว่าผู้ใช้ "พูดถึง" แผ่นดินไหว แต่ไม่รู้ว่ามีเกิดขึ้นจริงไหม ขนาดเท่าไหร่ ห่างแค่ไหน"""
import time

import pytest

from core import quakes

NOW = int(time.time() * 1000)


def _geo(*rows):
    return {"features": [{"id": f"q{i}", "properties": {"mag": m, "place": pl, "time": NOW - mins * 60000, "tsunami": ts,
                                                        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/q%d" % i},
                          "geometry": {"coordinates": [lon, lat, 10]}} for i, (m, pl, lat, lon, mins, ts) in enumerate(rows)]}


FEED = _geo((6.1, "Mandalay, Myanmar", 21.9, 96.1, 35, 0),        # ~950 กม. จากกรุงเทพ
            (3.0, "Chiang Rai, Thailand", 19.9, 99.8, 10, 0),      # เล็กกว่า 3.5 → ไม่บอก
            (4.2, "Andaman Sea", 9.5, 96.0, 200, 0),
            (7.4, "Kamchatka, Russia", 53.0, 159.0, 90, 1),          # ไกล แต่ใหญ่มาก → บอก
            (5.0, "Chile", -33.0, -71.0, 60, 0),                     # ไกลและไม่ใหญ่พอ → ไม่บอก
            (5.8, "Tonga", -21.0, -175.0, 120, 0),                   # ไกล แต่ถึง 5.5 (ทำตึกเสียหายได้) → บอก
            (6.0, "Myanmar old", 21.0, 96.0, 60 * 30, 0))            # เกิน 24 ชม. → ไม่บอก


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch):
    monkeypatch.setattr(quakes, "_cache", {"at": 0.0, "ok": False, "items": []})


def test_near_and_big_quakes_are_picked_correctly():
    r = quakes.recent(get=lambda url: FEED, now_ms=NOW)
    assert r["ok"] and [q["place"] for q in r["near"]] == ["Mandalay, Myanmar", "Andaman Sea"]
    assert [q["place"] for q in r["world"]] == ["Kamchatka, Russia", "Tonga"]
    assert quakes.MIN_MAG_WORLD == 5.5
    assert 850 < r["near"][0]["km"] < 1050


def test_ai_is_given_the_real_numbers_only():
    note = quakes.llm_note(quakes.recent(get=lambda url: FEED, now_ms=NOW), now_ms=NOW)
    assert "M6.1" in note and "Mandalay" in note and "35 นาทีก่อน" in note and "ห้ามเพิ่มตัวเลขอื่น" in note
    assert "สึนามิ" in note                                                  # Kamchatka แจ้งเตือนสึนามิ


def test_quiet_day_says_nothing_found_not_made_up():
    r = quakes.recent(get=lambda url: _geo((2.6, "Somewhere", 14.0, 100.0, 5, 0)), now_ms=NOW)
    assert r["ok"] and not r["near"] and not r["world"]
    assert "ไม่พบแผ่นดินไหว" in quakes.llm_note(r, now_ms=NOW)


def test_usgs_down_means_no_guessing_and_no_crash():
    def boom(url):
        raise TimeoutError("usgs slow")
    r = quakes.recent(get=boom)
    assert r["ok"] is False and r["near"] == []
    assert "ห้ามเดา" in quakes.llm_note(r) and "tmd.go.th" in quakes.llm_note(r)


def test_cache_avoids_calling_usgs_every_message():
    calls = []
    def get(url):
        calls.append(url)
        return FEED
    quakes.recent(get=get, now_ms=NOW)
    quakes.recent(get=get, now_ms=NOW)
    assert len(calls) == 1


def test_one_failure_keeps_the_good_data():
    quakes.recent(get=lambda url: FEED, now_ms=NOW)
    quakes._cache["at"] -= quakes.TTL + 1                                     # แคชหมดอายุ
    def boom(url):
        raise OSError("blip")
    r = quakes.recent(get=boom, now_ms=NOW)
    assert r["ok"] and r["near"]


def test_chat_about_an_earthquake_attaches_real_data(client, app_module, monkeypatch):
    monkeypatch.setattr(quakes, "_http_get", lambda url: FEED)
    d = client.post("/run", json={"input": "เมื่อกี้แผ่นดินไหว ตึกสั่น"}).json()
    assert d["quakes"]["ok"] and d["quakes"]["near"][0]["mag"] == 6.1


def test_other_chats_do_not_call_usgs(client, monkeypatch):
    calls = []
    monkeypatch.setattr(quakes, "_http_get", lambda url: calls.append(url) or FEED)
    d = client.post("/run", json={"input": "นอนไม่หลับมาหลายวัน"}).json()
    assert "quakes" not in d and not calls


def test_public_endpoint(client, monkeypatch):
    monkeypatch.setattr(quakes, "_http_get", lambda url: FEED)
    r = client.get("/api/quakes").json()
    assert r["source"] == "USGS" and r["near"]


def test_card_shows_in_chat_and_links_only_to_usgs():
    from tests._front import front_page
    page = front_page()
    assert "function quakeCard(r)" in page and "q: d.quakes" in page
    assert "/^https:\\/\\/earthquake\\.usgs\\.gov\\//.test(q.url)" in page


# ── จุดบนลูกโลก (scope=map): 7 วัน · ใกล้ไทย M3.5+ · ทั่วโลก M5.5+ · ไม่ซ้ำ · สูงสุด 40 จุด ──
WEEK = _geo((5.9, "Fiji", -18.0, 178.0, 60 * 24 * 3, 0),            # 3 วันก่อน ทั่วโลก ≥5.5 → ขึ้นบนลูกโลก
            (4.8, "Peru", -12.0, -77.0, 60 * 24 * 2, 0),              # ไกลและเล็ก → ไม่ขึ้น
            (4.6, "Myanmar", 20.0, 96.0, 60 * 24 * 5, 0),             # ใกล้ไทย 5 วันก่อน → ขึ้น
            (6.2, "Old", 0.0, 0.0, 60 * 24 * 9, 0))                   # เกิน 7 วัน → ไม่ขึ้น
for _f in WEEK["features"]:
    _f["id"] = "w" + _f["id"]                                           # คนละเหตุการณ์กับฟีด 24 ชม. (USGS ใช้ id เดียวกันข้ามฟีด)


def test_map_points_cover_a_week_without_duplicates():
    feeds = {quakes.FEED: FEED, quakes.WEEK_FEED: WEEK}
    r = quakes.map_points(get=lambda url: feeds[url], now_ms=NOW)
    places = [q["place"] for q in r["points"]]
    assert r["ok"] and r["days"] == 7 and r["updated"]
    assert "Kamchatka, Russia" == places[0]                              # M7.4 ใหญ่มากขึ้นก่อน
    assert {"Mandalay, Myanmar", "Andaman Sea", "Fiji", "Myanmar", "Myanmar old"} <= set(places)   # Myanmar old (30 ชม.) อยู่ใน 7 วัน
    assert not {"Peru", "Old", "Chiang Rai, Thailand", "Chile"} & set(places)
    assert len(places) == len(set(places)) and all("hours" in q for q in r["points"])


def test_map_points_survive_one_feed_down():
    def get(url):
        if url == quakes.WEEK_FEED:
            raise OSError("down")
        return FEED
    r = quakes.map_points(get=get, now_ms=NOW)
    assert r["ok"] and r["points"]


def test_api_quakes_map_scope(app_module):
    from fastapi.testclient import TestClient
    r = TestClient(app_module.app).get("/api/quakes?scope=map")
    assert r.status_code == 200 and r.json()["ok"] is False and r.json()["points"] == []   # เทสต์ไม่ยิงเน็ตจริง = ไม่เดาจุด
