"""โทนเดียวกันทุกหน้า: หน้านอกหน้าแรกเคยเป็นพื้นดำเรียบ และหน้าสมัครมีลิงก์ข้อกำหนด/ความเป็นส่วนตัวเป็นน้ำเงินเข้มบนพื้นมืด อ่านแทบไม่ออก"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "static/brand/brand.css").read_text(encoding="utf-8")
PAGES = ["guide", "learn", "privacy", "terms", "support", "refund", "architecture", "notfound", "wallet", "register"]


def test_every_secondary_page_loads_the_shared_tone_once():
    for f in PAGES:
        s = (ROOT / f"static/{f}.html").read_text(encoding="utf-8")
        assert s.count('<link rel="stylesheet" href="/static/brand/brand.css">') == 1, f
        assert s.index("brand/brand.css") < s.index("</head>"), f


def test_shared_tone_is_light_touch():
    assert "pointer-events:none" in CSS                       # แสงบรรยากาศไม่บังการกด
    assert "url(" not in CSS and "animation" not in CSS and "@import" not in CSS
    assert ":where(a:not([class])){color:#ecd6a6" in CSS      # น้ำหนักศูนย์: สีลิงก์ที่หน้านั้นกำหนดเองยังชนะ
