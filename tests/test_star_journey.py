"""ดาวเกิดแบบเดินทางในหน้าจักรวาล: เล่นครั้งเดียวต่อดาว · ลดการเคลื่อนไหวแล้วข้าม · 7 จุดตามขั้นจริง"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "static/app.js").read_text(encoding="utf-8")


def test_plays_once_per_star():
    body = JS[JS.index("function journey(now){"):JS.index("function drawMySky(now){")]
    assert "n.ts <= seenTs()" in body and "markSeen(" in body


def test_reduced_motion_skips_animation():
    body = JS[JS.index("function journey(now){"):JS.index("function drawMySky(now){")]
    assert "if(REDUCED){ markSeen(n.ts); return null; }" in body


def test_seven_real_stages():
    from core.progress import STAGES
    body = JS[JS.index("function journey(now){"):JS.index("function drawMySky(now){")]
    assert len(STAGES) == 7 and "s2 <= 7" in body
