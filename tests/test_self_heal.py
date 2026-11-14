"""ระบบดูแลตัวเอง: ส่วนที่พังถูกพัก ผู้ใช้ยังได้คำตอบ และเปิดคืนเองเมื่อหาย"""
import pytest
from core import self_heal as H


@pytest.fixture(autouse=True)
def _clean():
    H.reset()
    yield
    H.reset()


def test_guard_returns_none_and_trips_after_limit():
    def boom(*a, **k):
        raise RuntimeError("พังจำลอง")
    for _ in range(H.FAIL_LIMIT):
        assert H.guard("x", boom) is None
    assert not H.enabled("x")
    assert H.status()["parts"]["x"]["last_error"].startswith("RuntimeError")


def test_reopens_by_itself_after_cooldown(monkeypatch):
    def boom():
        raise ValueError
    for _ in range(H.FAIL_LIMIT):
        H.guard("y", boom)
    assert not H.enabled("y")
    real = H.time.time
    monkeypatch.setattr(H.time, "time", lambda: real() + H.COOLDOWN_S + 1)
    assert H.enabled("y")                     # ครบเวลาพัก = ลองใหม่เอง
    assert H.guard("y", lambda: "ok") == "ok"
    assert H.enabled("y") and not H.status()["parts"]["y"]["retry_in_s"]


def test_broken_module_does_not_break_reply(monkeypatch):
    """ถ้าตัวอ่านค่าเลือดพังหลังอัปเดต ผู้ใช้ยังได้คำตอบ ไม่ใช่ error"""
    from core import lab_values
    from core.kernel_voice import compose
    def boom(*a, **k):
        raise KeyError("bad update")
    monkeypatch.setattr(lab_values, "read", boom)
    out = compose("ผลตรวจ LDL 190 น้ำตาล 130", footer=False)
    assert out and "— LYLA" in out


def test_crisis_still_gets_hotline_when_parts_broken(monkeypatch):
    from core import problem_lens, human_needs
    from core.kernel_voice import compose
    def boom(*a, **k):
        raise RuntimeError
    monkeypatch.setattr(problem_lens, "find", boom)
    monkeypatch.setattr(human_needs, "adapt_main", boom)
    assert "1323" in compose("อยากตาย ไม่ไหวแล้ว", footer=False)


def test_check_all_passes_on_healthy_system():
    r = H.check_all()
    assert r["ok"], r["failed"]


def test_check_all_detects_and_benches_broken_part(monkeypatch):
    from core import drug_pairs
    monkeypatch.setattr(drug_pairs, "reply", lambda *a, **k: None)
    r = H.check_all()
    assert "drug_pairs" in r["failed"] and not H.enabled("drug_pairs")


def test_health_exposes_self_heal(client):
    assert "self_heal" in client.get("/health").json()
