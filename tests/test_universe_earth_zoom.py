"""หน้า Universe — กล้องมีมิติ ซูมลื่น ป้ายชื่อเรียงตามความสำคัญ (จังหวัดไทยชื่อไทย) หัวเรื่องหายเมื่อซูมลง
เดิม: ซูมเป็นภาพแบนขยาย · ไม่มีถ่างนิ้ว/ล้อเมาส์ · "อ่างทอง" ไม่ขึ้นเพราะแพ้ป้าย "โพธิ์ทอง" · หัวเรื่องจางเหลือ 6% ทับชื่อเมือง"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")
EARTH = ROOT / "static" / "earth"


def _load(f):
    return json.loads((EARTH / f).read_text(encoding="utf-8"))


def test_every_thai_province_has_a_thai_label():
    th = [r for r in _load("admin1.json") if len(r) > 3]
    assert len(th) == 76                                              # 76 จังหวัด (กรุงเทพฯ อยู่ในเมืองหลวง)
    names = {r[3] for r in th}
    assert {"อ่างทอง", "เชียงใหม่", "นครราชสีมา", "พระนครศรีอยุธยา", "ยโสธร"} <= names
    ang = next(r for r in th if r[3] == "อ่างทอง")
    assert abs(ang[1] - 14.59) < .05 and abs(ang[2] - 100.45) < .05
    bkk = next(c for c in _load("capitals.json")["capitals"] if c[0] == "Bangkok")
    assert bkk[5] == "กรุงเทพมหานคร" and abs(bkk[2] - 13.75) < .05


def test_province_tier_is_drawn_before_small_towns():
    """ชั้นศูนย์กลางจังหวัดต้องได้ที่ก่อนเมืองเล็ก — ชนกันแล้วเมืองเล็กหลีกทาง"""
    order = [JS.index(f"'{f}'") for f in ("capitals.json", "admin1.json", "cities_t2.json", "cities_t5.json")]
    assert order == sorted(order)
    admin = {r[0] for r in _load("admin1.json")}
    for t in range(2, 6):
        assert not admin & {r[0] for r in _load(f"cities_t{t}.json") if r[0] in ("Ang Thong", "Chiang Mai")}


def test_city_tiers_are_sorted_big_to_small():
    from scripts.build_earth_cities import BANDS
    assert [b[0] for b in BANDS] == [2, 3, 4, 5]
    assert "pop" in (ROOT / "scripts" / "build_earth_cities.py").read_text(encoding="utf-8")


def test_perspective_camera_and_gestures():
    assert "perspective" in JS and "tilt" in JS and "uniform float t,ready,lon,lat,D,tilt,F" in JS
    assert "'wheel'" in JS and "passive: false" in JS                  # ล้อเมาส์/ถ่างทัชแพดซูมได้
    assert "pinch" in JS and "d0" in JS                                # ถ่างนิ้วสองนิ้ว
    assert "vlon" in JS and "Math.exp(-dt * 3.2)" in JS                # ปล่อยนิ้วแล้วไหลต่อ
    assert "ArrowLeft" in JS and "tabIndex = 0" in JS                  # คีย์บอร์ดใช้ได้
    assert "touchAction = S.tL > 1.02 ? 'none' : 'pan-y'" in JS       # ซูมแล้วเป็นแผนที่เต็มตัว · ไม่ซูมยังเลื่อนหน้าได้


def test_smooth_on_phones():
    assert "generateMipmap" in JS                                      # ภาพทั้งโลกไม่ระยิบ
    assert "ftAvg > 26" in JS and "size();" in JS                       # เฟรมช้า → ลดความละเอียดการวาด
    assert "if(wm>.01){" in JS                                         # คลื่นทะเลคำนวณเฉพาะจุดน้ำ
    assert "key === lastKey && !labelsDirty" in JS                     # กล้องนิ่ง = ไม่วาดชื่อใหม่


def test_title_disappears_when_zoomed_in():
    assert "opacity:var(--hero-a,1)" in PAGE and "opacity:.06" not in PAGE
    assert "--hero-a" in JS and "1 - smooth((S.L - 1.08) / .55)" in JS


def test_calm_mode_still_respected():
    assert "prefers-reduced-motion" in JS and "function settle()" in JS and "if (calm()) {" in JS
