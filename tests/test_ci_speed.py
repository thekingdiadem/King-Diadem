"""CI เคยช้าจนเกือบครึ่งชั่วโมง เพราะรัน pytest สองรอบต่อกันแบบแกนเดียว แล้วค่อย sweep
ตอนนี้แยกเป็นงานคู่ขนาน และ pytest ใช้ทุกแกน (-n auto) — เทสต์นี้กันไม่ให้ใครเผลอย้อนกลับ"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _ci():
    return yaml.safe_load((ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8"))


def test_pytest_uses_all_cores_and_both_databases():
    job = _ci()["jobs"]["pytest"]
    assert set(job["strategy"]["matrix"]["db"]) == {"local", "hrana-fake"}
    runs = " ".join(step.get("run", "") for step in job["steps"])
    assert "-n auto" in runs
    assert "pytest-xdist" in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")


def test_sweep_runs_in_its_own_parallel_job():
    jobs = _ci()["jobs"]
    runs = " ".join(step.get("run", "") for step in jobs["sweep"]["steps"])
    assert "sweep_all.py" in runs and "blind_score.py" in runs and "pip-audit" in runs
    assert "needs" not in jobs["sweep"]   # ไม่ต้องรอ pytest
