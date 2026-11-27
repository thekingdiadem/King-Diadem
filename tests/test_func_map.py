"""แผนผังระดับฟังก์ชัน: ตรงกับโค้ดจริง และนับเฉพาะการเรียกที่ชี้ชัด"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load():
    return json.loads((ROOT / "static/func_map.json").read_text(encoding="utf-8"))


def test_func_map_points_at_real_files_and_functions():
    fm, sm = _load(), json.loads((ROOT / "static/system_map.json").read_text(encoding="utf-8"))
    files = [f[0] for f in sm["files"]]
    assert len(fm["nodes"]) > 1000
    for fi, name, lines, kind in fm["nodes"][::97]:
        src = (ROOT / files[fi]).read_text(encoding="utf-8")
        leaf = name.split(".")[-1]
        assert f"def {leaf}" in src or f"class {leaf}" in src, (files[fi], name)


def test_edges_reference_existing_nodes():
    fm = _load()
    n = len(fm["nodes"])
    assert fm["edges"] and all(0 <= a < n and 0 <= b < n and a != b for a, b in fm["edges"])


def test_known_real_call_is_present():
    """app.py เรียก _middle_path_stats → ต้องไม่หาย (ตัวอย่างการเรียกที่มีจริงในโค้ด)"""
    fm = _load()
    names = {i: (nd[1]) for i, nd in enumerate(fm["nodes"])}
    pairs = {(names[a], names[b]) for a, b in fm["edges"]}
    assert ("_middle_path_stats", "_mp_mem") in pairs
