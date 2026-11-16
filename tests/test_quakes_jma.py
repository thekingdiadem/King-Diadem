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
