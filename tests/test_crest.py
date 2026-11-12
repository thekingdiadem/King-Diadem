"""ตรา KING DIADEM กลางหน้า — จุดโฟกัสของหน้าเครื่องมือและหน้าระบบ (เจ้าของโปรเจกต์: ภาพทุกภาพมีจุดโฟกัสทรงพลังตรงกลาง)
ต้องเป็นเวกเตอร์วาดด้วยโค้ด ไม่มีภาพฝัง ไม่มีสคริปต์ และไม่ขยับ (ไม่กินแรงเครื่อง)"""
import re
from pathlib import Path

from tests._front import front_page

ROOT = Path(__file__).resolve().parent.parent
SVG = (ROOT / "static/brand/crest.svg").read_text(encoding="utf-8")
PAGE = front_page()


def test_crest_is_pure_vector_and_safe():
    assert SVG.lstrip().startswith("<svg") and 'viewBox="0 0 512 512"' in SVG
    for bad in ("<script", "<image", "data:", "http://", "https://", "<animate", "onload"):
        assert bad not in SVG.replace('xmlns="http://www.w3.org/2000/svg"', ""), bad
    assert len(SVG) < 8000                                     # เล็กพอจะโหลดทันทีบนเน็ตมือถือ
    ids = set(re.findall(r'id="(\w+)"', SVG))
    used = set(re.findall(r"url\(#(\w+)\)", SVG)) | set(re.findall(r'href="#(\w+)"', SVG))
    assert used <= ids, used - ids                              # ไม่มีการอ้างสี/รูปทรงที่ไม่ได้ประกาศ


def test_crest_has_the_focal_light_drop_and_blue_gold_halo():
    assert 'id="beam"' in SVG and 'id="drop"' in SVG and 'id="halo"' in SVG
    assert 'stop-color="#3f9bff"' in SVG and 'stop-color="#ffb04a"' in SVG     # ฟ้าซ้าย ทองขวา


def test_crest_heads_tools_and_system_without_inline_handlers():
    assert PAGE.count('<div class="crest" aria-hidden="true"><img src="/static/brand/crest.svg" alt=""') == 2
    assert ".crest{" in PAGE and ".crest::after{" in PAGE
    i = PAGE.index(".crest{")
    assert "animation" not in PAGE[i:PAGE.index("ปุ่มหลัก: ขอบแสงบาง", i)]


def test_small_readability_fixes_found_in_the_page_audit():
    wallet = (ROOT / "static/wallet.html").read_text(encoding="utf-8")
    assert ".legal-links a { color:var(--gold-hi)" in wallet
    assert 'html[data-ink="dark"] .live-pill:not(.old):not(.wait){color:#0b5a45}' in PAGE
