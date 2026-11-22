"""หน้า /equations — สมการต้องอยู่ใน HTML ตรงๆ (ไม่ใช่ใส่ด้วย JS) และอยู่ใน sitemap"""
import os
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "x" * 40)
HTML = Path("static/equations.html").read_text(encoding="utf-8")


def test_both_spellings_in_plain_html():
    for s in ("Choice(t) ≥ 1 → collapse = False", "Choice(t) &gt;= 1 -&gt; collapse = False",
              "Risk = Drift × Exposure × Time / Remaining Choice", "Risk = Drift * Exposure * Time / Remaining Choice"):
        assert s in HTML
    assert "DefinedTermSet" in HTML and "<title>Choice(t)" in HTML


def test_served_and_in_sitemap():
    from fastapi.testclient import TestClient
    import app
    c = TestClient(app.app)
    assert c.get("/equations").status_code == 200
    assert "/equations" in c.get("/sitemap.xml").text
