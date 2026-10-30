"""ดาวลูกไก่ใกล้ๆ: แตะบนฟ้าหน้าแรก → บินเข้าไปเห็นทั้งกระจุก วาดสดด้วยการ์ดจอ ไม่ใช้ภาพถ่ายของใคร"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "static" / "pleiades_view.js").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


def test_loads_only_when_tapped():
    assert "pleiades_view.js" not in PAGE.split("<script>")[0]                 # ไม่โหลดตอนเปิดหน้า
    assert "sc.src = '/static/pleiades_view.js'" in PAGE
    assert "if(d && Math.hypot(e.clientX - d[0], e.clientY - d[1]) > 8) return;" in PAGE   # ปัดหมุนโลกไม่นับเป็นแตะ
    assert "SKY.hit = A > .5 ? { x: px + ox, y: py + oy, k: k } : null;" in PAGE


def test_bright_stars_are_real_positions():
    names = {"Alcyone", "Atlas", "Electra", "Maia", "Merope", "Taygeta", "Pleione", "Celaeno", "Asterope"}
    for n in names:
        assert f"['{n}'," in JS, n
    sky = json.loads((ROOT / "static" / "earth" / "sky_taurus.json").read_text(encoding="utf-8"))["stars"]
    # ชื่อดาวที่ป้ายใช้ต้องตรงกับดาวสว่างในแคตตาล็อกจริง (ห่างไม่เกิน 1 ลิปดา)
    for ra, dec in ((56.871, 24.105), (56.581, 23.948), (56.457, 24.368)):
        assert any(math.hypot((r[0] - ra) * math.cos(math.radians(dec)), r[1] - dec) < 1 / 60 and r[2] < 4.5 for r in sky)


def test_rendering_is_procedural_and_free():
    assert "gl.drawArrays(gl.POINTS, 0, stars.length);" in JS                # ดาวเป็น point sprite บวกแสงกัน
    assert "gl.blendFunc(gl.ONE, gl.ONE);" in JS
    assert "NGC 1435" in JS and "float silk=" in JS                           # หมอกสะท้อนแสงรอบ Merope เป็นเส้นใย
    assert "vSz=2.*core/sz;vSp=2.*spk/sz;" in JS                              # ขนาดแกนดาวเทียบครึ่งกว้าง sprite (บั๊กเดิมเล็กไปครึ่ง)
    assert ".jpg" not in JS and ".png" not in JS                              # ไม่มีภาพถ่าย


def test_feels_like_the_city_map():
    assert "dur: 2200" in JS and "1 - Math.pow(1 - k, 3)" in JS              # บินเข้าแบบชะลอตอนจบ
    assert "if (dpp > view.exit) { close(); return; }" in JS                  # ซูมออกพ้นจุดเริ่ม = กลับ (แบบแผนที่เมือง)
    assert "e.key === 'Escape'" in JS and "aria-label=\"กลับหน้าแรก\"" in JS
    assert "prefers-reduced-motion" in JS                                     # ลดการเคลื่อนไหว = ไปถึงทันที
    assert "#m45{position:fixed;inset:0;z-index:120;background:#020309" in PAGE


def test_fly_in_never_runs_backwards():
    # บั๊กเดิม: เฟรมแรกได้เวลาติดลบ กล้องเลยพุ่งออกไปไกลมาก แล้วกระจุกดาวไปค้างนอกกลางจอ
    assert "Math.max(0, Math.min(1, (performance.now() - view.t0) / view.dur))" in JS
    assert "(t - view.t0)" not in JS


def test_nebula_follows_real_star_positions():
    # หมอกต้องฟุ้งรอบดาวจริงแต่ละดวง ไม่ใช่ตำแหน่งที่เดาเอา
    assert "uniform vec3 uS[9];uniform float uSig[9];" in JS
    assert "gl.uniform3fv(gl.getUniformLocation(P.neb, 'uS'), P.nebS)" in JS
    for name in ("Merope", "Alcyone", "Maia", "Electra", "Taygeta", "Atlas", "Celaeno", "Pleione", "Asterope"):
        assert name + ": [" in JS.split("var NEB_W")[1].split("};")[0]
