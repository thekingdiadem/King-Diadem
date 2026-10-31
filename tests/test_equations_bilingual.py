"""สมการในหน้า "ระบบ" มีชื่อเต็มทั้งไทยและอังกฤษ — คนที่ไม่รู้สัญลักษณ์ก็อ่านออก"""
import re
from pathlib import Path
from tests._front import front_page  # noqa: E402

HTML = front_page()


def _eq_rows():
    block = HTML[HTML.index("var EQ = ["):HTML.index("];\nfunction eqRow")]
    return re.findall(r"\[('[^']*'),\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'\]", block)


def test_every_equation_has_english_and_thai_names():
    rows = _eq_rows()
    assert len(rows) == 8
    for sym, expr, src, en, th in rows:
        assert en and re.search(r"[A-Za-z]", en) and not re.search(r"[฀-๿]", en), sym
        assert th and re.search(r"[฀-๿]", th), sym


def test_master_equation_reads_in_both_languages_with_time():
    rows = {r[0].strip("'"): r for r in _eq_rows()}
    _, expr, _, en, th = rows["R"]
    assert expr == "R = (D × E × T) / C"
    assert en == "Risk = Drift × Exposure × Time ÷ Remaining Choice"           # มีเวลา (T) ด้วย
    assert th == "ความเสี่ยง = การเบี่ยงเบน × การเปิดรับ × เวลา ÷ ทางเลือกที่เหลือ"


def test_catalog_renders_both_names():
    assert '<span class="nm" lang="en"><i>\' + esc(e[3])' in HTML
    assert '<span class="nm" lang="th">\' + esc(e[4])' in HTML
