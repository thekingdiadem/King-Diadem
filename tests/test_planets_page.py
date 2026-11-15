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
