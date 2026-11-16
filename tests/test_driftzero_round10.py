"""DriftZero รอบสุ่ม 10: บทสนทนาหลายรอบ — ชีวิตมาก่อน · ไม่รู้ = ข้าม · ยกเลิกได้ · คำนวณบิลที่ต้องจ่าย"""
from ENGINE.driftzero import audit, follow_up, lyla_voice

SINK = "ร้านจะเจ๊งแล้ว เหลือเงิน 1 หมื่น"
PLAN = "จะเปิดร้านกาแฟสาขาสองใช้เงิน 5 แสน"


def _keys(a):
    return [q["key"] for q in a["asks"]]


def test_crisis_in_a_follow_up_answer_gets_emergency_help():
    # เดิมตอนอยู่ใน "ตั้งหลักก่อน" แล้วตอบว่า "อยากตายเลย" ยังได้คำแนะนำเรื่องเงินต่อ
    a = audit(SINK)
    assert follow_up(a["text"], _keys(a), "อยากตายเลย")["verdict"] == "urgent"
    b = audit(PLAN)
    assert follow_up(b["text"], _keys(b), "อยากตายแล้ว ไม่ไหว")["verdict"] == "urgent"


def test_dont_know_skips_instead_of_looping():
    r = audit(PLAN)
    seen = []
    for _ in range(6):
        r = follow_up(r["text"], _keys(r), "ไม่รู้")
        seen.append(len(r["asks"]))
    assert seen[-1] == 0 and seen == sorted(seen, reverse=True)
    v = lyla_voice(r)
    assert "ยังไม่รู้" in v["lyla"]["th"]                         # ผ่าน แต่บอกตรงๆ ว่ายังไม่แน่นอน


def test_cancel_is_respected():
    a = audit(PLAN)
    r = lyla_voice(follow_up(a["text"], _keys(a), "ขอยกเลิก ไม่ทำแล้ว"))
    assert r.get("cancelled") and not r["asks"] and "ไม่ทำ" in r["lyla"]["th"]


def test_a_bill_due_is_subtracted_from_what_is_left():
    a = audit(SINK)
    r = follow_up(a["text"], _keys(a), "ค่าเช่า 6000 ต้องจ่ายสิ้นเดือน")
    assert r["after_due"] == 4000 and "4,000" in r["summary"]["th"]
    r = follow_up(a["text"], _keys(a), "ค่าเช่า 15000 ต้องจ่ายสิ้นเดือน")
    assert r["after_due"] == -5000 and "ขอแบ่งจ่าย" in r["summary"]["th"]
