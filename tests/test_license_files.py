"""LICENSE ต้องเป็น AGPL-3.0 ตัวเต็ม — เดิมเป็นประกาศสั้น 52 บรรทัด GitHub เลยขึ้น license ว่า Other"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_license_is_full_agpl_text():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "GNU AFFERO GENERAL PUBLIC LICENSE" in text
    assert "TERMS AND CONDITIONS" in text and "END OF TERMS AND CONDITIONS" in text
    assert len(text.splitlines()) > 600


def test_notice_keeps_creator_copyright():
    text = (ROOT / "NOTICE").read_text(encoding="utf-8")
    assert "Copyright (C) 2026 Nithikorn Bunsrang" in text
    assert "@thekingdiadem" in text


def test_readme_links_license_and_notice():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "](LICENSE)" in text and "](NOTICE)" in text
    assert "Render ปิดอยู่" not in text
