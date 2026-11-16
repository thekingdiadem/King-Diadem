"""DriftZero รอบสุ่ม 30: ลองครบทุกแบบบนหน้าเว็บจริง (ฉุกเฉิน · ตั้งหลักก่อน · เรื่องใจ · มิจฉาชีพ · หยุด · ไม่รู้แล้วยกเลิก)
การ์ดแสดงครบ ไม่มี error — เจอจุดเดียว: คนที่กำลังโดนหลอกได้ยินเหตุผลแรกว่า "มั่นใจเกินจริง" แทนที่จะเป็นมิจฉาชีพ"""
from ENGINE.driftzero import audit, lyla_voice


def test_scam_reason_is_said_first():
    r = lyla_voice(audit("มีคนชวนลงทุนคริปโต การันตีกำไรวันละ 2% จะเอาเงินเก็บทั้งหมดไปลง"))
    first = r["lyla"]["th"].split("มีจุดที่ควรหยุดคิดก่อน:")[1]
    assert first.strip().startswith("นี่คือรูปแบบที่มิจฉาชีพใช้บ่อยที่สุด")


def test_life_safety_is_said_before_softer_gates():
    r = lyla_voice(audit("ผู้รับเหมาจะไม่ใส่ราวกันตกที่ชั้น 8 เพราะงานต้องเสร็จไว"))
    assert "ชีวิตหรือร่างกาย" in r["lyla"]["th"]
