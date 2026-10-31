"""เจ้าของโปรเจกต์ขอเอาชื่อตัวเองออกจากหน้าเว็บ — ทุกหน้าที่ผู้ใช้เปิดเห็นต้องไม่มีชื่อ (ไทย/อังกฤษ/ญี่ปุ่น)

ครอบคลุม static/ (เว็บแอป), index.html ที่ root (แกลเลอรี) และ docs/ (หน้าเว็บเอกสาร)
ไม่รวม portfolio.html (พอร์ตโฟลิโอส่วนตัว) และเอกสาร/โค้ดที่ไม่ได้แสดงบนเว็บ
"""
import re
from pathlib import Path
from tests._front import front_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"nithikorn|bunsrang|boonsang|นิธิกร|บุญสร้าง|ニティコーン|ブンサーン", re.I)
WEB_SUFFIXES = {".html", ".js", ".css", ".json", ".webmanifest", ".svg", ".txt"}


def _web_files():
    for p in (ROOT / "static").rglob("*"):
        if p.is_file() and p.suffix in WEB_SUFFIXES:
            yield p
    yield ROOT / "index.html"
    yield from (ROOT / "docs").glob("*.html")


def test_owner_name_is_not_on_any_web_page():
    hits = [str(p.relative_to(ROOT)) for p in _web_files() if NAME.search(p.read_text(encoding="utf-8"))]
    assert not hits, hits


def test_pure_axis_line_still_translated():
    """บรรทัดใน THE PURE AXIS ที่เคยมีชื่อ ยังมีคำแปลอังกฤษ/ญี่ปุ่นตรงกับข้อความไทยใหม่"""
    line = "ไม่ต้องมีใครคนใดคนหนึ่งจึงจะใช้งานได้"
    assert f"<p>{line}</p>" in front_page()
    assert f"'{line}': [" in (ROOT / "static" / "i18n.js").read_text(encoding="utf-8")
