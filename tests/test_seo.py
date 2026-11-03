"""ให้ Google เจอ KING DIADEM — เดิมไม่มี robots.txt / sitemap.xml / canonical / ข้อมูลโครงสร้าง
และชื่อหน้าแรกมีแค่ "KING DIADEM" คนค้นหา "ช่วยตัดสินใจ" ไม่มีทางเจอ"""
import json
import re

from tests._front import front_page


def test_robots_allows_public_and_blocks_private(client):
    t = client.get("/robots.txt").text
    assert "Allow: /" in t and "Sitemap: https://" in t and "/sitemap.xml" in t
    for p in ("/api/", "/report/", "/auth/", "/dashboard"):
        assert f"Disallow: {p}" in t, p


def test_sitemap_lists_only_public_pages_that_exist(client):
    r = client.get("/sitemap.xml")
    assert r.status_code == 200 and "xml" in r.headers["content-type"]
    locs = re.findall(r"<loc>([^<]+)</loc>", r.text)
    assert len(locs) >= 8 and not any("/api/" in u or "/report/" in u for u in locs)
    for u in locs:
        path = "/" + u.split("://", 1)[1].split("/", 1)[1]
        assert client.get(path).status_code == 200, path


def test_front_page_has_title_description_canonical_and_structured_data():
    page = front_page()
    title = re.search(r"<title>([^<]+)</title>", page).group(1)
    assert "KING DIADEM" in title and "ตัดสินใจ" in title
    assert '<link rel="canonical" href="https://king-diadem.onrender.com/">' in page
    for tag in ('property="og:description"', 'property="og:url"', 'name="twitter:title"'):
        assert tag in page, tag
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.+?)</script>', page).group(1))
    kinds = {n["@type"] for n in ld["@graph"]}
    assert {"WebApplication", "Organization"} <= kinds


def test_google_verification_from_render_env(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "_GSV", "abc_DEF-123")
    monkeypatch.setattr(app_module, "_INDEX_HTML", None)
    t = client.get("/").text
    assert '<meta name="google-site-verification" content="abc_DEF-123">' in t
    monkeypatch.setattr(app_module, "_INDEX_HTML", None)


def test_private_pages_stay_out_of_search():
    for f in ("static/report.html", "static/notfound.html"):
        assert 'name="robots" content="noindex' in open(f, encoding="utf-8").read()
