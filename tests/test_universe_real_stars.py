"""ดาวจริงบนฟ้าหน้าจักรวาล (universe_sky.js) — ต้องอยู่ถูกฝั่งของทางช้างเผือกที่ shader วาด"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "static" / "universe_sky.js").read_text(encoding="utf-8")
ASTRO = (ROOT / "static" / "sky_astro.js").read_text(encoding="utf-8")


def _gal():
    rows = re.search(r"var GAL = (\[\[.*?\]\]);", SRC).group(1)
    return json.loads(re.sub(r"(^|[\[,\s-])\.", r"\g<1>0.", rows))   # .05 → 0.05


def _eq(ra, dec):
    a, d = math.radians(ra), math.radians(dec)
    return [math.cos(d) * math.cos(a), math.cos(d) * math.sin(a), math.sin(d)]


def test_galactic_center_and_pole_land_where_shader_draws_them():
    G = _gal()
    g = [sum(G[i][k] * v for k, v in enumerate(_eq(266.405, -28.936))) for i in range(3)]
    assert g[0] > .9999                                   # ใจกลางกาแล็กซี → แกน uG ของ shader
    p = [sum(G[i][k] * v for k, v in enumerate(_eq(192.859, 27.128))) for i in range(3)]
    assert p[2] > .9999                                   # ขั้วเหนือกาแล็กซี → แกน uN


def test_drawn_in_same_frame_as_shader_and_redone_on_rotate():
    i = SRC.index("gl.drawArrays(gl.TRIANGLES, 0, 3);")
    assert "drawRealSky(cam.yaw, pitch, f);" in SRC[i:i + 120]
    assert "if (RS.gn !== GN)" in SRC


def test_popup_built_from_text_nodes_only():
    i = SRC.index("function showRealStar")
    body = SRC[i:SRC.index("\n  }\n", i)]
    assert "innerHTML" not in body and "textContent" in body


def test_named_star_facts_present():
    cat = json.loads((ROOT / "static" / "sky" / "catalog.json").read_text(encoding="utf-8"))
    facts = {n[1]: n for n in cat["named"] if len(n) > 3}
    assert facts["Vega"][3] == 25 and facts["Aldebaran"][3] == 65 and facts["Sirius"][3] == 8.6
    assert cat["planets"]["jup"]["kind"] == "ดาวแก๊สยักษ์" and cat["planets"]["nep"]["kind"] == "ดาวน้ำแข็งยักษ์"


def test_astro_module_matches_sky_page_formula():
    # สูตรเคปเลอร์ของหน้าจักรวาลต้องเป็นชุดเดียวกับหน้าดูดาว (ซึ่งเทียบ astropy แล้วใน test_sky_view.py)
    sky = (ROOT / "static" / "sky_view.js").read_text(encoding="utf-8")
    for frag in ("el.a + el.da * t", "E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E))", "a * Math.sqrt(1 - e * e) * Math.sin(E)"):
        assert frag in ASTRO and frag in sky
