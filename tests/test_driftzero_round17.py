"""DriftZero รอบสุ่ม 17: ลองบนหน้าเว็บจริงทีละรอบ — ใช้ 5 แสน มี 6 แสน ต้องเหลืออย่างน้อย 2 แสน

เดิมได้ "ผ่านทุกด่าน" ทั้งที่ใช้แล้วเหลือแค่ 1 แสน ต่ำกว่าเส้นขั้นต่ำ
เพราะคำว่า "ต้อง*เหลือ*อย่างน้อย 2 แสน" ถูกอ่านเป็นเงินที่มีด้วย แล้วคำตอบ "มีเงินสด 6 แสน" ที่ตอบทีหลังไม่ถูกใช้เลย
"""
from ENGINE.driftzero import audit, follow_up, lyla_voice
from ENGINE.waterline_gauge import gauge


def _keys(a):
    return [q["key"] for q in a["asks"]]


def test_cash_answered_later_is_used_and_the_plan_stops():
    a = audit("จะเปิดร้านกาแฟสาขาสองใช้เงิน 5 แสน")
    r = follow_up(a["text"], _keys(a), "ถ้าพลาดก็เสียเงินเก็บ ต้องเหลืออย่างน้อย 2 แสน เงินออกวันละ 1500 ผมรับผิดชอบเอง")
    r = lyla_voice(follow_up(r["text"], _keys(r), "ตอนนี้มีเงินสด 6 แสน"))
    assert r["verdict"] == "stop" and r["waterline"]["current"] == 600000 and r["waterline"]["level"] == "below"
    assert "100,000" in r["lyla"]["th"] and "Below Water" not in r["lyla"]["th"]


def test_floor_words_are_not_read_as_cash_on_hand():
    assert gauge("ต้องเหลืออย่างน้อย 2 แสน ตอนนี้มีเงิน 6 แสน")["current"] == 600000
