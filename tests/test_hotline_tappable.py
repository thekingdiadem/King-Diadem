"""เบอร์สายด่วนทุกเบอร์ที่คำตอบพูดถึง ต้องแตะโทรได้บนมือถือ — เดิมศูนย์พิษวิทยา 1367 และสายด่วนอีกหลายเบอร์กดไม่ได้"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def test_every_hotline_in_answers_is_tappable():
    m = re.search(r"var HOTLINES = /\(\^\|\[\^[^\]]*\]\)\(([\d|]+)\)", _read("static/app.js"))      # สคริปต์หน้าแรกย้ายไป static/app.js
    assert m, "ไม่พบรายการเบอร์ที่แตะโทรได้"
    listed = set(m.group(1).split("|"))
    src = "".join(_read(p) for p in ("core/kernel_voice.py", "core/engine_bridge.py", "core/lang_signals.py"))
    used = set(re.findall(r"(?<![\d.,#x/:-])(1[1-9]\d{2}|19[19]|911|988|112|999)(?![\d.,%])", src))
    assert not used - listed, sorted(used - listed)
