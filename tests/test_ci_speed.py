"""CI เคยช้าจนเกือบครึ่งชั่วโมง เพราะรัน pytest สองรอบต่อกันแบบแกนเดียว แล้วค่อย sweep
ตอนนี้แยกเป็นงานคู่ขนาน และ pytest ใช้ทุกแกน (-n auto) — เทสต์นี้กันไม่ให้ใครเผลอย้อนกลับ
(อ่านเป็นข้อความธรรมดา ไม่ใช้ yaml เพราะเครื่อง CI ไม่ได้ติดตั้งไว้)

เทสต์ที่วัดความเร็วใช้ time.process_time() (เวลา CPU ของตัวเอง) แทนนาฬิกาจริง
เพราะตอนรันหลายแกนพร้อมกัน นาฬิกาจริงจะนับเวลาที่รอเทสต์อื่นใช้ CPU ด้วย"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CI = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")


def test_pytest_uses_all_cores_and_both_databases():
    assert "-n auto" in CI
    assert "db: [local, hrana-fake]" in CI
    assert "pytest-xdist" in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")


def test_sweep_runs_in_its_own_parallel_job():
    sweep = CI.split("\n  sweep:\n", 1)[1]
    assert "sweep_all.py" in sweep and "blind_score.py" in sweep and "pip-audit" in sweep
    assert "needs:" not in sweep   # ไม่ต้องรอ pytest


def test_speed_tests_measure_cpu_time_not_wall_clock():
    for name in ("test_random_round87.py", "test_sweep_round21.py", "test_driftzero_round22.py", "test_kernel_speed.py"):
        assert "perf_counter" not in (ROOT / "tests" / name).read_text(encoding="utf-8"), name
