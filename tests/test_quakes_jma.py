"""ชินโดะจาก JMA — ปิดข้อ Real-time disaster data (USGS · JMA) ใน ROADMAP Phase 4
USGS บอกขนาด M แต่ไม่บอกว่าคนในญี่ปุ่นรู้สึกแรงแค่ไหน JMA บอกเป็นชินโดะ (1–7) ซึ่งคนญี่ปุ่นคุ้นกว่า"""
import time

import pytest

from core import quakes

NOW = int(time.time() * 1000)


def _jst(mins_ago):
    from datetime import datetime, timedelta, timezone
    return datetime.fromtimestamp((NOW - mins_ago * 60000) / 1000, timezone(timedelta(hours=9))).isoformat()


USGS = {"features": [{"id": "us1", "properties": {"mag": 6.0, "place": "Noto, Japan", "time": NOW - 30 * 60000, "tsunami": 0},
                      "geometry": {"coordinates": [137.05, 37.25, 10]}}]}
JMA = [
    {"eid": "E1", "at": _jst(29), "anm": "石川県能登地方", "en_anm": "Noto, Ishikawa Prefecture", "cod": "+37.3+137.0-10000/", "mag": "5.9", "maxi": "5+"},
    {"eid": "E1", "at": _jst(29), "anm": "石川県能登地方", "cod": "+37.3+137.0-10000/", "mag": "5.8", "maxi": "5-"},   # ฉบับเก่ากว่าของเหตุเดียวกัน
    {"eid": "E2", "at": _jst(60), "en_anm": "Off\u200b Ibaraki", "cod": "+36.3+140.6-50000/", "mag": "5.2", "maxi": "4"},      # M ไม่ถึง 5.5 แต่ชินโดะ 4
    {"eid": "E3", "at": _jst(70), "en_anm": "Chiba", "cod": "+35.6+140.1-40000/", "mag": "3.1", "maxi": "2"},             # เล็ก ไม่บอก
    {"eid": "E4", "at": _jst(5), "ttl": "震度速報", "maxi": "3"},                                                         # ยังไม่รู้ศูนย์กลาง → ข้าม
]


def _get(url):
    return JMA if "jma" in url else USGS


@pytest.fixture(autouse=True)
def _fresh(monkeypatch):
    monkeypatch.setattr(quakes, "_cache", {"at": 0.0, "ok": False, "items": []})
    monkeypatch.setattr(quakes, "_jcache", {"at": 0.0, "ok": False, "items": []})


def test_parse_keeps_latest_report_and_skips_unlocated():
    rows = quakes.parse_jma(JMA)
    assert [r["id"] for r in rows] == ["jmaE1", "jmaE2", "jmaE3"]
    assert rows[0]["shindo"] == "5+" and rows[0]["depth"] == 10 and abs(rows[0]["lat"] - 37.3) < 1e-9
    assert quakes.parse_jma({"features": []}) == [] and quakes.parse_jma(None) == []


def test_shindo_order_is_not_string_order():
    assert quakes.shindo_rank("5+") > quakes.shindo_rank("5-") > quakes.shindo_rank("4") > quakes.shindo_rank(None)


def test_usgs_quake_gets_jma_shindo_and_japan_list_adds_felt_ones():
    r = quakes.recent(get=_get, now_ms=NOW, jma=True)
    assert r["world"][0]["shindo"] == "5+"                                  # จับคู่กับ USGS แล้ว ไม่ซ้ำใน japan
    assert [j["place"] for j in r["japan"]] == ["Off Ibaraki"]
    note = quakes.llm_note(r, now_ms=NOW)
    assert "ชินโดะสูงสุด 5+" in note and "Off Ibaraki" in note and "JMA" in note


def test_jma_down_does_not_hurt_usgs():
    def get(url):
        if "jma" in url:
            raise TimeoutError("jma slow")
        return USGS
    r = quakes.recent(get=get, now_ms=NOW, jma=True)
    assert r["ok"] and r["jma_ok"] is False and r["japan"] == [] and "shindo" not in r["world"][0]
    assert "JMA" not in quakes.llm_note(r, now_ms=NOW)


def test_default_does_not_call_jma():
    calls = []
    quakes.recent(get=lambda url: calls.append(url) or USGS, now_ms=NOW)
    assert not any("jma" in c for c in calls)


def test_chat_uses_jma(client, monkeypatch):
    monkeypatch.setattr(quakes, "_http_get", _get)
    d = client.post("/run", json={"input": "เมื่อกี้แผ่นดินไหว ตึกสั่น"}).json()
    assert d["quakes"]["jma_ok"] and d["quakes"]["japan"][0]["shindo"] == "4"


def test_naive_jma_timestamp_is_read_as_jst_not_server_time():
    # ถ้าสตริงเวลาไม่มีโซน (+09:00) ต้องถือเป็น JST ไม่ใช่เวลาเครื่อง (UTC) ไม่งั้นเพี้ยน 9 ชม.
    from datetime import datetime, timedelta, timezone
    naive = "2026-11-17T12:00:00"
    aware = "2026-11-17T12:00:00+09:00"
    assert quakes._jst_ms(naive) == quakes._jst_ms(aware)
    expect = int(datetime(2026, 11, 17, 12, 0, tzinfo=timezone(timedelta(hours=9))).timestamp() * 1000)
    assert quakes._jst_ms(naive) == expect


def test_same_quake_far_apart_solutions_is_not_listed_twice():
    # USGS กับ JMA คำนวณศูนย์กลางเหตุนอกชายฝั่งเดียวกันต่างกัน ~250 กม. (เกินกรอบจับคู่ 150 กม.)
    usgs = {"features": [{"id": "u", "properties": {"mag": 6.4, "place": "off Fukushima", "time": NOW - 20 * 60000, "tsunami": 0},
                          "geometry": {"coordinates": [142.0, 37.5, 20]}}]}
    jma = [{"eid": "J", "at": _jst(20), "en_anm": "Off Fukushima", "cod": "+37.4+139.5-20000/", "mag": "6.2", "maxi": "5-"}]
    r = quakes.recent(get=lambda url: jma if "jma" in url else usgs, now_ms=NOW, jma=True)
    places = [q["place"] for q in r["world"] + r["near"]] + [j["place"] for j in r["japan"]]
    assert places.count("off Fukushima") + places.count("Off Fukushima") == 1       # ครั้งเดียว ไม่ซ้ำ
    assert quakes.llm_note(r, now_ms=NOW).count("M6") == 1


def test_one_shindo_is_not_pinned_to_two_quakes():
    # เมนช็อก + อาฟเตอร์ช็อก ใกล้กันมาก แต่ JMA วัดชินโดะมาลูกเดียว — ต้องไม่เอาค่าเดียวไปติดทั้งสอง
    usgs = {"features": [
        {"id": "a", "properties": {"mag": 6.0, "place": "Noto A", "time": NOW - 10 * 60000, "tsunami": 0},
         "geometry": {"coordinates": [137.0, 37.3, 10]}},
        {"id": "b", "properties": {"mag": 5.7, "place": "Noto B", "time": NOW - 10 * 60000, "tsunami": 0},
         "geometry": {"coordinates": [137.02, 37.31, 10]}}]}
    jma = [{"eid": "J1", "at": _jst(10), "en_anm": "Noto", "cod": "+37.30+137.00-10000/", "mag": "5.9", "maxi": "5+"}]
    r = quakes.recent(get=lambda url: jma if "jma" in url else usgs, now_ms=NOW, jma=True)
    with_shindo = [q for q in r["world"] + r["near"] if q.get("shindo")]
    assert len(with_shindo) == 1 and with_shindo[0]["shindo"] == "5+"
