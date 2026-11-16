"""DriftZero รอบสุ่ม 8: LYLA เล่าผลด้วยตัวเลขและเหตุผลจริง ไม่ใช่ชื่อด่าน"""
from ENGINE.driftzero import audit, follow_up, lyla_voice


def test_pass_says_how_far_above_the_floor():
    a = audit("จะเปิดสาขา 2 ใช้เงิน 8 แสน มีเงินสด 1.2 ล้าน ขั้นต่ำต้องเหลือ 3 แสน")
    r = lyla_voice(follow_up(a["text"], [q["key"] for q in a["asks"]], "1. ถ้าพลาดเสียเงินลงทุน 2. ค่าเช่าวันละ 2000 3. ผมเอง"))
    assert r["verdict"] == "pass" and "400,000" in r["lyla"]["th"] and "100,000" in r["lyla"]["th"]


def test_stop_explains_the_reason_not_the_gate_name():
    r = lyla_voice(audit("จะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้"))
    assert "Waterline —" not in r["lyla"]["th"] and "เส้นขั้นต่ำ" in r["lyla"]["th"]


def test_several_stops_mention_the_rest():
    r = lyla_voice(audit("บริษัทจะไม่จ่ายค่าโอที และจะเก็บรหัสผ่านลูกค้าใน excel"))
    assert "อีก 1 จุด" in r["lyla"]["th"]
