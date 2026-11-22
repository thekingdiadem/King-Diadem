"""Black Saturn (/saturn) — ผู้ใช้อยู่ตรงกลาง วงแหวนเครื่องยนต์สว่างตามขั้นที่ระบบทำจริง ยุบเมื่อทางเลือกหมด
แรงบันดาลใจ: คำตอบใหม่ของสมการไอน์สไตน์ใน 5 มิติ (J. Armas, arXiv 2026) — วงแหวนหลุมดำอยู่ได้เพราะหมุน"""
import re

from core import progress

HTML = open("static/black_saturn.html", encoding="utf-8").read()


def test_page_is_served_and_linked_from_universe(client):
    r = client.get("/saturn")
    assert r.status_code == 200 and "BLACK SATURN" in r.text
    uni = open("static/king_diadem_universe.html", encoding="utf-8").read()
    assert 'href="/saturn"' in uni


def test_ring_segments_are_the_real_pipeline_stages():
    """ทุกช่วงของวงแหวนต้องตรงกับขั้นที่ server บันทึกจริง (core/progress) — ไม่ใช่ภาพสวยที่ไม่ผูกกับระบบ"""
    segs = re.findall(r"\['(\w+)', '[^']+', '#[0-9a-f]{6}'\]", HTML)
    assert segs == list(progress.STAGES)
    assert "/api/progress/" in HTML and "rid: id" in HTML


def test_ring_collapses_when_choices_run_out():
    assert "var life = Math.max(0, shown / 3)" in HTML and "R = base * (.15 + .22 * Math.max(.06, life))" in HTML
    assert "Choice = 0" in HTML and 'id="choices"' in HTML


def test_csp_safe_and_respects_reduced_motion():
    assert not re.search(r"<[^>]+\son[a-z]+=", HTML)
    assert "prefers-reduced-motion" in HTML


def test_hybrid_colors_blend_not_flat():
    assert "function hybrid(" in HTML and "'lighter'" in HTML
