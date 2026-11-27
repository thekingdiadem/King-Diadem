"""ไอคอนบนแถบที่อยู่ต้องเป็นตัวปัจจุบันทุกทาง: /favicon.ico · <link rel=icon> · ไม่มี alternate icon ชี้ตราเก่า"""
import glob
import os

os.environ.setdefault("SECRET_KEY", "x" * 40)


def test_favicon_ico_serves_current_icon():
    from fastapi.testclient import TestClient
    import app
    r = TestClient(app.app).get("/favicon.ico")
    assert r.status_code == 200 and r.content == open("static/icons/favicon-48.png", "rb").read()


def test_no_page_points_browser_at_old_logo_as_icon():
    for f in glob.glob("static/*.html"):
        assert 'rel="alternate icon" href="/static/logo.png"' not in open(f, encoding="utf-8").read(), f
