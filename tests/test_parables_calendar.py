"""ข้อคิดจากปฏิทินวันพระ — LYLA หยิบมาใช้ตามสถานการณ์ ไม่แปะทุกข้อความ"""
from core.parables import select_parable


def test_tired_gets_breath():
    assert select_parable("ช่วงนี้เหนื่อยล้ามาก หมดแรงไปหมด")["name"] == "หลักลมหายใจ"


def test_cannot_resist_gets_restraint():
    assert select_parable("ห้ามใจไม่ได้ ใช้เงินเกินตัวทุกเดือน")["name"] == "หลักดูแลใจ"


def test_life_down_gets_journey():
    assert select_parable("ชีวิตตกต่ำมาก เคยดีกว่านี้")["name"] == "หลักการเดินทาง"


def test_scammed_gets_avijja_without_blame():
    p = select_parable("โดนหลอกโอนเงินไป รู้งี้ไม่เชื่อ")
    assert p["name"] == "อวิชชา" and "ไม่ได้แปลว่าคนที่พลาดเป็นคนผิด" in p["text"]


def test_plain_message_gets_nothing():
    assert select_parable("ขอสูตรต้มยำหน่อย") is None
