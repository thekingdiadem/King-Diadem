"""เส้นทางแสงสดในฟองรอคำตอบ: ใช้ขั้นจริงจากเซิร์ฟเวอร์ครบ 7 ขั้น และเคารพการลดการเคลื่อนไหว"""
from pathlib import Path

from core.progress import STAGES
from tests._front import front_page

ROOT = Path(__file__).resolve().parent.parent


def test_live_path_uses_real_server_stages():
    js = front_page()
    i = js.index("var KEYS = ["); keys = js[i:js.index("];", i)]
    for st in STAGES:
        assert "'" + st + "'" in keys, st


def test_live_path_respects_reduced_motion():
    css = (ROOT / "static/app.css").read_text(encoding="utf-8")
    assert ".live-path" in css and "prefers-reduced-motion: reduce){.live-path" in css
