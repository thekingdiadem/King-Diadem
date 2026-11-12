"""โทนเดียวกันทุกหน้า: หน้านอกหน้าแรกเคยเป็นพื้นดำเรียบ และหน้าสมัครมีลิงก์ข้อกำหนด/ความเป็นส่วนตัวเป็นน้ำเงินเข้มบนพื้นมืด อ่านแทบไม่ออก"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "static/brand/brand.css").read_text(encoding="utf-8")
PAGES = ["guide", "learn", "privacy", "terms", "support", "refund", "architecture", "notfound", "wallet", "register",
         "letter", "report", "ask", "offline"]   # ไม่รวม sky (ท้องฟ้าจริง สีต้องไม่เพี้ยน) และ safe (หน้าฉุกเฉิน ไม่แตะ)


def test_every_secondary_page_loads_the_shared_tone_once():
    for f in PAGES:
        s = (ROOT / f"static/{f}.html").read_text(encoding="utf-8")
        assert s.count('<link rel="stylesheet" href="/static/brand/brand.css">') == 1, f
        assert s.index("brand/brand.css") < s.index("</head>"), f


def test_shared_tone_is_light_touch():
    assert "pointer-events:none" in CSS                       # แสงบรรยากาศไม่บังการกด
    assert "url(" not in CSS and "animation" not in CSS and "@import" not in CSS
    assert ":where(a:not([class])){color:#ecd6a6" in CSS      # น้ำหนักศูนย์: สีลิงก์ที่หน้านั้นกำหนดเองยังชนะ


def test_login_background_is_drawn_by_code_in_the_original_composition():
    """เจ้าของโปรเจกต์: พื้นหลังหน้าเข้าสู่ระบบวาดด้วยโค้ดพร้อมตราใหม่ แต่ต้องจัดวางแบบเดิม (เนบิวลาฟ้าซ้าย ส้มขวา ตรากลาง ชื่อใต้ตรา)"""
    scene = (ROOT / "scripts/hero/scene.html").read_text(encoding="utf-8")
    assert 'src="../../static/brand/crest.svg"' in scene and "mulberry32" in scene and "a=20261112" in scene   # ดาวสุ่มแบบเลขตั้งต้นคงที่
    assert "http://" not in scene.replace("http://www.w3.org/2000/svg", "") and "https://" not in scene      # ไม่ดึงอะไรจากข้างนอก
    assert 'id="b" cx="20%"' in scene and 'id="o" cx="82%"' in scene
    from PIL import Image
    for f, size in (("hero.jpg", (2560, 1440)), ("hero_m.jpg", (1280, 720))):
        assert Image.open(ROOT / "static" / f).size == size


def test_crest_keeps_the_original_barbed_wings():
    svg = (ROOT / "static/brand/crest.svg").read_text(encoding="utf-8")
    assert 'id="barb"' in svg and svg.count('href="#barb"') >= 5
