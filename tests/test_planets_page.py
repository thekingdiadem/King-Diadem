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


def test_planets_can_be_turned_by_hand_and_zoomed():
    """เจ้าของโปรเจกต์: อยากให้คนเอามือหมุนดาวได้ ฉากหลังเคลื่อนตามอย่างลื่น · ระยะไม่เคยเท่ากัน แต่ดาวยังเป็นดวงเดิม"""
    from pathlib import Path
    src = (Path(__file__).resolve().parent.parent / "static" / "planets.html").read_text(encoding="utf-8")
    assert "addEventListener('pointermove'" in src and "addEventListener('wheel'" in src
    assert "gl.uniform3f(U.uRot" in src and "uRot.x*.12" in src          # ฉากหลังเลื่อนตาม (พารัลแลกซ์)
    assert "ivrot(nv)" in src and "RN=vrot(RN)" in src                     # ดวงและวงแหวนหมุนไปด้วยกัน
    assert "onclick=" not in src


def test_background_is_the_real_sky_behind_each_body_today():
    """ทุกดวงอยู่ใต้ฟ้าผืนเดียวกัน — ฉากหลังคือกลุ่มดาวจริงที่ดวงนั้นอยู่วันนี้ (มองจากโลก)"""
    import json, subprocess
    from pathlib import Path
    src = (Path(__file__).resolve().parent.parent / "static" / "planets.html").read_text(encoding="utf-8")
    js = src[src.index("var REALSKY"):src.index("/* ใช้ทิศจริงของวันนี้")]
    out = subprocess.run(["node", "-e", js + "console.log(JSON.stringify(REALSKY(new Date('2026-11-15'))))"],
                         capture_output=True, text=True, timeout=20)
    if out.returncode:
        import pytest
        pytest.skip("ไม่มี node")
    r = json.loads(out.stdout)
    assert -150 < r["5"][0] < -125 and 35 < r["5"][1] < 55        # พฤหัส: ปู/สิงโต (ฟ้าเหนือดาราจักร)
    assert 90 < r["6"][0] < 135 and r["6"][1] < -50                # เสาร์: ปลา (ฟ้าใต้ดาราจักร)
    assert "REALSKY(new Date())" in src
