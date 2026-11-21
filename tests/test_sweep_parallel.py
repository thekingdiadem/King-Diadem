"""sweep_all แบ่งชุด urgent เป็นส่วนๆ ให้หลายแกนช่วยกันรัน — ทุกส่วนรวมกันต้องครบทุกข้อความ ไม่ตกหล่นและไม่ซ้ำ"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))
import sweep_all  # noqa: E402


def test_urgent_parts_cover_every_case_once(monkeypatch):
    seen = []
    monkeypatch.setattr(sweep_all, "assess", lambda t: (seen.append(t), {"text_risk": 0})[1])
    monkeypatch.setattr(sweep_all, "compose", lambda t: "")
    total = None
    for i in range(4):
        total, bad = sweep_all.urgent(40, i, 4)
    assert len(seen) == total == 40 and len(set(seen)) == 40


def test_parallel_and_serial_report_the_same():
    assert sweep_all.main(["intl", "en_scam", "--sample", "30"]) == sweep_all.main(["intl", "en_scam", "--sample", "30", "--serial"]) == 0
