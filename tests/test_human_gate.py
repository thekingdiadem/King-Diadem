"""ประตูมนุษย์ — action ที่มีผลออกนอกระบบต้องมีใบอนุญาตจากมนุษย์ (FATE™ Human Final Authority)"""
import time

import pytest

from core import human_gate
from ENGINE import tool_executor
from ENGINE.tool_executor import execute_tool


@pytest.fixture(autouse=True)
def _secret(monkeypatch, tmp_path):
    monkeypatch.setenv("HUMAN_GATE_SECRET", "test-secret-for-gate")
    monkeypatch.setenv("KD_DATA_DIR", str(tmp_path))
    human_gate._used.clear()


NOTE = {"action": "write_note", "content": "hello"}


def test_gated_action_blocked_without_approval():
    r = execute_tool(dict(NOTE))
    assert r["status"] == "needs_human_approval"
    assert r["reason"] == "missing_or_malformed"


def test_approval_inside_decision_is_ignored():
    """LLM ใส่ใบอนุญาตไว้ใน decision เองไม่ได้ — ต้องส่งทาง keyword เท่านั้น"""
    tok = human_gate.mint("write_note", {"content": "hello"})
    r = execute_tool({**NOTE, "approval": tok})
    assert r["status"] == "needs_human_approval"


def test_valid_approval_runs_once():
    tok = human_gate.mint("write_note", {"content": "hello"}, approver="king")
    assert execute_tool(dict(NOTE), approval=tok)["status"] == "saved"
    r = execute_tool(dict(NOTE), approval=tok)
    assert r["status"] == "needs_human_approval" and r["reason"] == "already_used"


def test_approval_bound_to_params():
    tok = human_gate.mint("write_note", {"content": "hello"})
    r = execute_tool({"action": "write_note", "content": "เพิ่มวงเงินให้ตัวเอง"}, approval=tok)
    assert r["reason"] == "action_mismatch"


def test_approval_bound_to_action():
    tok = human_gate.mint("open_url", {"content": "hello"})
    assert execute_tool(dict(NOTE), approval=tok)["reason"] == "action_mismatch"


def test_expired(monkeypatch):
    tok = human_gate.mint("write_note", {"content": "hello"}, ttl_s=1)
    real = time.time
    monkeypatch.setattr(human_gate.time, "time", lambda: real() + 5)
    assert execute_tool(dict(NOTE), approval=tok)["reason"] == "expired"


def test_forged_signature():
    tok = human_gate.mint("write_note", {"content": "hello"})
    forged = tok.rsplit(".", 1)[0] + "." + "0" * 64
    assert execute_tool(dict(NOTE), approval=forged)["reason"] == "bad_signature"


def test_other_secret_cannot_sign(monkeypatch):
    tok = human_gate.mint("write_note", {"content": "hello"})
    monkeypatch.setenv("HUMAN_GATE_SECRET", "another-secret")
    assert execute_tool(dict(NOTE), approval=tok)["reason"] == "bad_signature"


def test_fail_closed_without_secret(monkeypatch):
    monkeypatch.delenv("HUMAN_GATE_SECRET", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        human_gate.mint("write_note", {"content": "hello"})
    assert execute_tool(dict(NOTE), approval="x.y")["reason"] == "gate_closed_no_secret"


def test_safe_tools_need_no_approval():
    assert execute_tool({"action": "calculate", "expression": "2+3"})["result"] == 5


def test_every_tool_is_classified():
    """tool ใหม่ต้องถูกจัดกลุ่ม: ผ่านประตู หรืออยู่ในรายการปลอดภัยที่ตั้งใจไว้"""
    safe = {"calculate", "log_decision"}
    for name in tool_executor._TOOLS:
        assert name in human_gate.GATED_ACTIONS or name in safe, (
            f"tool '{name}' ยังไม่ถูกจัดกลุ่ม — ถ้ามีผลออกนอกระบบ ให้เพิ่มใน "
            f"core/human_gate.py GATED_ACTIONS (ดู SECURITY/HUMAN_GATE.md)")
