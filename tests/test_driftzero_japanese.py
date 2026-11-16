"""DriftZero ภาษาญี่ปุ่น (ภาษาเดียวของเว็บที่รอบ DZ11 ยังไม่ได้ลอง)"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t,gate", [("準備金を全部使って10店舗に拡大する", "E2"), ("残業代を払わないことにする", "L1"),
                                    ("顧客データを第三者に売る予定です", "S2")])
def test_core_gates_in_japanese(t, gate):
    assert gate in _stops(audit(t))


def test_japanese_sinking_and_crisis():
    assert audit("店がもうすぐ潰れそう、お金が5万円しかない")["verdict"] == "steady"
    assert audit("死にたい、会社が倒産した")["verdict"] == "urgent"


@pytest.mark.parametrize("t", ["新しい店を100万円で開く予定です", "顧客データは絶対に売らない"])
def test_japanese_ordinary_plans_pass_and_are_organisations(t):
    a = audit(t)
    assert not _stops(a) and not a["talk"]
