"""หน้าเว็บบนมือถือ: ฟอนต์ไทยอ่านออก · ปุ่มใหญ่พอ · เบอร์สายด่วนกดโทรได้"""
import pathlib
import re

PAGE = (pathlib.Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def test_thai_font_is_looped():
    """ไทยแบบไม่มีหัวทำให้ "ระบบ" อ่านเป็น "ระUU" บนมือถือ"""
    assert "Noto+Sans+Thai+Looped" in PAGE
    for var in ("--f-sans", "--f-mono", "--f-title"):
        assert re.search(var + r':[^;]*"Noto Sans Thai Looped"', PAGE), var


def test_mobile_touch_targets():
    block = PAGE[PAGE.index("ปุ่มต้องใหญ่พอให้นิ้วกด"):]
    assert re.search(r"\.chip\{height:3[6-9]px", block)
    assert re.search(r"\.seg button\{height:3[4-9]px", block)


def test_hotlines_become_tel_links():
    assert "function telify" in PAGE and "telify(key === 'COUNCIL'" in PAGE
    pat = re.search(r"var HOTLINES = (/.*/g);", PAGE).group(1)
    assert "191" in pat and "1669" in pat and "บาท" in pat
