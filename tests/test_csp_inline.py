"""CSP ไม่มี 'unsafe-inline' สำหรับสคริปต์แล้ว (เจ้าของโปรเจกต์ขอเสริมความปลอดภัยข้อ 1)

เดิมถ้ามีจุดไหนหลุดให้ข้อความกลายเป็น <script> หรือ <img onerror="..."> เบราว์เซอร์จะรันทันที
ตอนนี้สคริปต์ในไฟล์ HTML ทำงานได้เฉพาะตัวที่ hash ตรง และไม่มี handler ที่เขียนในแท็กเหลืออยู่"""
import base64
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_FILES = sorted(set(ROOT.glob("*.html")) | set((ROOT / "static").rglob("*.html")))
TAG_HANDLER = re.compile(r"<[a-zA-Z][^<>]*\son[a-z]+\s*=", re.S)


def _script_src(client):
    csp = client.get("/").headers["content-security-policy"]
    return re.search(r"script-src ([^;]*)", csp).group(1).split()


def test_no_unsafe_inline_for_scripts(client):
    src = _script_src(client)
    assert "'unsafe-inline'" not in src and "'unsafe-eval'" not in src
    assert src[0] == "'self'"


def test_every_inline_script_is_allowed_by_hash(client):
    import app as A
    allowed = set(_script_src(client))
    n = 0
    for f in HTML_FILES:
        for m in A._INLINE_SCRIPT.finditer(f.read_text(encoding="utf-8")):
            t = re.search(r"\btype\s*=\s*[\"']?([^\"'\s>]+)", m.group(1), re.I)
            if t and t.group(1).lower() not in A._JS_TYPES:
                continue
            h = "'sha256-" + base64.b64encode(hashlib.sha256(m.group(2).encode()).digest()).decode() + "'"
            assert h in allowed, f.name
            n += 1
    assert n >= 15


def test_no_handlers_written_in_html_tags():
    for f in HTML_FILES:
        text = f.read_text(encoding="utf-8")
        text = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.S | re.I)   # โค้ดในสคริปต์ไม่ใช่แท็ก
        assert not TAG_HANDLER.search(text), f.name


def test_json_data_blocks_are_not_hashed(client):
    import app as A
    page = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="system-map">(.*?)</script>', page, re.S)
    h = "'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode() + "'"
    assert h not in _script_src(client)
