"""ติดตั้งเป็นแอปบนมือถือได้ (PWA) + เปิดได้ตอนออฟไลน์
เดิม: มี manifest และ service worker แต่ไม่มีหน้าไหน register · SW อยู่ใต้ /static/ (ดูแลได้แค่ /static/)
· ไอคอนเป็น logo.png 1920px ไฟล์เดียวที่ประกาศว่าเป็น 192 และ 512 พร้อม maskable (โลโก้ถูกตัดขอบ)"""
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "static"
SW = (S / "service-worker.js").read_text(encoding="utf-8")
MAN = json.loads((S / "manifest.json").read_text(encoding="utf-8"))


def test_service_worker_is_served_from_the_root_and_always_rechecked(client):
    r = client.get("/service-worker.js")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/javascript")
    assert r.headers["service-worker-allowed"] == "/" and r.headers["cache-control"] == "no-cache"


def test_app_registers_it():
    page = (S / "index.html").read_text(encoding="utf-8")
    assert "navigator.serviceWorker.register('/service-worker.js', {scope:'/'})" in page
    assert '<link rel="apple-touch-icon" href="/static/icons/apple-touch-icon.png">' in page


def test_network_first_and_never_caches_private_data():
    """ออนไลน์ = ได้ไฟล์ใหม่เสมอ (ไม่ค้างของเก่าหลัง deploy) · แคชเฉพาะ "/" กับ /static/ ไม่มี query · ไม่แตะ API/บัญชี"""
    assert "fetch(req).then(" in SW and "staleWhileRevalidate" not in SW
    assert "if (req.method !== 'GET') return;" in SW
    assert "if (url.origin !== self.location.origin || url.search) return false;" in SW
    assert "return url.pathname === '/' || url.pathname.indexOf('/static/') === 0;" in SW
    assert "if (!nav && !cacheable(url)) return;" in SW


def test_offline_page_works_without_network():
    off = (S / "offline.html").read_text(encoding="utf-8")
    assert "fonts.googleapis" not in off and "<script src" not in off       # ไม่โหลดอะไรจากภายนอก
    assert "1669" in off and "191" in off and "1323" in off                 # เบอร์ฉุกเฉินโทรได้แม้ไม่มีเน็ต
    assert "'/static/offline.html'" in SW


def test_manifest_icons_have_the_sizes_they_claim():
    seen = set()
    for ic in MAN["icons"]:
        w, h = (int(x) for x in ic["sizes"].split("x"))
        with Image.open(ROOT / ic["src"].lstrip("/")) as im:
            assert im.size == (w, h), ic
        seen.add(ic["purpose"])
    assert seen == {"any", "maskable"}                                     # maskable แยกไฟล์ มีขอบปลอดภัย
    with Image.open(S / "icons" / "apple-touch-icon.png") as im:
        assert im.size == (180, 180) and im.mode in ("RGB", "P")


def test_manifest_matches_the_app():
    page = (S / "index.html").read_text(encoding="utf-8")
    assert f'<meta name="theme-color" content="{MAN["theme_color"]}">' in page
    assert MAN["start_url"] == "/" and MAN["scope"] == "/" and MAN["display"] == "standalone"
    assert {s["url"] for s in MAN["shortcuts"]} == {"/?new=1", "/?tab=tools"}
    assert "qs.get('new') === '1'" in page and "qs.get('tab')" in page          # ทางลัดใช้งานได้จริง
