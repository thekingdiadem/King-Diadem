"""หน้า The Universe: ท้องฟ้าจากข้างใน ไม่มีลำแสงกลาง · แนวคิด 5 ข้อของผู้สร้างเป็นบทที่พาท้องฟ้าเปลี่ยน"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")
SKY = (ROOT / "static" / "universe_sky.js").read_text(encoding="utf-8")


def test_page_has_no_center_beam():
    """เดิมฉากเมฆมีลำแสงพุ่งขึ้นกลางจอ (ทุกอย่างหันเข้าจุดเดียว) — ตอนนี้โหลดท้องฟ้าจากข้างในแทน"""
    assert "s.src = '/static/universe_sky.js';" in PAGE
    assert "s.src = '/static/galaxy_scene.js';" not in PAGE
    assert "กลุ่มดาวแห่งการตัดสินใจ" in PAGE and "ระบบสุริยะแห่งการตัดสินใจ" not in PAGE


def test_five_principles_drive_the_sky():
    """แต่ละการ์ดของแนวคิดผูกกับผลบนท้องฟ้า: ขอบฟ้า · ผู้สังเกตโคจร · กระจายเท่ากัน · ภาพลวง · แสงเดียวกัน"""
    for name in ("horizon", "orbit", "uniform", "illusion", "egoless"):
        assert f'data-sky="{name}"' in PAGE and f"{name}: function" in SKY
    assert "จักรวาลไม่ได้หมุนรอบใคร" in PAGE and "อาบแสงเดียวกับเรา" in PAGE


def test_scrolling_turns_the_viewer_not_the_sky():
    """เลื่อนหน้า = หันมองรอบตัวเกือบครบรอบ · แตะฟ้า = แสงแผ่ไปทุกดวง · ลดการเคลื่อนไหวแล้วไม่มีแสงแผ่/ซูม"""
    assert "scrollY / Math.max(1, document.documentElement.scrollHeight - H)" in SKY
    assert "sc * Math.PI * 2 * .92" in SKY
    assert "function ripple(x, y) { if (REDUCED) return;" in SKY
    assert "illusion: function () { if (!REDUCED) dolly = 0; }" in SKY


def test_sky_is_battery_friendly_and_has_fallback():
    """ไม่เกิน 90 เฟรม · หยุดเมื่อซ่อนแท็บ · เครื่องช้าลดความละเอียดเอง · ไม่มี WebGL ยังมีพื้นหลังจาก CSS"""
    assert "acc + 1e-4 < 1 / 90" in SKY and "if (document.hidden) return;" in SKY
    assert "qs *= .8" in SKY
    assert "document.documentElement.classList.add('no-sky')" in SKY and "html.no-sky body{" in PAGE


def test_thai_font_is_looped():
    """ไทยแบบไม่มีหัวทำให้ "ระบบ" อ่านเป็น "ระUU" บนมือถือ"""
    assert "Noto+Sans+Thai+Looped" in PAGE and "family=Noto+Sans+Thai:" not in PAGE


def test_creator_photo_is_removed_from_the_site():
    """เจ้าของโปรเจกต์ขอเอารูปโปรไฟล์ออกจากเว็บ — ไม่มีส่วนรูป/หัวข้อ Creator และไม่มีเส้นทาง /profile-image
    (ต่อให้บน Render ยังตั้ง KD_PROFILE_IMAGE ค้างไว้ ก็ไม่มีทางดึงรูปออกไปได้)"""
    assert not (ROOT / "static" / "king_diadem_profile.png").exists()
    for gone in ("/profile-image", "profile-section", "profile-frame", "profile-caption", ">Creator<"):
        assert gone not in PAGE, gone
    assert "private/" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_profile_image_route_is_gone(client, tmp_path, monkeypatch):
    img = tmp_path / "me.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nfake")
    monkeypatch.setenv("KD_PROFILE_IMAGE", str(img))
    r = client.get("/profile-image")
    assert r.status_code == 404 and not r.content.startswith(b"\x89PNG")
    assert "KD_PROFILE_IMAGE" not in (ROOT / "app.py").read_text(encoding="utf-8")


def test_old_cloud_scene_is_removed():
    """galaxy_scene.js ไม่มีหน้าไหนโหลดแล้ว จึงลบออก (พี่อนุญาต) — หน้ารวมฉากใช้ท้องฟ้าใหม่แทน"""
    assert not (ROOT / "static" / "galaxy_scene.js").exists()
    gallery = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "static/galaxy_scene.js" not in gallery
    assert "scripts: ['static/universe_sky.js']" in gallery
