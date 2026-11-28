"""ความปลอดภัยต่อสายตา: ฉากบิ๊กแบงไม่สั่นจอ และแสงวาบตอนเริ่มไม่จ้าเต็มจอ"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_big_bang_never_shakes_screen():
    js = (ROOT / "static/big_bang.js").read_text(encoding="utf-8")
    assert not re.search(r"shake\s*=\s*(?:[1-9]|Math\.max)", js)
