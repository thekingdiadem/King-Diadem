"""แผนผังระบบในหน้าเว็บ (#system-map) ต้องตรงกับ repo จริง

เดิมแผนผังเขียนมือแล้วค้างอยู่ที่ commit เก่า 75 commit: ไฟล์ที่ต่อเข้าระบบแล้วยังขึ้นว่าเป็นวิสัยทัศน์
และไฟล์ใหม่ไม่อยู่ในแผนผัง — ถ้าเทสต์นี้ล้ม ให้รัน  SECRET_KEY=x python scripts/build_system_map.py
"""
import json
import re

from scripts import build_system_map as sm


def _embedded():
    html = open(sm.INDEX, encoding="utf-8").read()
    return json.loads(sm._MAP_RE.search(html).group(2))


def test_map_matches_repo():
    old = _embedded()
    new = sm.build(old)
    # เทียบชื่อไฟล์กับหมวด (จำนวนบรรทัดเปลี่ยนทุกครั้งที่แก้ไฟล์ — ไม่นับ)
    assert [(r[0], r[2]) for r in old["files"]] == [(r[0], r[2]) for r in new["files"]], \
        "แผนผังไม่ตรงกับ repo — รัน SECRET_KEY=x python scripts/build_system_map.py"


def test_edges_point_at_real_files():
    m = _embedded()
    n = len(m["files"])
    assert m["edges"] and all(0 <= a < n and 0 <= b < n for a, b, _ in m["edges"])


def test_moved_files_are_marked_legacy():
    rows = {r[0]: r for r in _embedded()["files"]}
    legacy = [p for p in rows if p.startswith("legacy/") and p.endswith(".py")]
    assert legacy and all(rows[p][2] == "legacy" for p in legacy)
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
    assert rows["static/ai_brain.js"][2] == "legacy"      # ไม่มีหน้าไหนโหลด


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
