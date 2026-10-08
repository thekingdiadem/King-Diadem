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
