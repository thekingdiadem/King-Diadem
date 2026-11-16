"""DriftZero รอบสุ่ม 5: ความไม่ซื่อตรงที่ฟังดูเหมือนเรื่องเล็ก"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t,gate", [
    ("หัวหน้าบอกให้โกหกลูกค้าว่าของมาพรุ่งนี้ ทั้งที่ยังไม่สั่ง", "G1"),
    ("จะไล่พนักงานที่ท้องออกเพราะลาบ่อย", "L2"),
    ("จะให้แม่บ้านถือเงินสดของร้านไว้ทั้งหมดไม่ต้องลงบัญชี", "G1"),
    ("จะเก็บเงินมัดจำลูกค้าไปจ่ายหนี้เก่าก่อน", "G1"),
    ("we'll ask suppliers to pay us a fee to be listed first, without telling customers", "G1"),
    ("จะขายประกันให้ผู้สูงอายุโดยไม่อธิบายเงื่อนไข เพราะยาว", "G1"),
])
def test_dishonesty_stops(t, gate):
    assert gate in _stops(audit(t))


@pytest.mark.parametrize("t", ["เราจะไม่โกหกลูกค้าเรื่องวันส่งของ", "จะลงบัญชีทุกบิลให้ครบ", "จะให้พนักงานที่ท้องทำงานเบาลง"])
def test_the_decent_version_passes(t):
    assert not _stops(audit(t))
