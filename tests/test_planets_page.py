"""หน้าระบบสุริยะ: ทุกดวงเรนเดอร์สด (ไม่ใช้ภาพของคนอื่น) บนฟ้าจริงจาก Gaia · ไม่มีสคริปต์ในแท็ก (CSP)"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / "static" / "planets.html").read_text(encoding="utf-8")


def test_twelve_bodies_with_facts():
    assert len(re.findall(r"\{k:\d+, th:", HTML)) == 12
    for name in ("ดวงอาทิตย์", "ดาวพุธ", "ดาวศุกร์", "โลก", "ดาวอังคาร", "ดาวพฤหัสบดี", "ดาวเสาร์", "ดาวยูเรนัส", "ดาวเนปจูน", "ดาวพลูโต", "ซีรีส", "ดวงจันทร์"):
        assert f"th:'{name}'" in HTML, name


def test_uses_only_own_assets_and_credits_them():
    srcs = re.findall(r"tex\('([^']+)'", HTML)
    assert srcs and all(s.startswith("/static/") for s in srcs)
    assert "ESA/Gaia/DPAC" in HTML and "NASA" in HTML


def test_no_inline_handlers_and_reserved_glsl_names():
    assert not re.search(r"\son[a-z]+=\"", HTML)
    assert "gl_=" not in HTML


def test_smooth_on_slow_devices():
    assert "QS = Math.max(.55" in HTML           # ลดความละเอียดเองเมื่อเฟรมช้า
    assert "prefers-reduced-motion" in HTML


def test_linked_from_universe_tab():
    assert 'href="/static/planets.html"' in (ROOT / "static" / "index.html").read_text(encoding="utf-8")


def test_every_body_has_its_own_sky_and_tint():
    m = re.search(r"var VIEW = \[(.*?)\n\];", HTML, re.S)
    rows = re.findall(r"\[(-?\d+), (-?\d+), (-?[\d.]+), \[", m.group(1))
    assert len(rows) == 12 and len({(a, b) for a, b, _ in rows}) == 12     # ไม่มีดวงไหนใช้ฟ้าซ้ำกัน


def test_thai_below_vowels_not_clipped_in_title():
    """สระอู/อุ ใต้บรรทัด (ดาวพุธ ดาวพลูโต ดาวยูเรนัส ดาวเนปจูน) เคยถูกตัดเพราะ line-height 1.02 กับ background-clip:text"""
    h1 = re.search(r"h1\{([^}]*)\}", HTML).group(1)
    lh = float(re.search(r"/(\d*\.?\d+) var", h1).group(1))
    assert lh >= 1.15 and "padding" in h1


def test_front_page_sky_varies_per_visit():
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "SKY_VIEWS" in js and "Math.random() * SKY_VIEWS.length" in js


def test_shader_has_no_undefined_glsl_math():
    """หัวใจพลูโตเคยเหลือแค่สองแฉก: pow(ฐานติดลบ, n) และ smoothstep ขอบกลับด้าน ไม่นิยามใน GLSL"""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent.parent / "static" / "planets.html").read_text(encoding="utf-8")
    assert not re.search(r"pow\([^;]*?,\s*[23]\.\)", src.replace("pow(1.-nv.z,3.)", "").replace("pow(ฐานติดลบ,3.)", ""))
    for a, b in re.findall(r"smoothstep\((-?[\d.]+),(-?[\d.]+),", src):
        assert float(a) < float(b), f"smoothstep({a},{b}) ขอบกลับด้าน"
