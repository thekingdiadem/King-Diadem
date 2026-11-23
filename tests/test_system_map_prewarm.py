"""ตัวเลขสดหน้า "ระบบ" — นับไว้ล่วงหน้าตอนเปิดเซิร์ฟเวอร์ ไม่ให้คนแรกรอ 10+ วินาที"""
from pathlib import Path

SRC = Path("app.py").read_text(encoding="utf-8")


def test_live_map_prewarmed_in_background_on_startup():
    life = SRC[SRC.index("async def _lifespan("):SRC.index("def _prewarm_live_map(")]
    assert "_prewarm_live_map" in life and "daemon=True" in life
    assert life.index("Thread(") < life.index("yield")
    pw = SRC[SRC.index("def _prewarm_live_map("):][:300]
    assert "_build_live_map()" in pw and "except Exception" in pw
