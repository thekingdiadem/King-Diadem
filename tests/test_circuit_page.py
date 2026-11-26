"""หน้าวงจรระบบ (/circuit): วาดจากแผนผังจริงเท่านั้น และเปิดได้จากหน้าแรก"""
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "static/circuit.html").read_text(encoding="utf-8")


def test_route_serves_page():
    import app
    r = TestClient(app.app).get("/circuit")
    assert r.status_code == 200 and "วงจรระบบ" in r.text


def test_draws_only_from_real_map():
    assert "getJSON('/api/system_map')" in HTML and "/static/system_map.json" in HTML


def test_respects_reduced_motion_and_caps_pulses_on_mobile():
    assert "prefers-reduced-motion" in HTML
    assert "mobile ? 26" in HTML


def test_linked_from_front_page():
    from tests._front import front_page
    assert 'href="/circuit"' in front_page()


def test_journey_follows_real_pipeline_files():
    """ทุกไฟล์ในเส้นทาง "ดูข้อความเดินทาง" ต้องมีอยู่จริง และถูกเรียกใช้ใน app.py"""
    import re
    stops = re.findall(r"\['([^']+\.py)', '[^']+'\]", HTML[HTML.index("var JOURNEY"):HTML.index("];", HTML.index("var JOURNEY"))])
    assert stops[0] == "app.py" and stops[-1] == "app.py" and len(stops) >= 6
    app_src = (ROOT / "app.py").read_text(encoding="utf-8")
    for p in stops:
        assert (ROOT / p).exists(), p
        if p != "app.py":
            assert p[:-3].replace("/", ".") in app_src, p
