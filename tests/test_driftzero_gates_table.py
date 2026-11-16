"""ตารางด่านของ DriftZero (ENGINE/driftzero_gates.py) — แต่ละบรรทัดต้องเป็นรูปแบบที่ใช้ได้จริง

เดิมด่านทั้ง 25 ด่านเป็น regex ก้อนยาวในโค้ด เพิ่มทีละรอบจนอ่านไม่ออก (หนี้เทคนิค)
ตอนนี้แยกเป็นตาราง: หนึ่งบรรทัด = หนึ่งรูปแบบ ตรวจและเพิ่มได้ทีละบรรทัด"""
import re

import pytest

from ENGINE import driftzero as D
from ENGINE.driftzero_gates import GATES_DATA

PATTERNS = [(g["id"], p) for g in GATES_DATA for p in g["patterns"]]


def test_every_gate_is_complete_and_unique():
    ids = [g["id"] for g in GATES_DATA]
    assert len(ids) == len(set(ids))
    for g in GATES_DATA:
        assert g["th"] and g["en"] and g["why_th"] and g["why_en"] and g["patterns"], g["id"]


@pytest.mark.parametrize("gid,pattern", PATTERNS)
def test_each_line_is_a_working_pattern_on_its_own(gid, pattern):
    assert pattern.strip(), gid
    re.compile(pattern, re.I)                 # บรรทัดที่พังจะบอกชัดว่าด่านไหน บรรทัดไหน


def test_no_duplicate_lines_inside_a_gate():
    for g in GATES_DATA:
        assert len(g["patterns"]) == len(set(g["patterns"])), g["id"]


def test_shared_priority_names_real_gates():
    ids = {g["id"] for g in GATES_DATA}
    assert set(D._PRIORITY) <= ids and set(D._PLAN_ONLY) <= ids


def test_engine_uses_the_table():
    assert [g[0] for g in D.GATES] == [g["id"] for g in GATES_DATA]
    for (gid, _, _, rx, _, _), g in zip(D.GATES, GATES_DATA):
        assert rx.pattern == "|".join(g["patterns"]), gid
