"""หน้าดูดาว (static/sky.html + static/sky_view.js) — ตำแหน่งต้องตรงกับฟ้าจริง

ค่าอ้างอิงคำนวณด้วย astropy 8 (ephemeris ในตัว · แสงหักเหที่ 1013 hPa 20°C) สำหรับ
2026-11-05 16:00 UTC ที่กรุงเทพฯ แล้วฝังไว้ในเทสต์ — ไม่ต้องใช้เน็ตหรือ astropy ตอนรัน
รันโค้ดจริงของหน้าใน node โดยจำลอง DOM เท่าที่จำเป็น (ไม่มี node = ข้าม)
"""
import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "static" / "sky_view.js"
HTML = (ROOT / "static" / "sky.html").read_text(encoding="utf-8")
WHEN = "2026-11-05T16:00:00Z"
REF = {"Sirius": [0, 109.764, 8.926], "Polaris": [46, 0.239, 14.394], "Betelgeuse": [9, 88.643, 27.193],
       "Vega": [4, 311.362, -3.202], "Canopus": [1, 145.109, 0.457],
       "sun": [260.196, -74.975], "moon": [69.231, -62.668], "mer": [262.434, -77.366], "ven": [78.444, -85.711],
       "mar": [65.839, -22.126], "jup": [66.639, -26.115], "sat": [232.861, 69.69], "ura": [73.3, 53.912], "nep": [239.812, 63.12]}

HARNESS = r"""
const fs = require('fs');
const noop = () => {}, ctx = new Proxy({}, { get: (t, k) => k === 'measureText' ? () => ({ width: 10 }) :
  (k === 'createLinearGradient' || k === 'createRadialGradient') ? () => ({ addColorStop: noop }) : noop, set: () => true });
const el = () => ({ getContext: () => ctx, addEventListener: noop, classList: { add: noop, remove: noop, toggle: noop, contains: () => true },
  style: {}, setAttribute: noop, removeAttribute: noop, appendChild: noop, clientWidth: 800, clientHeight: 600, textContent: '',
  getBoundingClientRect: () => ({ left: 0, top: 0 }), setPointerCapture: noop });
global.document = { getElementById: el, documentElement: { lang: 'th', classList: el().classList }, querySelectorAll: () => [],
  addEventListener: noop, hidden: true, createElement: el };
global.window = global; global.addEventListener = noop; global.location = { search: '' }; global.localStorage = { getItem: () => null, setItem: noop };
global.requestAnimationFrame = () => 1; global.setInterval = noop; global.navigator = {};
global.fetch = () => new Promise(noop);
eval(fs.readFileSync(process.argv[2], 'utf8'));
const T = KD_sky._test, cat = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
T.load(cat); T.setLoc({ lat: 13.7563, lon: 100.5018 }); T.at(Date.parse(process.argv[4]));
const out = { bodies: T.bodies(), stars: {} };
JSON.parse(process.argv[5]).forEach(i => { out.stars[i] = T.starAltAz(i); });
console.log(JSON.stringify(out));
"""


def _sep(a1, h1, a2, h2):
    a1, h1, a2, h2 = map(math.radians, (a1, h1, a2, h2))
    c = math.sin(h1) * math.sin(h2) + math.cos(h1) * math.cos(h2) * math.cos(a1 - a2)
    return math.degrees(math.acos(max(-1, min(1, c)))) * 60     # ลิปดา


@pytest.fixture(scope="module")
def sky(tmp_path_factory):
    if not shutil.which("node"):
        pytest.skip("ไม่มี node")
    h = tmp_path_factory.mktemp("sky") / "h.js"
    h.write_text(HARNESS)
    idx = [v[0] for k, v in REF.items() if len(v) == 3]
    out = subprocess.check_output(["node", str(h), str(JS), str(ROOT / "static" / "sky" / "catalog.json"), WHEN, json.dumps(idx)], timeout=60)
    return json.loads(out)


def _tol(alt):
    return 6 if alt > 1 else 20          # ใต้ขอบฟ้า แบบจำลองแสงหักเหของแต่ละโปรแกรมต่างกัน


@pytest.mark.parametrize("name", ["Sirius", "Polaris", "Betelgeuse", "Vega", "Canopus"])
def test_star_positions_match_real_sky(sky, name):
    i, az, alt = REF[name]
    jaz, jalt = sky["stars"][str(i)]
    assert _sep(jaz, jalt, az, alt) < _tol(alt), (name, jaz, jalt, az, alt)


@pytest.mark.parametrize("body", ["sun", "moon", "mer", "ven", "mar", "jup", "sat", "ura", "nep"])
def test_planet_moon_sun_positions(sky, body):
    az, alt = REF[body]
    got = {b["id"]: b["altaz"] for b in sky["bodies"]}[body]
    tol = 10 if body == "moon" else _tol(alt)
    assert _sep(got[0], got[1], az, alt) < tol, (body, got, az, alt)


def test_catalog_complete_and_attributed():
    cat = json.loads((ROOT / "static" / "sky" / "catalog.json").read_text(encoding="utf-8"))
    assert len(cat["stars"]) > 5000 and len(cat["lines"]) >= 88
    assert "d3-celestial" in cat["source"] and "d3-celestial" in HTML and "BSD-3" in HTML
    th = {c["id"]: c["th"] for c in cat["cons"]}
    assert th["Ori"] == "นายพราน" and th["Peg"] == "ม้าบิน" and th["Aur"] == "สารถี"


def test_tools_live_in_layers_sheet():
    for label in ("กลุ่มดาว", "ป้ายชื่อ", "ชี้มือถือขึ้นฟ้า", "ตำแหน่งของฉัน", "ภัยพิบัติ", "บิ๊กแบง", "คู่มือเอาชีวิตรอด"):
        assert label in HTML, label
    assert 'id="sky-layers"' in HTML and 'aria-controls="sky-sheet"' in HTML


def test_location_only_on_user_tap_and_never_sent():
    src = JS.read_text(encoding="utf-8")
    i = src.index("getCurrentPosition")
    assert src.rfind("$('sky-here').addEventListener('click'", 0, i) > 0      # ขอตำแหน่งเมื่อกดเท่านั้น
    # ทุก fetch อ่านแค่ไฟล์ข้อมูลดาวของเราเอง (catalog / milkyway / deep) — ไม่มีการส่งตำแหน่งออกไปไหน
    import re as _re
    calls = _re.findall(r"fetch\(([^)]*)\)", src)
    assert calls and all("'/static/sky/" in c for c in calls), calls
    assert "loc.lat" not in "".join(calls) and "store('kd-sky-loc'" in src


def test_full_circle_arc_for_ground():
    # arc(0, 6.283, true) ทวนเข็มได้แค่เสี้ยวเดียว → พื้นทับทั้งจอ (บั๊กที่เคยเจอ)
    assert "6.283, true" not in JS.read_text(encoding="utf-8")



def test_globe_link_opens_sky_above_viewed_spot():
    earth = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
    assert "a.href = '/sky?lat=' + la.toFixed(2) + '&lon=' + lo.toFixed(2)" in earth
    src = JS.read_text(encoding="utf-8")
    assert "q.get('lat')" in src and "away: true" in src
    i = src.index("away: true")
    assert "store('kd-sky-loc'" not in src[i - 400:i + 200]          # ตำแหน่งจากลูกโลกใช้รอบเดียว ไม่จำทับของผู้ใช้


def test_deep_stars_and_real_milky_way_files():
    deep = json.loads((ROOT / "static" / "sky" / "deep.json").read_text(encoding="utf-8"))
    mw = json.loads((ROOT / "static" / "sky" / "milkyway.json").read_text(encoding="utf-8"))
    n = len(deep["stars"]) // 4
    assert 30000 < n < 40000 and deep["stars"][2] >= 60                 # จางกว่าโชติมาตร 6 (6.01 ปัดเป็น 60)
    mags = deep["stars"][2::4]
    assert mags == sorted(mags) and max(mags) <= 80                     # เรียงสว่าง→จาง ถึง 8
    assert len(mw["levels"]) == 5 and all(mw["levels"])
    assert "d3-celestial" in deep["source"] and "d3-celestial" in mw["source"]


def test_aim_button_is_on_the_bar():
    i = HTML.index('id="sky-aim"')
    assert 'class="bar-btn"' in HTML[i - 10:i + 80] and HTML.index('id="sky-sheet"') > i


def test_my_decision_constellation_is_local_and_textless():
    app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    i = app.index("window.addEventListener('KD:response'")
    rec = app[i:app.index("\n});", i)]
    assert "localStorage.setItem('kd-my-stars'" in rec and "slice(-300)" in rec
    assert "fetch(" not in rec and "text" not in rec.lower().replace("textcontent", "")   # ไม่เก็บข้อความ ไม่ส่งไปไหน
    src = JS.read_text(encoding="utf-8")
    assert "store('kd-my-stars')" in src and "function drawMine" in src and "if (LAY.mine) drawMine(labels);" in src
    assert 'data-layer="mine"' in HTML and 'id="sky-mine-n"' in HTML


def test_sky_and_universe_are_findable(app_module):
    from fastapi.testclient import TestClient
    c = TestClient(app_module.app)
    sm = c.get("/sitemap.xml").text
    assert "/sky</loc>" in sm and "/universe</loc>" in sm
    r = c.get("/sky", follow_redirects=False)
    assert r.status_code == 200 and 'rel="canonical" href="https://king-diadem.onrender.com/sky"' in r.text   # URL สั้นเป็นหน้าหลัก ไม่ redirect
    u = c.get("/universe")
    assert u.status_code == 200 and 'rel="canonical" href="https://king-diadem.onrender.com/universe"' in u.text and 'name="description"' in u.text
    assert '"@type":"WebApplication"' in r.text


def test_waterline_horizon_follows_latest_topic():
    src = JS.read_text(encoding="utf-8")
    i = src.index("function waterline()")
    body = src[i:src.index("\n  }\n", i)]
    assert "(m.k - 30) / 70" in body and "Math.exp(-Math.max(0, age) / 3)" in body     # หนักขึ้น = สูงขึ้น · ลดเองใน ~3 วัน
    assert "return WL + Math.max(0," in src and "function behindHill(l)" in src
    for use in ("if (behindHill(l)) continue;", "behindHill(q.l)", "b.id !== 'sun' && behindHill(l)"):
        assert use in src, use                                                      # ของที่อยู่หลังขอบฟ้าที่ยกขึ้นถูกซ่อนทั้งดาวและชื่อ
    assert 'id="sky-wl"' in HTML


def test_stars_drawn_as_light_sprites_with_atmosphere():
    src = JS.read_text(encoding="utf-8")
    assert "function starSprite(bv)" in src and "cx.drawImage(spr," in src               # แกนขาว + ฟุ้งเป็นสีดาว ประทับซ้ำ (เร็ว)
    assert "X = 1 / (sh + .025 * Math.exp(-11 * sh))" in src                            # airmass: ใกล้ขอบฟ้าจางและอมแดง
    i = src.index("    // ดาว\n"); j = src.index("cx.restore(); cx.globalAlpha = 1;", i)
    assert "globalCompositeOperation = 'lighter'" in src[i:i + 120] and j > i             # แสงบวกกันแบบแสงจริง แล้วคืนค่า
