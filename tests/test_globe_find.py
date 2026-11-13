"""ค้นหาเมืองบนลูกโลก Universe + เมฆที่เคยเป็นพิกเซลแตกตอนซูม (static/cockpit_earth.js · king_diadem_universe.html)"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
HTML = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")


def test_city_search_is_offline_and_bilingual():
    assert "find: function (q, cb)" in JS and "flyTo: function (lat, lon, tier)" in JS
    for f in ("capitals.json", "admin1.json", "places.json", "cities_t5.json"):
        assert f in JS                                   # ค้นในไฟล์ของเราเอง ไม่ส่งคำค้นไปบริการภายนอก
    assert "fetch(base + 'earth/'" in JS and "nominatim" not in JS.lower()


def test_search_button_is_small_until_tapped():
    assert 'id="ec-fbtn"' in HTML and '<input id="ec-fq" class="hide"' in HTML
    assert "addEventListener('click'" in HTML and 'onclick=' not in HTML.split('id="ec-find"')[1][:800]


def test_still_globe_gets_full_resolution_back():
    # เดิมลดเหลือ 55% ตอนหมุนแล้วไม่เคยคืน ภาพนิ่งจึงค้างเป็นสี่เหลี่ยมใหญ่
    assert "else if (scale < DPR_MAX && now - quietSince > 500) { scale = DPR_MAX; size(); }" in JS
    assert "Math.max(.8, scale * .82)" in JS and "Math.max(.55" not in JS


def test_cloud_edges_use_soft_wisps_not_sub_pixel_noise():
    assert "fbm(cc*vec2(1500.,750.))" not in JS and "float wisp=fbm(" in JS


def test_city_data_has_thai_names_for_provinces():
    import json
    rows = json.loads((ROOT / "static" / "earth" / "admin1.json").read_text(encoding="utf-8"))
    assert any(r[0] == "Chiang Mai" and r[3] == "เชียงใหม่" for r in rows)
