"""ภัยพิบัติจริงทั่วโลก (core/hazards.py · GDACS) — เดิมระบบรู้ข้อมูลจริงแค่แผ่นดินไหว (USGS)
เจ้าของโปรเจกต์: "แผ่นดินไหวนี่ทั่วโลกเลยมะ เอาอย่างอื่นด้วยได้ไหม ทุกภัยพิบัติ เพราะโลกสุดขั้วแล้วตอนนี้" """
import pytest

from core import hazards as hz


def _f(kind, eid, level, lon, lat, name="", country="", geom="Point", current="true", sev=""):
    return {"type": "Feature", "geometry": {"type": geom, "coordinates": [lon, lat]},
            "properties": {"eventtype": kind, "eventid": eid, "alertlevel": level, "eventname": name, "country": country,
                           "iscurrent": current, "severitydata": {"severitytext": sev},
                           "url": {"report": f"https://www.gdacs.org/report.aspx?eventid={eid}"}}}


GEO = {"type": "FeatureCollection", "features": [
    _f("TC", 1, "Orange", 115.0, 15.0, "YAGI-24", "Philippines, Viet Nam", sev="Tropical Storm (maximum wind speed of 120 km/h)"),
    _f("TC", 1, "Orange", 115.0, 15.0, geom="Polygon"),                          # รูปร่างของเหตุการณ์เดียวกัน — ข้าม
    _f("FL", 2, "Green", 100.6, 14.0, "Flood in Thailand", "Thailand"),           # ใกล้: ระดับเขียวก็แสดง
    _f("VO", 3, "Red", 110.4, -7.5, "Merapi", "Indonesia"),
    _f("WF", 4, "Green", -120.0, 38.0, "Wildfire", "United States"),              # ไกล + เขียว: ไม่แสดง
    _f("DR", 5, "Red", 30.0, 15.0, "Drought", "Sudan"),                           # ไกล + แดง: แสดง
    _f("EQ", 6, "Red", 96.0, 22.0, "Earthquake", "Myanmar"),                      # แผ่นดินไหวใช้ USGS — ข้าม
    _f("FL", 7, "Orange", 101.0, 13.0, current="false"),                           # จบแล้ว — ข้าม
    _f("TC", 8, "Purple", 101.0, 13.0),                                            # ระดับไม่รู้จัก — ข้าม
    {"type": "Feature", "geometry": None, "properties": {"eventtype": "FL"}},      # ข้อมูลเสีย — ข้าม ไม่ล่ม
]}


@pytest.fixture(autouse=True)
def fresh_cache():
    hz._cache.update(at=0.0, ok=False, items=[])
    yield
    hz._cache.update(at=0.0, ok=False, items=[])


def test_parse_keeps_one_point_per_current_event_and_skips_bad_rows():
    rows = hz.parse(GEO)
    assert [r["id"] for r in rows] == ["TC1", "FL2", "VO3", "WF4", "DR5"]
    assert rows[0]["level"] == "orange" and "120 km/h" in rows[0]["severity"] and rows[0]["url"].startswith("https://www.gdacs.org/")


def test_near_thailand_every_level_far_away_only_orange_and_red():
    r = hz.recent(get=lambda url: GEO)
    assert r["ok"] and r["source"] == "GDACS"
    assert [x["id"] for x in r["near"]] == ["TC1", "FL2"] and r["near"][1]["km"] < 100
    assert [x["id"] for x in r["world"]] == ["VO3", "DR5"]                        # แดงก่อน · WF เขียวไกล ไม่แสดง


def test_filter_by_kind():
    assert [x["id"] for x in hz.recent(["TC"], get=lambda url: GEO)["near"]] == ["TC1"]


def test_feed_down_means_say_so_never_guess():
    def down(url):
        raise TimeoutError("gdacs slow")
    r = hz.recent(get=down)
    assert r["ok"] is False and r["near"] == [] and "ห้ามเดา" in hz.llm_note(r)


def test_one_failure_keeps_the_last_good_data():
    hz.recent(get=lambda url: GEO)
    hz._cache["at"] -= hz.TTL + 1                                                  # แคชหมดอายุ แล้วรอบใหม่ล้ม
    r = hz.recent(get=lambda url: (_ for _ in ()).throw(ConnectionError()))
    assert r["ok"] and r["near"]


def test_llm_note_uses_only_real_numbers():
    note = hz.llm_note(hz.recent(get=lambda url: GEO))
    assert "GDACS" in note and "YAGI-24" in note and "ห้ามเพิ่มตัวเลขอื่น" in note
    hz._cache.update(at=0.0)
    empty = hz.llm_note(hz.recent(get=lambda url: {"features": []}))
    assert "ไม่มีประกาศ" in empty


def test_chat_attaches_live_data_when_asked_or_in_a_storm(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    monkeypatch.setattr(hz, "_http_get", lambda url: GEO)
    d = client.post("/run", json={"input": "ตอนนี้มีพายุเข้าไทยไหม"}).json()
    assert d["hazards"]["ok"] and d["hazards"]["near"][0]["id"] == "TC1" and d.get("survival") == "storm"
    assert "hazards" not in client.post("/run", json={"input": "วันนี้กินข้าวอะไรดี"}).json()


def test_public_api(client, monkeypatch):
    monkeypatch.setattr(hz, "_http_get", lambda url: GEO)
    d = client.get("/api/hazards").json()
    assert d["ok"] and {x["kind"] for x in d["near"] + d["world"]} == {"TC", "FL", "VO", "DR"}


def test_card_only_links_to_gdacs():
    from tests._front import front_page
    page = front_page()
    assert "function hazardCard(r)" in page and "hz: d.hazards" in page and r"/^https:\/\/www\.gdacs\.org\//" in page
