"""โหมดยานอวกาศหน้า /universe — ยานโคจรแบบสถานีอวกาศนานาชาติ มองโลกผ่านหน้าต่างห้องโดยสาร

พี่คิงขอ "โหมดยานอวกาศบินรอบโลก เหมือนของจริงทุกอย่าง คมชัด" ไว้ให้สาวๆ ที่ฝันอยากเห็นโลกจากมุมนักบินอวกาศ
· คณิตศาสตร์วงโคจรอยู่ใน static/ship_orbit.js (รันจริงใน node — ไม่มี node = ข้ามเฉพาะส่วนนั้น)
· ตัวเลขบนการ์ดหน้าต่างต้องตรงกับฟิสิกส์ที่ตรวจได้ (ไม่ใช่ตัวเลขสวยๆ ที่แต่งขึ้น)
· เฟรมเรต 30/60/90/120/144 ที่เลือกไว้ ใช้กับโลกและท้องฟ้าหน้านี้ด้วย
"""
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ORBIT_JS = ROOT / "static" / "ship_orbit.js"
ORBIT = ORBIT_JS.read_text(encoding="utf-8")
EARTH = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
SKY = (ROOT / "static" / "universe_sky.js").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")

R_KM, MU = 6371.0, 398600.4418          # รัศมีโลกเฉลี่ย · ค่าคงที่ความโน้มถ่วงของโลก (กม.³/วินาที²)

# รันโค้ดจริงของ ship_orbit.js แล้วส่งค่าที่ต้องตรวจกลับมาเป็น JSON
_PROBE = r"""
global.window = global; require(process.argv[2]); const O = global.KD_orbit;
const geo = (V) => {
  const st = Math.sin(V.tilt), ct = Math.cos(V.tilt), P = [0, -V.D * st, 1 + V.D * ct], r = Math.hypot(P[0], P[1], P[2]);
  const fw = [0, st, -ct], eta = Math.acos(-(P[1] * fw[1] + P[2] * fw[2]) / r);   // มุมระหว่างแนวดิ่งใต้ยานกับเส้นกลางจอ
  return { alt: (r - 1) * 6371, off: Math.atan2(V.D * st, 1 + V.D * ct) * 180 / Math.PI, ahead: V.ahead,
           above: (O.HORIZON - eta) * 180 / Math.PI };
};
let st = { u: 0.3, node: 40 }, lats = [], n = 2000;
for (let i = 0; i < n; i++) { st = O.step(st, O.PERIOD_S / n, 1); lats.push(O.ground(st.u, st.node).lat); }
const fast = O.step({ u: 0.3, node: 40 }, O.PERIOD_S / 60, 60);
const sun = {};
for (const t of ['2026-03-20T12:00:00Z', '2026-06-21T12:00:00Z', '2026-11-03T12:00:00Z', '2026-12-21T12:00:00Z']) sun[t] = O.sun(Date.parse(t));
const v = O.vec(13.75, 100.5);
console.log(JSON.stringify({ C: { ALT_KM: O.ALT_KM, INC_DEG: O.INC_DEG, PERIOD_S: O.PERIOD_S, SPEED_KMS: O.SPEED_KMS },
  wide: geo(O.VIEW), tall: geo(O.VIEW_TALL), latMax: Math.max(...lats), latMin: Math.min(...lats),
  back: { u: st.u, node: st.node }, fast: fast, sun: sun, vec: v }));
"""


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    if not shutil.which("node"):
        pytest.skip("ไม่มี node")
    f = tmp_path_factory.mktemp("ship") / "probe.js"
    f.write_text(_PROBE, encoding="utf-8")
    return json.loads(subprocess.check_output(["node", str(f), str(ORBIT_JS)], timeout=60))


def test_camera_really_sits_at_iss_altitude(probe):
    """เดิมกล้องอยู่สูงแค่ราว 124 กม. ทั้งที่ HUD ขึ้น 408 กม. (เอาระยะมองเฉียงไปใส่แทนความสูง)
    ตอนนี้แก้สามเหลี่ยมศูนย์กลางโลก–กล้อง–จุดที่มอง ให้กล้องอยู่ 408 กม. ตรงเหนือจุดใต้ยานพอดี"""
    for v in (probe["wide"], probe["tall"]):
        assert abs(v["alt"] - 408) < 0.5
        assert abs(v["off"] - v["ahead"]) < 1e-6                      # จุดกลางจออยู่เหนือจุดใต้ยานเท่าที่ frame() เลื่อนไปจริง
    assert abs(probe["wide"]["above"] - 5) < 1e-6 and abs(probe["tall"]["above"] - 10) < 1e-6   # ขอบฟ้าอยู่เหนือกลางจอ ไม่ตกขอบ


def test_orbit_matches_real_physics(probe):
    """คาบ ความเร็ว และความสูงต้องเข้ากันตามกฎของเคปเลอร์ — ไม่ใช่ตัวเลขที่เลือกมาแยกกัน"""
    C = probe["C"]
    a = R_KM + C["ALT_KM"]
    kepler = 2 * math.pi * math.sqrt(a ** 3 / MU)
    assert abs(kepler - C["PERIOD_S"]) / C["PERIOD_S"] < 0.01
    assert abs(2 * math.pi * a / C["PERIOD_S"] - C["SPEED_KMS"]) / C["SPEED_KMS"] < 0.01
    assert 15 < 86400 / C["PERIOD_S"] < 16                            # "เห็นพระอาทิตย์ขึ้นราว 16 ครั้งต่อวัน"


def test_ground_track_stays_within_inclination(probe):
    inc = probe["C"]["INC_DEG"]
    assert abs(probe["latMax"] - inc) < 0.05 and abs(probe["latMin"] + inc) < 0.05
    # ครบหนึ่งรอบ ยานกลับมามุมเดิม แต่โลกหมุนไปทางตะวันออกใต้ยาน — จุดตัดเส้นศูนย์สูตรเลื่อนไปทางตะวันตกราว 23°
    assert abs(probe["back"]["u"] - 0.3) < 1e-6
    assert abs((40 - probe["back"]["node"]) - 360 * probe["C"]["PERIOD_S"] / 86164) < 1e-6
    # เร่ง ×60: เวลาจริง 1/60 รอบ = ยานไปครบหนึ่งรอบพอดี
    d = (probe["fast"]["u"] - 0.3 + math.pi) % (2 * math.pi) - math.pi
    assert abs(d) < 1e-6


@pytest.mark.parametrize("when,lat,lon", [
    ("2026-03-20T12:00:00Z", 0.0, 1.9),      # วสันตวิษุวัต · สมการเวลาราว −7.5 นาที → ดวงอาทิตย์ยังอยู่ตะวันออกของกรีนิช
    ("2026-06-21T12:00:00Z", 23.44, 0.4),    # ครีษมายัน
    ("2026-11-03T12:00:00Z", -15.1, -4.1),   # สมการเวลาสูงสุดราว +16.4 นาที
    ("2026-12-21T12:00:00Z", -23.44, -0.5),  # เหมายัน
])
def test_sun_position_matches_almanac(probe, when, lat, lon):
    """กลางวัน/กลางคืนในหน้าต่างยานใช้ดวงอาทิตย์จริง — ยานจึงผ่านพระอาทิตย์ขึ้นตรงกับเวลาจริง"""
    s = probe["sun"][when]
    assert abs(s["lat"] - lat) < 0.3 and abs(s["lon"] - lon) < 0.5, s


def test_vector_convention_matches_the_earth_shader(probe):
    """ทิศดวงอาทิตย์ส่งเข้า shader ต้องใช้แกนเดียวกับที่ shader อ่านละติจูด/ลองจิจูด (asin(n.y), atan(n.x, n.z))"""
    x, y, z = probe["vec"]
    assert abs(math.degrees(math.asin(y)) - 13.75) < 1e-9 and abs(math.degrees(math.atan2(x, z)) - 100.5) < 1e-9
    assert "float la=asin(clamp(n.y,-1.,1.)),lo=atan(n.x,n.z);" in EARTH


def test_window_cards_state_checkable_facts():
    """การ์ดบนหน้าต่าง: ตัวเลขต้องตรงกับค่าคงที่ของยานและฟิสิกส์ — ไม่ใช้ AI ไม่มีค่าโทเคน"""
    notes = PAGE[PAGE.index("var SHIP_NOTES = {"):PAGE.index("var shipNoteI")]
    th, en = notes[:notes.index("  en: [")], notes[notes.index("  en: ["):]
    assert th.count('["') == en.count('["') >= 8                        # สองภาษาเท่ากันทุกใบ
    alt = float(re.search(r"ALT_KM: (\d+)", ORBIT).group(1))
    period_min = 92.9
    speed = float(re.search(r"SPEED_KMS: ([\d.]+)", ORBIT).group(1))
    assert f"{alt:.0f} กม." in th and f"{alt:.0f} km" in en
    assert f"ราว {round(period_min)} นาที" in th and f"~{round(period_min)} minutes" in en
    assert f"{speed} กม./วินาที" in th and f"{speed} km per second" in en
    # ข้ามไทยเหนือจรดใต้ (~1,620 กม.) ด้วยความเร็วที่พื้น v·R/(R+h) ≈ 3.8 นาที → "ราว 4 นาที"
    assert round(1620 / (speed * R_KM / (R_KM + alt)) / 60) == 4 and "ราว 4 นาที" in th
    # แสงอาทิตย์: 1 AU ÷ ความเร็วแสง = 499 วินาที = 8 นาที 19 วินาที → "ราว 8 นาที 20 วินาที"
    assert abs(149_597_870.7 / 299_792.458 - (8 * 60 + 20)) < 2 and "8 นาที 20 วินาที" in th
    assert "Black Marble" in th and "Black Marble" in (ROOT / "static" / "earth" / "README.md").read_text(encoding="utf-8")
    assert "Frank White" in th and "Overview Effect" in en and "Choice(t) ≥ 1" in th


def test_ship_markup_and_controls():
    assert 'id="ec-ship"' in PAGE and 'data-act="ship"' in PAGE
    assert 'id="ship"' in PAGE and 'id="ship-hud"' in PAGE and 'id="ship-note" aria-live="polite"' in PAGE
    assert 'id="ship-fast" data-act="shipfast"' in PAGE
    assert PAGE.index("/static/ship_orbit.js") < PAGE.index("/static/cockpit_earth.js")   # คณิตวงโคจรต้องมาก่อนโลก
    assert "ship: function(){ KD_toggleShip(); }" in PAGE
    assert "e.key === 'Escape' && document.documentElement.classList.contains('kd-ship')" in PAGE   # Esc ออกจากยาน
    ship_tags = re.findall(r"<[^>]+\bship[^>]*>", PAGE)
    assert ship_tags and not [t for t in ship_tags if re.search(r"\son[a-z]+=", t)]   # CSP: ไม่มี onclick ในแท็ก


def test_ship_mode_engine_guards():
    # อยู่ในยาน: ถ่างนิ้ว/ล้อเมาส์ลึกไม่สลับไปแผนที่เมือง (ทั้งทาง go และ setL)
    assert "if (SHIP.on && o.L > LMAX) return;" in EARTH and "if (SHIP.on && L > LMAX) L = LMAX;" in EARTH
    # มือถือโหลดภาพ 4K เมื่ออยู่ในยานด้วย — หน้าต่างยานมองใกล้ ภาพ 2K เบลอ
    assert "(light && S.tL < 2 && !SHIP.on)" in EARTH
    # กดกลับเข้ายานระหว่างกำลังออก = โคจรต่อจากเดิม ไม่กระโดด
    assert "if (SHIP.k > 0) { SHIP.on = true; maybe4k(); shipRes(true); return true; }" in EARTH
    # ชื่อเมืองไม่บังวิวหน้าต่าง · ดวงอาทิตย์จริงเฉพาะในยาน (นอกยาน sunM = 0 → ภาพโลกเดิมทุกอย่าง)
    assert "if (SHIP.k > 0) { if (lab) lab.style.opacity = '0'; }" in EARTH
    assert "uniform vec3 sun;" in EARTH and "'sunM', 'near', 'sun'" in EARTH and "gl.uniform1f(U.sunM, OB ? 1 - dayM : 0); gl.uniform1f(U.near, near);" in EARTH
    for keep in ("mix(26.,130.,near)", "mix(150.,700.,near)", "mix(.45+.5*dayM,", "mix(.007,.0147,near)", "dl=max(dayM,"):
        assert keep in EARTH                                           # ค่าแรกของ mix = ค่าเดิม (นอกยาน near = 0)


@pytest.mark.parametrize("cap", [30, 60, 90, 120, 144])
def test_auto_resolution_does_not_punish_low_frame_rate_choice(cap):
    """เลือก 30 เฟรมเอง ภาพห่างกัน 33 ms — ตัวลดความละเอียดอัตโนมัติเคยนับว่า "เครื่องช้า" แล้วลดความคมชัดลงเรื่อยๆ"""
    assert "var slack = Math.max(0, 1000 / capNow - 16.7);" in EARTH
    assert "ftAvg > 26 + slack * 1.5" in EARTH and "ftAvg < 17 + slack" in EARTH
    slack = max(0, 1000 / cap - 16.7)
    interval = max(1000 / cap, 1000 / 144)                             # เครื่องที่ทันทุกเฟรมตามค่าที่เลือก
    assert not interval > 26 + slack * 1.5                             # ไม่ลดความคมชัด
    assert 45 > 26 + slack * 1.5 or cap == 30                          # เครื่องที่ช้าจริง (45 ms) ยังถูกลดเพื่อความลื่น
    assert 60 > 26 + slack * 1.5                                       # 60 ms ช้าจริงทุกค่า


def test_frame_rate_choice_reaches_universe_page():
    """เฟรมเรตที่เลือกในหน้าแชต (kd-fps) ใช้กับโลกและท้องฟ้าหน้า /universe — เดิมโลกวาดเต็มความเร็วจอ ท้องฟ้าล็อก 90"""
    assert "var FPS_OK = [30, 60, 90, 120, 144]" in EARTH and "localStorage.getItem('kd-fps')" in EARTH
    assert "capAcc + 1e-4 < 1 / capNow" in EARTH
    assert "[30, 60, 90, 120, 144].indexOf(v) >= 0 ? v : 90" in SKY and "acc + 1e-4 < 1 / cap" in SKY
    assert "1 / 90" not in SKY
    # ท้องฟ้าใช้เวลาจริงตั้งแต่ภาพก่อน (เดิมใช้ช่วงรอบจอ — ข้ามเฟรมแล้วฟ้าเคลื่อนช้ากว่าจริง)
    assert "(now - lastDraw) / 1000" in SKY and "dt > Math.max(1 / 40, 1.3 / cap)" in SKY
    # แถวเลือกเฟรมเรตในแผงเครื่องมือหน้านี้ → บอกโลกและท้องฟ้าทันทีด้วยเหตุการณ์ kd-fps
    assert 'id="ec-fps"' in PAGE and all(f'data-fps="{c}"' in PAGE for c in (30, 60, 90, 120, 144))
    assert "window.dispatchEvent(new Event('kd-fps'))" in PAGE
    assert "addEventListener('kd-fps'" in EARTH and "addEventListener('kd-fps'" in SKY
    # เครื่องเบาที่ผู้ใช้ไม่ได้เลือกเอง ยังวาด ~30 ตอนลอยเองเพื่อประหยัดแบต · เลือกเอง/อยู่ในยาน = ใช้ค่าที่เลือก
    assert "if (light && !busy && !SHIP.on && !capUser && last && now - last < 30)" in EARTH


def test_ship_looks_like_the_naked_eye_and_keeps_phones_cool():
    """พี่คิงขอ "สวยแบบของจริง เหมือนมองจากอวกาศจริงๆ" และเครื่องไม่ร้อน
    · airglow ในยานจางลง (ที่เห็นเข้มๆ ในภาพ NASA มักเป็นภาพเปิดหน้ากล้องนาน) · กลางคืนพื้นโลกมืด เหลือไฟเมืองเท่าเดิม
    · ในยานใครไม่ได้ตั้งเฟรมเรตเองวาดไม่เกิน 60 · ปรับมองใกล้ (near) มีผลเฉพาะในยาน"""
    assert "*mix(.5,.26,near)*(1.-ls)" in EARTH
    assert "*mix(1.,.42,sunM)+city*ready;" in EARTH
    assert "var capNow = SHIP.on && !capUser ? Math.min(cap, 60) : cap;" in EARTH      # ใครไม่ได้ตั้งเอง = 60
    assert "cl=mix(cl,smoothstep(.08,.85,cl),near*.55);" in EARTH                       # ขอบเมฆคมขึ้นเฉพาะในยาน
    assert "Math.min(window.devicePixelRatio || 1, 2)" in EARTH and "shipRes(false)" in EARTH   # ในยานวาดละเอียดเต็มจอ ออกแล้วกลับค่าเดิม


def test_ship_can_fly_over_thailand_and_shows_stars():
    """มองบ้านเรา: ปุ่ม "เหนือประเทศไทย" วางยานทางใต้ของกรุงเทพฯ เท่าระยะที่หน้าต่างมองไปข้างหน้า แล้วโคจรต่อตามจริง
    · ในยาน ห้องมืด ตาเห็นดาวชัดขึ้น (นอกยาน near = 0 ดาวเท่าเดิม)"""
    assert 'data-act="shiphome"' in PAGE and "shiphome: function(){ if(E() && E().shipOn()) E().shipHome(); }" in PAGE
    assert "SHIP.st = orbitOver(OB, 13.75 - VW.ahead, 100.5);" in EARTH and "function orbitOver(OB, lat, lon)" in EARTH
    assert "*(1.+1.3*near);}'" in EARTH


def test_decision_planets_are_tappable():
    """กลุ่มดาวแห่งการตัดสินใจ: แตะดาวแล้วส่งคำถามของดาวนั้นเข้าเครื่องจำลอง (แบบหน้า FATE แต่ใช้ชื่อของเรา)"""
    cards = re.findall(r'<button type="button" class="planet-card" data-try="([^"]+)">', PAGE)
    assert len(cards) == 6 and "เลือกไม่ถูกว่าจะเรียนต่อหรือทำงานดี" in cards
    assert "var t = e.target.closest('[data-try]'); if(t) tryText(t.dataset.try);" in PAGE


def test_window_is_empty_yet_not_empty():
    """พี่คิง: "ว่างไม่ว่างในเวลาเดียวกัน ดูสงบ" — ไม่เพิ่มข้อความ แต่ปล่อยหน้าต่างว่างให้โลก
    การ์ดอ่าน 8 วินาทีแล้วจาง · แผงและปุ่มจางเมื่อไม่มีใครแตะ 5 วินาที แตะ/ขยับแล้วกลับมา · ลดการเคลื่อนไหว = ไม่ซ่อนอะไรเอง"""
    assert "shipFadeT = setTimeout(function(){ box.classList.add('fade'); }, 8000);" in PAGE
    assert "h.classList.add('kd-ship-still'); }, 5000);" in PAGE
    assert "html.kd-ship-still .ship-ctl{pointer-events:none}" in PAGE
    assert "['pointermove', 'pointerdown', 'keydown', 'focusin']" in PAGE
    assert "!h.classList.contains('kd-calm')) shipIdleT" in PAGE
