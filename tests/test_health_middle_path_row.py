"""หน้า "ระบบ" ต้องโชว์ผลตัวตรวจทางสายกลางจาก /health ว่าเอียงไปฝั่งไหนบ่อยกว่า"""
from pathlib import Path

from tests._front import front_page

ROOT = Path(__file__).resolve().parent.parent


def test_health_rows_include_middle_path():
    page = front_page()
    assert "['middle_path','ทางสายกลาง','mp']" in page
    assert "r[2] === 'mp'" in page and "v.upside" in page and "v.constraint" in page


def test_middle_path_labels_translated():
    keys = ["ทางสายกลาง", "ตรวจ {n} · เติมด้านเสีย {u} · เติมทางไปต่อ {c}"]
    main = (ROOT / "static/i18n.js").read_text(encoding="utf-8")
    for k in keys:
        assert f"'{k}':" in main
    for lang in ("es", "ko", "vi", "zh"):
        pack = (ROOT / f"static/i18n/{lang}.js").read_text(encoding="utf-8")
        for k in keys:
            assert f'"{k}":' in pack, (lang, k)


def test_health_endpoint_exposes_middle_path_counts():
    from app import _middle_path_stats
    s = _middle_path_stats()
    assert s is not None and {"checked", "upside", "constraint"} <= set(s)
