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
    assert len(SVG) < 10000                                    # เล็กพอจะโหลดทันทีบนเน็ตมือถือ (เพิ่มจาก 8000 เมื่อใส่หนามปีกทรงเดิมกลับมา)
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


def test_crest_is_symmetric_jewellery_not_cartoon():
    """เจ้าของโปรเจกต์: รุ่นก่อน "ดูเป็นการ์ตูน" — รุ่นนี้ครึ่งซ้ายคือภาพสะท้อนของครึ่งขวาทุกพิกัด ขอบหน้าปัดมีขีด 72 + 12 และเส้นขอบบาง"""
    assert SVG.count('transform="translate(512 0) scale(-1 1)"') >= 3
    assert 'stroke-dasharray="1 16.889"' in SVG and 'stroke-dasharray="1.6 105.738"' in SVG
    import math
    c = 2 * math.pi * 205
    assert abs(c / 72 - (1 + 16.889)) < .01 and abs(c / 12 - (1.6 + 105.738)) < .01     # ขีดลงตัวพอดีรอบวง ไม่มีรอยต่อ
    assert 'stroke-width="9"' not in SVG                       # ไม่มีเส้นขอบหนาแบบการ์ตูน
    assert "M256 104 L275 252 L256 372 L237 252 Z" in SVG       # แกนกลางสมมาตรรอบ x = 256 (275 − 256 = 256 − 237)


def test_wordmark_is_optically_centred():
    assert PAGE.count('<span class="crest-word" data-i18n-skip>KING DIADEM</span>') == 2
    assert "letter-spacing:.56em;padding-left:.56em" in PAGE    # ชดเชยช่องไฟหลังตัวสุดท้าย คำจึงอยู่กึ่งกลางพอดี


def test_home_scene_is_quiet():
    """หน้าแรก "ดูเลอะเทอะ": ไม่มีป้ายชื่อดาวเคราะห์/ดาวลูกไก่ ป้ายเส้นทางเหลือเฉพาะที่เลือก วงโคจรอื่นจางลง"""
    assert "var QUIET = true;" in PAGE
    assert "if(drew && !CINEMA.on && !QUIET) drawBodyLabels(" in PAGE
    assert "if(spot && !CINEMA.on && (on || !QUIET)){" in PAGE
    assert "if(!CINEMA.on && !QUIET){ ctx.globalAlpha = A * .8; ctx.fillText(_t(l[0]), x, y); }" in PAGE


def test_eternal_drop_plays_once_and_respects_reduced_motion():
    """แกนแสงลงจากฟ้าที่ตรา แล้วหยดแสงกระจายเป็นวงคลื่น — จากภาพอ้างอิงของเจ้าของโปรเจกต์ (Cosmic Axis → Crown Kernel)"""
    assert PAGE.count('<b class="axis"></b><s class="ripple"></s>') == 2
    assert "animation:kd-axis 2.2s" in PAGE and "infinite" not in PAGE[PAGE.index("Eternal Drop"):PAGE.index("kd-crest-lit{")]
    assert "@media (prefers-reduced-motion:reduce){ .crest .axis,.crest .ripple::before,.crest .ripple::after,.crest img{animation:none}" in PAGE
    assert "html.kd-calm .crest .axis,html.kd-calm .crest .ripple,html.kd-calm .crest img{animation:none}" in PAGE
