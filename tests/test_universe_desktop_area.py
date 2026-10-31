"""กลุ่มดาวของฉันต้องวางดาวในกรอบหน้าจักรวาล ไม่ใช่ทั้งจอ

จอคอมมีแถบเมนูซ้ายทับ canvas อยู่ ถ้าคิดพื้นที่จาก 0..W ดาวและเส้นจะไปซ่อนใต้เมนู
(เจ้าของโปรเจกต์ถ่ายรูปจากแลปท็อปมาให้ดู)
"""
import re
from pathlib import Path

SRC = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def _fn(name):
    m = re.search(r"function " + name + r"\(\)\{(.*?)\n  \}", SRC, re.S)
    assert m, name + " not found"
    return m.group(1)


def test_my_area_uses_universe_view_rect():
    body = _fn("myArea")
    assert "#view-universe'" in body and ".left" in body and ".right" in body
    assert "l: 34," not in body, "ขอบซ้ายต้องเริ่มจากกรอบหน้าจักรวาล ไม่ใช่ขอบจอ"


def test_layout_cache_key_tracks_horizontal_bounds():
    body = _fn("layoutMine")
    assert "A.l" in body.split("MY.key === k")[0] and "A.r" in body.split("MY.key === k")[0]
