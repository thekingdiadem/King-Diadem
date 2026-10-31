"""หน้าแรกแยกเป็น 3 ไฟล์แล้ว: static/index.html (โครง) · static/app.css (หน้าตา) · static/app.js (สคริปต์)

เทสต์ที่ตรวจข้อความในหน้าแรกอ่านผ่าน front_page() — ประกอบกลับเป็นหน้าเดียวเหมือนที่เบราว์เซอร์เห็น
(CSS แทรกกลับที่ <link> · สคริปต์แทรกกลับที่ <script src>) เทสต์เดิมจึงตรวจเจตนาเดิมได้ครบ"""
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "static"
LINK = '<link rel="stylesheet" href="/static/app.css">'
SCRIPT = '<script src="/static/app.js"></script>'


def front_page() -> str:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (STATIC / "app.css").read_text(encoding="utf-8")
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    assert LINK in html and SCRIPT in html, "index.html ต้องโหลด app.css และ app.js"
    return html.replace(LINK, "<style>\n" + css + "</style>").replace(SCRIPT, "<script>\n" + js + "</script>")
