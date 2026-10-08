"""หน้าเว็บ: ป้ายตอนสภากำลังคิดต้องตรงกับสภาจริง และปุ่มธีมฟ้ายามเย็นยังกดง่ายบนมือถือ"""
import re
from pathlib import Path

from AI.council_engine import COUNCIL_SIZE

HTML = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def test_thinking_label_matches_council_size():
    # เดิมขึ้น "สภา 5 เสียง" ระหว่างรอ ทั้งที่สภามี 6 เสียงแล้ว
    live = re.sub(r'<script type="application/json" id="system-map">.*?</script>', "", HTML, flags=re.S)  # ประวัติการแก้
    labels = set(re.findall(r"สภา (\d) เสียง", live))
    assert labels == {str(COUNCIL_SIZE)}


def test_tab_icons_alternate_cool_and_warm():
    tabbar = re.search(r'<nav id="tabbar".*?</nav>', HTML, re.S).group(0)
    assert re.findall(r'<span class="i">(.)</span>', tabbar) == ["☾", "✦", "☁", "☼"]
    assert "#tabbar button:nth-child(odd) .i" in HTML and "#tabbar button:nth-child(even) .i" in HTML


def test_dusk_theme_respects_reduced_motion():
    assert "@keyframes twinkle" in HTML
    assert re.search(r"prefers-reduced-motion:reduce\)\{\*\{animation:none!important", HTML)
