"""สถานที่ท่องเที่ยวจริงบนลูกโลก · ลิงก์ Google Maps · ทางหนีทีไล่

พี่คิงขอ: "รายละเอียดทั้งโลก สถานที่ท่องเที่ยว เชื่อม Google Maps" และ "ทางหนีทีไล่ เผื่อใครหนีคนร้าย"
· สถานที่มาจาก Wikidata (CC0) — มรดกโลกทุกแห่ง + ที่เที่ยวสำคัญในไทย (scripts/build_earth_places.py) ไม่แต่งเอง
· Google Maps ใช้ลิงก์ทางการ (Maps URLs) ไม่มีคีย์ ไม่มีค่าใช้จ่าย ไม่ดึงข้อมูลของ Google มาวางบนแผนที่เรา
· แผนที่เมืองไฮไลต์จุดที่ขอความช่วยเหลือได้ (OpenStreetMap) · คำตอบเมื่อถูกตามข้างนอกต่างจากเมื่อถูกบุกบ้าน
"""
import json
from pathlib import Path

from core.kernel_voice import compose

ROOT = Path(__file__).resolve().parent.parent
EARTH = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
CITY = (ROOT / "static" / "city_map.js").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")
PLACES = json.loads((ROOT / "static" / "earth" / "places.json").read_text(encoding="utf-8"))


def test_places_are_real_and_complete():
    rows = PLACES["places"]
    assert "Wikidata" in PLACES["source"] and len(rows) >= 1500
    assert all(len(r) == 8 and r[4] in (1, 2, 3) and -90 <= r[2] <= 90 and -180 <= r[3] <= 180 for r in rows)
    assert sum(r[7] for r in rows) >= 1100                                       # มรดกโลก UNESCO ทุกแห่งที่มีพิกัด
    gp = next(r for r in rows if r[0] == "Grand Palace")
    assert gp[1] == "พระบรมมหาราชวัง" and abs(gp[2] - 13.75) < .02 and abs(gp[3] - 100.49) < .02
    names = {r[0] for r in rows}
    assert {"Taj Mahal", "Historic Sanctuary of Machu Picchu"} <= names
    ay = [r for r in rows if abs(r[2] - 14.35) < .01 and abs(r[3] - 100.56) < .01]
    assert len(ay) == 1 and ay[0][1] and ay[0][7] == 1                        # อยุธยาจุดเดียว มีชื่อไทย เป็นมรดกโลก
    assert (ROOT / "static" / "earth" / "places.json").stat().st_size < 300_000     # โหลดเมื่อซูมลงเท่านั้น


def test_places_load_lazily_and_glow_softly():
    assert "if (S.tL < PL_AT[1] - .15) return;" in EARTH and "fetch(base + 'earth/places.json')" in EARTH
    assert "function glowSprite()" in EARTH and "if (plGlow) return plGlow;" in EARTH   # แสงวาดครั้งเดียว ไม่สร้าง gradient ทุกเฟรม
    assert "drawPlaces(V, Wc, Hc, boxes);" in EARTH


def test_place_card_is_safe_and_links_out_officially():
    card = EARTH[EARTH.index("function showPlace(m)"):EARTH.index("function labels()")]
    assert "innerHTML" not in card and "textContent" in card                     # ข้อมูลภายนอก ใส่ด้วย textContent เท่านั้น
    assert "https://www.google.com/maps/search/?api=1&query=" in EARTH and "key=" not in EARTH
    assert "'https://www.wikidata.org/wiki/' + P.q" in card and "rel = 'noopener'" in card
    assert 'id="ec-gmaps"' in PAGE and "a.href = gmaps(la, lo);" in EARTH        # ปุ่มในแผงเปิดจุดกลางจอ


def test_place_card_light_feel_respects_calm():
    assert "@keyframes pl-dawn" in PAGE and ".pl-pop.lit .pl-line{animation:pl-dawn" in PAGE
    assert "html.kd-calm .pl-pop .pl-line,html.kd-calm .pl-pop *{animation:none!important}" in PAGE


def test_city_map_shows_places_to_run_to():
    assert "'source-layer': 'poi'" in CITY
    for k in ("'police'", "'hospital'", "'fire_station'", "'convenience'", "'fuel'"):
        assert k in CITY
    assert "24 ชม" not in CITY                                                   # ไม่อ้างว่าเปิด 24 ชม. ถ้าข้อมูลไม่ได้บอก


def test_being_followed_outside_is_not_answered_like_a_break_in():
    out = compose("มีคนเดินตามมา กลัวมาก จะหนีไปไหนดี")
    first = out[out.index("1)"):].split("\n")[0]
    assert "อย่ากลับบ้าน" in first and "ล็อกตัวเองในห้อง" not in first
    home = compose("มีคนพยายามงัดประตูบ้าน")
    assert "ล็อกตัวเองในห้อง" in home[home.index("1)"):].split("\n")[0]
    en = compose("someone is following me at night")
    assert "Don't go home" in en[en.index("1)"):].split("\n")[0]


def test_places_and_city_names_can_be_hidden():
    """พี่คิง: "ทำปุ่มซ่อนด้วย เผื่อบางคนตาลาย" — ปุ่มสถานที่/ชื่อเมืองในแผงเครื่องมือ จำไว้ในเครื่อง"""
    assert 'id="ec-places" aria-pressed="true" data-act="places"' in PAGE and 'id="ec-names" aria-pressed="true" data-act="names"' in PAGE
    assert "places: function(){ KD_layer('places'); }, names: function(){ KD_layer('names'); }," in PAGE
    assert "if (!LAYER.places) return;" in EARTH
    assert "if (!LAYER.names) return;" in EARTH
    assert "localStorage.setItem(k === 'places' ? 'kd-places' : 'kd-names'" in EARTH
    assert "if (k === 'places' && !LAYER.places) hidePlace();" in EARTH
