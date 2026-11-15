"""ฉากหลังหน้าแรกใช้ฟ้าจากข้อมูลจริง (static/sky/allsky.jpg) แบบมุมมองผู้สังเกต"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_allsky_image_exists_and_is_light_enough_for_mobile():
    p = ROOT / "static" / "sky" / "allsky.jpg"
    assert p.exists() and p.stat().st_size < 900_000


def test_allsky_is_credited_and_reproducible():
    md = (ROOT / "static" / "sky" / "ALLSKY.md").read_text(encoding="utf-8")
    assert "ESA/Gaia/DPAC" in md and "CC BY-SA" in md
    assert (ROOT / "scripts" / "build_allsky.py").exists()


def test_front_page_shader_uses_real_sky_with_fallback():
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "/static/sky/allsky.jpg" in js and "uSkyOn" in js
    assert "if(uSkyOn>.5)" in js and "} else {" in js          # ยังโหลดไม่เสร็จ = ใช้แถบที่คำนวณแทน
    assert "gl_=" not in js                                      # ชื่อที่ขึ้นต้นด้วย gl_ ถูกจองไว้ใน GLSL
