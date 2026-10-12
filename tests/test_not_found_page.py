"""ลิงก์ผิด/ลิงก์เก่า: เบราว์เซอร์ได้หน้า 404 ในธีมของเว็บ (แทน {"detail":"Not Found"} ดิบๆ) · API ยังได้ JSON"""
from pathlib import Path

PAGE = (Path(__file__).resolve().parent.parent / "static" / "notfound.html").read_text(encoding="utf-8")
HTML = {"accept": "text/html,application/xhtml+xml,*/*;q=0.8"}


def test_browser_gets_the_themed_page_with_a_real_404(client):
    for path in ("/no-such-page", "/static/no-such-file.html", "/report-old-link/abc"):
        r = client.get(path, headers=HTML)
        assert r.status_code == 404, path                      # ยังเป็น 404 จริง — เครื่องมือค้นหาไม่เก็บเป็นหน้าปกติ
        assert r.headers["content-type"].startswith("text/html")
        assert "ที่นี่ยังไม่มีดาว" in r.text


def test_programs_still_get_json(client):
    r = client.get("/no-such-page")                            # fetch() ปกติส่ง Accept: */*
    assert r.status_code == 404 and r.json() == {"detail": "Not Found"}
    r = client.get("/api/no-such-endpoint", headers=HTML)      # ใต้ /api/ เป็น JSON เสมอ
    assert r.status_code == 404 and r.json() == {"detail": "Not Found"}
    r = client.post("/no-such-page", headers=HTML)
    assert r.status_code in (404, 405) and "ที่นี่ยังไม่มีดาว" not in r.text


def test_other_errors_are_untouched(client):
    r = client.post("/letter", headers=HTML)                   # มีหน้านี้ แต่ไม่รับ POST
    assert r.status_code == 405 and "ที่นี่ยังไม่มีดาว" not in r.text


def test_page_always_offers_a_way_forward():
    """Choice(t) ≥ 1 — หน้า 404 มีทางไปต่อเสมอ และแสดงที่อยู่ด้วย textContent (ไม่ตีความเป็น HTML)"""
    for href in ('href="/"', 'href="/ask"', 'href="/guide"'):
        assert href in PAGE
    assert 'href="/letter"' not in PAGE                        # พี่ไม่ให้โชว์จดหมายในหน้านี้
    assert ".textContent = decodeURIComponent(location.pathname + location.search)" in PAGE
    assert "innerHTML" not in PAGE
    assert '<meta name="robots" content="noindex">' in PAGE
