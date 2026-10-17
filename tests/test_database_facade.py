"""ระบบตัดสินใจชุดเก่า (ENGINE/brain · decision · intent · risk · intervention_engine) และ core/database.py
ย้ายไป legacy/ แล้วลบออกจาก repo (พี่อนุญาต · ดูย้อนหลังได้ใน git) — กันไม่ให้ใครเอากลับมาแล้วได้ pipeline หรือฐานข้อมูลชุดที่สองซ้อนกับของจริง"""
import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MOVED = ["ENGINE/brain.py", "ENGINE/decision.py", "ENGINE/intent.py", "ENGINE/risk.py",
         "ENGINE/intervention_engine.py", "core/database.py"]


@pytest.mark.parametrize("path", MOVED)
def test_old_second_pipeline_is_gone(path):
    assert not (ROOT / path).exists()
    with pytest.raises(ImportError):
        importlib.import_module(path[:-3].replace("/", "."))


def test_app_still_uses_the_one_real_database_and_pipeline():
    from DATABASE import db
    from ENGINE.decision_engine import run_decision
    assert db.DB_PATH and callable(run_decision)
