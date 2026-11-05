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
    assert "fetch(" in src and src.count("fetch(") == 1                        # fetch เดียวคือแค็ตตาล็อก


def test_full_circle_arc_for_ground():
    # arc(0, 6.283, true) ทวนเข็มได้แค่เสี้ยวเดียว → พื้นทับทั้งจอ (บั๊กที่เคยเจอ)
    assert "6.283, true" not in JS.read_text(encoding="utf-8")
