"""ภัยจริงบนลูกโลกหน้าจักรวาล (cockpit_earth.js) และแผนที่เมือง (city_map.js)

จุดภัยต้องฉายด้วยสมการเดียวกับชื่อเมือง (toScreen) จึงอยู่ตรงพิกัดจริงทุกระดับซูม
กล่องรายละเอียดสร้างด้วย DOM (ไม่ต่อ HTML จากข้อมูลภายนอก) และลิงก์ออกไปได้เฉพาะแหล่งทางการ
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EARTH = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
CITY = (ROOT / "static" / "city_map.js").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")


def _fn(src, name):
    i = src.index("function " + name)
    j = src.index("\n  }\n", i)
    return src[i:j]


def test_markers_use_same_projection_as_city_labels():
    draw = _fn(EARTH, "drawHazards")
    assert "toScreen(V, h.w)" in draw
    # เวกเตอร์โลกต้องเป็นสูตรเดียวกับชื่อเมือง: [cos(la)·sin(lo), sin(la), cos(la)·cos(lo)]
    assert "x.w = [Math.cos(la) * Math.sin(lo), Math.sin(la), Math.cos(la) * Math.cos(lo)]" in EARTH


def test_markers_drawn_at_every_zoom_before_city_label_gate():
    lab = _fn(EARTH, "labels")
    assert lab.index("drawHazards(") < lab.index("if (show <= 0) return")


def test_card_built_with_dom_and_official_links_only():
    i = EARTH.index("window.KD_hazardCard")
    card = EARTH[i:EARTH.index("\n  };\n", i)]
    assert "innerHTML" not in card
    assert r"/^https:\/\/(?:earthquake\.usgs\.gov|www\.gdacs\.org)\//" in card
    for key in ("quake", "storm", "flood", "volcano", "wildfire", "drought"):
        assert "'" + key + "'" in EARTH


def test_survival_anchors_exist():
    from core.survival_guide import HAZARDS
    for key in re.findall(r"\[\s*'#[0-9a-f]{6}',\s*'(\w+)'\s*\]", EARTH):
        assert key in HAZARDS, key


def test_tap_shows_and_drag_hides():
    assert "hazardAt(e.clientX - rr.left, e.clientY - rr.top)" in EARTH
    assert "if (gest.moved > 8) hideHazard();" in EARTH


def test_city_map_layer_readded_after_style_change():
    assert "map.on('style.load', addHazards);" in CITY
    assert "window.addEventListener('kd-hazards', addHazards);" in CITY
    assert "setDOMContent(" in CITY and "setHTML(" not in CITY


def test_popup_style_present():
    assert ".cockpit .hz-pop{" in PAGE and ".cockpit .hz-pop.hide{display:none}" in PAGE


def test_hazard_card_offers_ask_lyla_prefill_not_autosend():
    app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "/?ask=' + encodeURIComponent(" in EARTH and "/?ask=' + encodeURIComponent(" in app
    i = app.index("if(qs.get('ask'))")
    block = app[i:i + 300]
    assert "inp0.value" in block and "send" not in block.lower()          # เติมข้อความให้ ผู้ใช้กดส่งเอง


def test_prefilled_hazard_messages_reach_survival_steps():
    from core.kernel_voice import assess
    for t, kind in (("ฉันอยู่ใกล้แผ่นดินไหว M6.1 · Fiji region ตอนนี้ต้องทำอะไรก่อน", "quake"),
                    ("ฉันอยู่ใกล้ไฟป่า Forest fires in Indonesia ตอนนี้ต้องทำอะไรก่อน", "fire"),
                    ("I am near the typhoon (IN-FA-26) — what should I do first?", "storm"),
                    ("I am near the flood (Flood Thailand) — what should I do first?", "flood")):
        assert (assess(t).get("disaster") or {}).get("kind") == kind, t
