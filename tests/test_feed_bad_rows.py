"""ข้อมูลเสียรายการเดียวในฟีดภัยพิบัติ ต้องไม่ทำให้ทั้งฟีดหาย (USGS · JMA · GDACS)
เดิม: แผ่นดินไหวที่ mag เป็นข้อความ หรือ feature เป็น null แค่รายการเดียว → exception หลุดทั้งก้อน
→ ระบบถือว่า "ดึงไม่ได้" แล้ว LYLA บอกคนที่กำลังตกใจว่าไม่มีข้อมูล ทั้งที่ในฟีดมีแผ่นดินไหวจริงอยู่
และค่า "nan" เคยหลุดเข้ามาจน AI จะพูดว่า "Mnan" """
import pytest

from core import hazards, quakes

GOOD_USGS = {"id": "g", "properties": {"mag": 6.1, "time": 1, "place": "Mandalay"}, "geometry": {"coordinates": [96.1, 21.9, 10]}}
BAD_USGS = [
    None, "text", 42,
    {"id": "b", "properties": {"mag": "abc", "time": 1}, "geometry": {"coordinates": [1, 2]}},
    {"id": "c", "properties": {"mag": 5, "time": "yesterday"}, "geometry": {"coordinates": [1, 2]}},
    {"id": "d", "properties": {"mag": 5, "time": 1}, "geometry": {"coordinates": ["a", "b"]}},
    {"id": "e", "properties": [], "geometry": {"coordinates": [1, 2]}},
    {"id": "n", "properties": {"mag": "nan", "time": 1}, "geometry": {"coordinates": [1, 2]}},
    {"id": "i", "properties": {"mag": 5, "time": 1}, "geometry": {"coordinates": ["inf", 2]}},
]


@pytest.mark.parametrize("bad", BAD_USGS, ids=repr)
def test_usgs_one_bad_row_keeps_the_rest(bad):
    rows = quakes.parse({"features": [GOOD_USGS, bad]})
    assert [r["place"] for r in rows] == ["Mandalay"]


GOOD_JMA = {"eid": "G", "at": "2026-11-17T01:45:00+09:00", "cod": "+24.3+125.2-30000/", "mag": "3.9", "maxi": "1"}
BAD_JMA = [
    None, "text",
    {"eid": "B", "at": "2026-11-17T01:45:00+09:00", "cod": 12345, "mag": "3"},
    {"eid": "C", "at": "not-a-date", "cod": "+1+2", "mag": "3"},
    {"eid": ["x"], "at": "2026-11-17T01:45:00+09:00", "cod": "+1+2", "mag": "3"},
    {"eid": "D", "at": None, "cod": "+1+2", "mag": "3"},
    {"eid": "E", "at": "2026-11-17T01:45:00+09:00", "cod": "+1+2", "mag": "nan"},
]


@pytest.mark.parametrize("bad", BAD_JMA, ids=repr)
def test_jma_one_bad_row_keeps_the_rest(bad):
    assert [r["id"] for r in quakes.parse_jma([GOOD_JMA, bad])] == ["jmaG"]


GOOD_GDACS = {"properties": {"eventtype": "TC", "alertlevel": "Red", "eventid": 1, "eventname": "KONG-REY"},
              "geometry": {"type": "Point", "coordinates": [121.0, 22.0]}}
BAD_GDACS = [
    None, "text",
    {"properties": "x", "geometry": []},
    {"properties": {"eventtype": "TC", "alertlevel": "Red", "eventid": 2}, "geometry": {"type": "Point", "coordinates": {"a": 1, "b": 2}}},
    {"properties": {"eventtype": "FL", "alertlevel": "Red", "eventid": 3}, "geometry": {"type": "Point", "coordinates": ["nan", 1]}},
]


@pytest.mark.parametrize("bad", BAD_GDACS, ids=repr)
def test_gdacs_one_bad_row_keeps_the_rest(bad):
    assert [h["name"] for h in hazards.parse({"features": [GOOD_GDACS, bad]})] == ["KONG-REY"]


def test_chat_still_gets_real_quake_when_feed_has_junk(client, monkeypatch):
    feed = {"features": [GOOD_USGS | {"properties": GOOD_USGS["properties"] | {"time": __import__("time").time() * 1000 - 60000}}, None,
                         {"id": "x", "properties": {"mag": "??"}, "geometry": {"coordinates": [0, 0]}}]}
    monkeypatch.setattr(quakes, "_cache", {"at": 0.0, "ok": False, "items": []})
    monkeypatch.setattr(quakes, "_jcache", {"at": 0.0, "ok": False, "items": []})
    monkeypatch.setattr(quakes, "_http_get", lambda url: [] if "jma" in url else feed)
    d = client.post("/run", json={"input": "เมื่อกี้แผ่นดินไหว ตึกสั่น"}, headers={"cf-connecting-ip": "203.0.113.50"}).json()
    assert d["quakes"]["ok"] and d["quakes"]["near"][0]["mag"] == 6.1
