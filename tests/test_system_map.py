"""แผนผังระบบในหน้าเว็บ (#system-map) ต้องตรงกับ repo จริง

เดิมแผนผังเขียนมือแล้วค้างอยู่ที่ commit เก่า 75 commit: ไฟล์ที่ต่อเข้าระบบแล้วยังขึ้นว่าเป็นวิสัยทัศน์
และไฟล์ใหม่ไม่อยู่ในแผนผัง — ตอนนี้หน้าเว็บอ่านแผนผังสดจาก /api/system_map ชุดที่ฝังไว้เป็นแค่สำรอง + คำอธิบายไฟล์
"""
import json
import re

from scripts import build_system_map as sm


def _embedded():
    html = open(sm.INDEX, encoding="utf-8").read()
    return json.loads(sm._MAP_RE.search(html).group(2))


def test_live_map_covers_every_file_in_repo():
    """หน้า "ระบบ" ใช้แผนผังสดจากเซิร์ฟเวอร์แล้ว — เพิ่ม/ลบไฟล์โดยไม่รันสคริปต์ก็ไม่ทำให้ตัวเลขค้างหรือเทสต์ล้มอีก
    (เดิมเทสต์นี้บังคับให้ชุดที่ฝังไว้ตรงกับ repo เป๊ะ ลืมรันสคริปต์ทีไร CI แดงทันที)"""
    new = sm.build(_embedded())
    assert [r[0] for r in new["files"]] == sm.tracked()
    assert all(isinstance(r[1], int) and r[2] for r in new["files"])        # ทุกไฟล์มีจำนวนบรรทัดและหมวด
    old = {r[0]: r[3] for r in _embedded()["files"]}
    kept = [r for r in new["files"] if r[0] in old]
    assert kept and all(r[3] == old[r[0]] for r in kept)                    # คำอธิบายเดิมไม่หาย


def test_tracked_files_without_git(monkeypatch):
    """บนเซิร์ฟเวอร์ที่ไม่มี git ก็ยังนับไฟล์ได้ — เดินโฟลเดอร์เอง ตัดข้อมูลตอนรันและแคชทิ้ง"""
    with_git = set(sm.tracked())

    def no_git(*a, **k):
        raise OSError("git not found")
    monkeypatch.setattr(sm.subprocess, "check_output", no_git)
    walked = sm.tracked()
    assert with_git <= set(walked)
    assert not [f for f in walked if "__pycache__" in f or f.startswith((".git/", "data/")) or f.endswith((".pyc", ".db"))]
    assert sm.head_commit("abc1234") == "abc1234"                          # ไม่มี git ก็ไม่ล้ม


def test_commit_comes_from_render_when_deployed(monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "0123456789abcdef")
    assert sm.head_commit("old") == "0123456"


def test_live_endpoint_counts_running_files(client):
    import app as app_module
    app_module._live_map = None
    d = client.get("/api/system_map").json()
    assert d["live"] is True and d["built_at"]
    assert [r[0] for r in d["files"]] == sm.tracked()
    assert d["edges"] and d["commit"]
    assert client.get("/api/system_map").json() is not None                 # ครั้งต่อไปใช้ของที่คำนวณไว้


def test_system_page_prefers_live_map():
    html = open(sm.INDEX, encoding="utf-8").read()
    js = open(sm.INDEX.replace("index.html", "app.js"), encoding="utf-8").read()     # สคริปต์หน้าแรกอยู่ static/app.js
    assert "fetch('/api/system_map'" in js and "MAP = d; mapLive = true;" in js
    # ป้ายเด่นใต้ Σ บอกว่าตัวเลขสดไหม (เดิมเป็นคำเล็กๆ ท้าย commit เจ้าของโปรเจกต์หาไม่เจอ)
    assert '<div id="sys-live" class="live-pill wait" role="status"' in html
    assert "'สด · นับจากโค้ดที่รันอยู่จริง'" in js and "'ชุดที่ฝังไว้ · ยังโหลดตัวเลขสดไม่ได้'" in js
    assert "pill.className = 'live-pill ' + (mapLive ? 'on' : mapLoading ? 'wait' : 'old');" in js
    assert js.index("loadLiveMap();                                   // ขอตัวเลขสดก่อน") < js.index("  sysStats();\n  $('#sys-eq')")
    arch = open(sm.INDEX.replace("index.html", "architecture.html"), encoding="utf-8").read()
    assert "getJSON('/api/system_map').catch(function(){ return getJSON('/static/system_map.json'); })" in arch


def test_edges_point_at_real_files():
    m = _embedded()
    n = len(m["files"])
    assert m["edges"] and all(0 <= a < n and 0 <= b < n for a, b, _ in m["edges"])


def test_deleted_legacy_folder_is_gone_from_the_map():
    """โฟลเดอร์ legacy/ ถูกลบแล้ว (พี่อนุญาต) — แผนที่ต้องไม่ชี้ไปหาไฟล์ที่ไม่มีอยู่"""
    rows = {r[0]: r for r in _embedded()["files"]}
    assert not [p for p in rows if p.startswith("legacy/")]
    assert rows["app.py"][2] in ("boot", "request")


def test_map_json_cannot_close_the_script_tag():
    html = open(sm.INDEX, encoding="utf-8").read()
    body = re.search(r'id="system-map">(.*?)</script>', html, re.S).group(1)
    assert "</" not in body


def test_web_assets_follow_what_pages_load():
    """แผนผังจัดหมวดตามที่หน้าเว็บโหลดจริง: หน้า The Universe เปลี่ยนจากฉากเมฆ (galaxy_scene.js)
    เป็นท้องฟ้าจากข้างใน (universe_sky.js) แล้ว — ไฟล์เดิมลบออกจาก repo แล้ว (พี่อนุญาต)"""
    rows = {r[0]: r for r in _embedded()["files"]}
    assert rows["static/universe_sky.js"][2] == "web"
    assert "static/galaxy_scene.js" not in rows
    assert rows["static/i18n.js"][2] == "web"
    for gone in ("ai_brain.js", "galaxy_scene_api.js", "main.js", "decision.js", "ai_thinking.js"):
        assert f"static/{gone}" not in rows                 # ไม่มีหน้าไหนหรือแกลเลอรีโหลด — ลบแล้ว (พี่อนุญาต)
    # app.js เก่า (ไม่มีใครโหลด) ลบไปแล้ว · ชื่อนี้กลับมาเป็นสคริปต์หลักของหน้าแรกที่แยกออกจาก index.html
    assert rows["static/app.js"][2] == "web" and rows["static/app.css"][2] == "web"


def test_script_loaded_from_js_counts_as_used():
    """หน้า The Universe โหลดท้องฟ้าด้วย s.src = '...' (ไม่ใช่ src="...")
    เดิมสคริปต์อ่านแค่ src="..." เลยจัดไฟล์ที่ยังใช้อยู่เป็นรุ่นเก่า"""
    files = sm.tracked()
    assert "universe_sky.js" in sm.static_refs(files)


def test_new_static_script_is_classified_by_usage():
    """ไฟล์ JS ใหม่ใน static/ ที่หน้าเว็บโหลดต้องขึ้นเป็น web ตั้งแต่ครั้งแรก (เดิมค้างเป็น config)"""
    old = _embedded()
    old["files"] = [r for r in old["files"] if r[0] != "static/universe_sky.js"]
    rows = {r[0]: r for r in sm.build(old)["files"]}
    assert rows["static/universe_sky.js"][2] == "web"


def test_file_moved_back_from_legacy_is_live():
    """ย้ายไฟล์กลับจาก legacy/ แล้วต่อเข้าระบบ — เดิมสคริปต์ไม่รู้จัก ไฟล์ตกไปหมวด "config" ทั้งที่ทำงานจริง"""
    rows = {r[0]: r for r in _embedded()["files"]}
    assert "legacy/DOMAINS/business_engine.py" not in rows
    assert rows["DOMAINS/business_engine.py"][2] == "request"
    assert "ย้ายกลับจาก legacy/" in rows["DOMAINS/business_engine.py"][6]


def test_new_live_python_file_is_not_stuck_in_config():
    """ไฟล์ Python ใหม่ที่ app.py เรียกใช้ (core/history_export.py) เคยค้างหมวด "config" ทั้งที่ทำงานจริง"""
    rows = {r[0]: r for r in _embedded()["files"]}
    assert rows["core/history_export.py"][2] == "request"
    assert rows["scripts/build_system_map.py"][2] == "request"    # app.py เรียกสร้างแผนผังสดตอนมีคนขอ (/api/system_map)
    assert rows["scripts/stress_test.py"][2] == "tests"              # สคริปต์ที่ไม่ได้อยู่ในเส้นทางของแอปไม่ถูกนับว่าทำงาน


def test_gallery_and_asset_files_are_classified_by_real_use():
    """JS ที่หน้าแกลเลอรี (index.html ราก) โหลด เคยขึ้นว่า "รุ่นเก่า ไม่มีหน้าไหนโหลด" ·
    ภาพที่ CSS ใช้ (hero.jpg) เคยขึ้นว่าเป็นไฟล์ตั้งค่า · คอมเมนต์ใน app.py ไม่นับเป็นการใช้งาน"""
    rows = {r[0]: r for r in _embedded()["files"]}
    assert rows["static/galaxy.js"][2] == "site" and "แกลเลอรี" in rows["static/galaxy.js"][3]
    assert rows["static/hero.jpg"][2] == "web" and rows["static/icons/icon-192.png"][2] == "web"
    assert rows["static/service-worker.js"][2] == "web"           # เสิร์ฟโดย app.py ที่ /service-worker.js
    assert rows["static/warp_intro.js"][2] == "site"              # ยังใช้ในแกลเลอรี — เก็บไว้


def test_earth_assets_loaded_by_js_are_web_not_config():
    """ภาพโลก/ข้อมูลเมืองโหลดจาก cockpit_earth.js ด้วยชื่อที่ประกอบตอนรัน — เดิมขึ้นเป็นไฟล์ตั้งค่า"""
    rows = {r[0]: r for r in _embedded()["files"]}
    for f in ("static/earth/day_4k.jpg", "static/earth/cities_t3.json", "static/earth/capitals.json"):
        assert rows[f][2] == "web", f


def test_no_orphan_legacy_files_left():
    """ธีม deepspace ไม่มีหน้าไหนโหลด — ลบแล้ว (พี่อนุญาตให้ตัดส่วนที่ไม่ใช้) และต้องไม่มีไฟล์ค้างหมวด legacy"""
    rows = _embedded()["files"]
    assert not [r[0] for r in rows if r[2] == "legacy"]
    assert "static/kd_theme_deepspace.css" not in {r[0] for r in rows}


def test_docs_do_not_link_to_deleted_files():
    import os
    readme = open("README.md", encoding="utf-8").read()
    assert "legacy/README.md" not in readme
    gallery = open("index.html", encoding="utf-8").read()
    assert "kd_theme_deepspace" not in gallery
    from core.emptiness_guard import CONNECTED_MODULES
    assert all(os.path.exists(p) for p in CONNECTED_MODULES), [p for p in CONNECTED_MODULES if not os.path.exists(p)]


def _edges(m):
    names = [r[0] for r in m["files"]]
    return {(names[a], names[b], k) for a, b, k in m["edges"]}


def test_files_are_connected_by_real_references():
    """เดิมนับเส้นแค่ import จาก app.py กับหน้าเว็บโหลด JS/CSS — 268 จาก 397 ไฟล์ลอยเดี่ยวในแผนที่
    ทั้งที่มีเทสต์ทดสอบ สคริปต์สร้าง หรือหน้าเว็บโหลดอยู่จริง ตอนนี้เหลือแค่เอกสารที่ไม่มีใครอ้างถึงจริงๆ"""
    m = sm.build(_embedded())
    e = _edges(m)
    linked = {a for a, _, _ in e} | {b for _, b, _ in e}
    alone = [r[0] for r in m["files"] if r[0] not in linked]
    assert all(f.endswith((".md", ".txt")) for f in alone), alone
    assert len(alone) < 20
    assert ("tests/test_pleiades_view.py", "static/pleiades_view.js", 2) in e      # เทสต์อ่านไฟล์ด้วย ROOT / "static" / ...
    assert ("static/app.js", "static/pleiades_view.js", 1) in e                    # หน้าแรกโหลดตอนแตะดาวลูกไก่
    assert ("static/index.html", "static/app.js", 1) in e and ("static/index.html", "static/app.css", 1) in e
    assert ("scripts/build_sky_stars.py", "static/earth/sky_taurus.json", 2) in e  # สคริปต์สร้างไฟล์ข้อมูลฟ้า
    assert ("tests/test_pleiades_view.py", "tests/conftest.py", 2) in e


def test_reference_edges_do_not_double_count():
    """คู่ไฟล์เดียวกันมีเส้นเดียว — import (0) และหน้าเว็บโหลด (1) ชนะเส้นอ้างถึง (2)"""
    m = sm.build(_embedded())
    pairs = [(a, b) for a, b, _ in m["edges"]]
    assert len(pairs) == len(set(pairs))
