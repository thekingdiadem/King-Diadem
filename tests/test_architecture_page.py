"""หน้า /architecture: อธิบายสถาปัตยกรรมให้คนที่สงสัย · ชื่อไฟล์ในเส้นทางของข้อความต้องเป็นไฟล์จริงที่ทำงานอยู่
· แผนที่ไฟล์อ่านจาก static/system_map.json ที่สร้างจาก repo (ไม่วาดมือ)"""
import json
import re
from pathlib import Path
from tests._front import front_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "static" / "architecture.html").read_text(encoding="utf-8")
MAP = json.loads((ROOT / "static" / "system_map.json").read_text(encoding="utf-8"))
ROWS = {r[0]: r for r in MAP["files"]}


def _embedded():
    html = front_page()
    return json.loads(re.search(r'id="system-map">(.*?)</script>', html, re.S).group(1))


def test_every_file_named_in_the_flow_is_real_and_live():
    """ชื่อไฟล์ในขั้นตอนของ POST /run ต้องมีอยู่จริง และเป็นไฟล์ที่ทำงาน (ไม่ใช่ของเก่า) — ไฟล์ถูกย้าย/ลบ เทสต์นี้จะเตือน"""
    named = set(re.findall(r'data-f="([^"]+)"', PAGE))
    assert len(named) >= 25
    for f in named:
        assert (ROOT / f).exists(), f
        assert ROWS[f][2] in ("boot", "request", "web"), (f, ROWS[f][2])


def test_council_step_names_the_router_council_too():
    """ศูนย์กลางเครื่องยนต์เรียก ENGINE/council_engine ซึ่งใช้สภาเดียวของระบบใน AI/council_engine"""
    assert 'data-f="ENGINE/council_engine.py"' in PAGE and 'data-f="AI/council_engine.py"' in PAGE


def test_map_json_matches_the_app_map():
    """ข้อมูลชุดเดียวกับแท็บ "ระบบจริง" ในแอป — สร้างพร้อมกันจากสคริปต์เดียว"""
    emb = _embedded()
    assert [(r[0], r[2]) for r in emb["files"]] == [(r[0], r[2]) for r in MAP["files"]]
    assert emb["edges"] == MAP["edges"]


def test_web_edges_show_what_pages_load():
    """เส้นชนิด 1 = ฝั่งเว็บ: app.py ส่งหน้า HTML · หน้า HTML โหลด CSS/JS (เดิมมีแค่ import ของ Python)"""
    idx = {r[0]: i for i, r in enumerate(MAP["files"])}
    web = {(MAP["files"][a][0], MAP["files"][b][0]) for a, b, k in MAP["edges"] if k == 1}
    assert ("app.py", "static/architecture.html") in web
    assert ("app.py", "static/notfound.html") in web            # ส่งด้วย os.path.join(..., "static", "notfound.html")
    assert ("static/architecture.html", "static/cinema.css") in web
    assert ("static/login.html", "static/portal.css") in web
    assert all(k in (0, 1, 2) for _, _, k in MAP["edges"]) and idx          # 2 = ทดสอบ/สร้าง/อ้างถึง


def test_new_html_pages_are_web_not_config():
    """หน้า HTML ใหม่ใน static/ เคยถูกจัดเป็น "ตั้งค่า" (notfound.html) — เป็นหน้าเว็บ"""
    for f in ("static/notfound.html", "static/architecture.html", "static/letter.html"):
        assert ROWS[f][2] == "web", f


def test_route_and_links(client):
    r = client.get("/architecture")
    assert r.status_code == 200 and "KING DIADEM ทำงานอย่างไร" in r.text
    assert client.get("/static/system_map.json").status_code == 200
    assert 'href="/architecture"' in (ROOT / "static" / "guide.html").read_text(encoding="utf-8")
    assert 'href="/architecture"' in front_page()
    assert "`/architecture`" in (ROOT / "SYSTEM_ARCHITECTURE.md").read_text(encoding="utf-8")


def test_map_is_readable_without_the_canvas():
    """แผนที่วาดบน canvas — รายการไฟล์แบบข้อความ (โฟลเดอร์) ต้องมีให้คนที่ใช้โปรแกรมอ่านหน้าจอ/คีย์บอร์ด"""
    assert 'id="flds"' in PAGE and "el('details'" in PAGE
    assert "cache: 'no-cache'" in PAGE and "getJSON('/static/system_map.json')" in PAGE   # สำรองเมื่อแผนผังสดใช้ไม่ได้
    assert "textContent" in PAGE and ".innerHTML = ''" in PAGE and "innerHTML = '<" not in PAGE   # ข้อมูลไฟล์ใส่เป็นข้อความเท่านั้น
