"""ข้อความของผู้ใช้ต้องไม่ถูกพิมพ์ลง log ของเซิร์ฟเวอร์ (Render เก็บ log ไว้ และคนที่ดู log ไม่ควรเห็นเรื่องส่วนตัวของผู้ใช้)
เดิม DRIFT ALERT พิมพ์ 60 ตัวอักษรแรกของข้อความ — ซึ่งอาจเป็นเรื่องทำร้ายตัวเองหรือถูกทำร้าย"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER_TEXT = {"user_input", "input_text", "message", "raw_input", "situation"}
LIVE = ["app.py", "report_engine.py", *map(str, (ROOT / "core").glob("*.py")), *map(str, (ROOT / "ENGINE").glob("*.py")),
        *map(str, (ROOT / "AI").glob("*.py")), *map(str, (ROOT / "AI_KERNEL").glob("*.py")), *map(str, (ROOT / "DOMAINS").glob("*.py"))]


def _prints_user_text(path):
    tree = ast.parse(Path(ROOT, path).read_text(encoding="utf-8"))
    hits = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "print":
            names = {x.id for a in n.args for x in ast.walk(a) if isinstance(x, ast.Name)}
            if names & USER_TEXT:
                hits.append((path, n.lineno, sorted(names & USER_TEXT)))
    return hits


def test_live_code_never_prints_user_text():
    hits = [h for p in LIVE for h in _prints_user_text(p)]
    assert not hits, hits


def test_drift_alert_logs_route_only():
    src = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'print(f"⚠ DRIFT ALERT | route={route}")' in src
