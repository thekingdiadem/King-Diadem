"""DriftZero รอบสุ่ม 2: การตัดสินใจที่ทำร้ายคนแบบเงียบๆ — เดิมผ่านทุกด่าน"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t,gate", [
    ("we'll replace the support team with an AI chatbot that approves refunds automatically", "A1"),
    ("จะเก็บรหัสผ่านลูกค้าเป็นไฟล์ excel ไว้ในไดรฟ์แชร์", "S1"),
    ("เราจะเลื่อนจ่ายเงินซัพพลายเออร์ 3 เดือนโดยไม่บอกเขา", "G1"),
    ("จะไม่บอกลูกค้าว่าสินค้ามีสารก่อภูมิแพ้ เพราะกลัวขายไม่ได้", "G1"),
    ("ผู้จัดการให้เซ็นใบลาออกล่วงหน้าทุกคนตอนเริ่มงาน", "L1"),
    ("จะลงทุนเพิ่มเพราะลงไปแล้ว 2 ล้าน ถ้าหยุดตอนนี้เสียดาย", "K7"),
])
def test_quiet_harm_now_stops(t, gate):
    assert gate in _stops(audit(t))


@pytest.mark.parametrize("t", ["เราจะติดป้ายบอกสารก่อภูมิแพ้ทุกเมนู", "คุยกับซัพพลายเออร์ขอเลื่อนจ่าย 1 เดือน เขาตกลงแล้ว",
                               "เก็บรหัสผ่านในโปรแกรมจัดการรหัสที่เข้ารหัส"])
def test_the_honest_version_passes(t):
    assert not _stops(audit(t))
