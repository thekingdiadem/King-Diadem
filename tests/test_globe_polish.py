"""ลูกโลกบนมือถือ: ไฟเมือง/เมฆเป็นบล็อกสี่เหลี่ยมตอนมองใกล้ หัวเรื่องจมอยู่ในไฟเมือง และขอบโลกหน้าแรกแตกเป็นจุดบนเครื่องช้า"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EARTH = (ROOT / "static/cockpit_earth.js").read_text(encoding="utf-8")
UNIVERSE = (ROOT / "static/king_diadem_universe.html").read_text(encoding="utf-8")
APP = (ROOT / "static/app.js").read_text(encoding="utf-8")


def test_close_up_lights_and_clouds_are_smoothed_only_when_magnified():
    assert "float mag=1.-smoothstep(" in EARTH
    assert "texture2D(lights,tc+hp)" in EARTH and "texture2D(clouds,cc+hp)" in EARTH
    assert "vec2 hp=px*1.3*mag;" in EARTH          # มองทั้งโลก (mag = 0) ได้ภาพเดิมทุกจุด


def test_hero_title_has_a_scrim_and_steps_aside_for_popups():
    assert ".cockpit::after{" in UNIVERSE and "opacity:var(--hero-a,1)" in UNIVERSE
    assert "#hero.pop-open>" in UNIVERSE and "classList.toggle('pop-open'" in EARTH


def test_home_globe_edge_scales_with_render_resolution():
    assert "float aa=2./(uR*uQ);" in APP
    assert "smoothstep(1.,1.-max(.01,aa),r)" in APP and "exp(-hg/max(.012,aa))" in APP


def test_scrim_ellipse_fits_inside_its_box():
    """วงรีของเงาต้องอยู่ในกรอบทั้งวง — เดิมขอบบนถูกตัดเป็นเส้นตรงพาดกลางลูกโลก เห็นชัดในโหมดกลางวัน"""
    assert "inset:30% 0 0 0" in UNIVERSE and "radial-gradient(110% 46% at 50% 56%" in UNIVERSE


def test_cloud_shadows_reuse_the_cloud_texture():
    assert "texture2D(clouds,cc+so).r" in EARTH and "cross(n,ea)" in EARTH


def test_hazard_pin_shows_coordinates_depth_and_distance_advice():
    assert "mag: x.mag, depth: x.depth" in EARTH
    assert "(en ? 'depth ' : 'ลึก ')" in EARTH and "className = 'hz-tip'" in EARTH
    assert "ไกลจากไทย — ที่นี่ไม่ต้องทำอะไร" in EARTH and "หมอบ หาที่กำบัง จับให้มั่น" in EARTH
