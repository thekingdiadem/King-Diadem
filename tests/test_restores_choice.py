"""THE UNIVERSE THAT RESTORES CHOICE — KING DIADEM

"บางครั้งเราไม่ได้ต้องการคำตอบที่สมบูรณ์แบบ เราแค่ต้องการรู้ว่า... เรายังมีทางเลือกอยู่ในคำตอบนั้นหรือเปล่า"

ทุกคำตอบของ DriftZero — ไม่ว่าจะหยุด ฉุกเฉิน ตั้งหลัก หรือยกเลิก — ต้องเหลือทางให้คนที่พิมพ์มาอย่างน้อยหนึ่งทาง
ไม่มีคำตอบไหนที่จบแค่ "ห้าม" หรือ "ไม่ได้" แล้วปล่อยให้เขายืนอยู่ตรงนั้นคนเดียว
"""
import re

import pytest

from ENGINE.driftzero import audit, follow_up, lyla_voice

_PATH = re.compile(r"\b1[0-9]{3}\b|191|ไม่ได้แปลว่าห้ามทำ|การตัดสินใจยังเป็นของคุณ|กลับมา|โหมดปรึกษา|ตอบสั้นๆ|เริ่ม|"
                   r"(?i:doesn't mean don't|decision is still yours|come back|talk mode|start)")


def _has_choice(r: dict) -> bool:
    words = " ".join(str(x) for x in ((r.get("lyla") or {}).get("th"), (r.get("summary") or {}).get("th")))
    return bool(r.get("steps") or r.get("asks") or r.get("talk") or _PATH.search(words))


CASES = [
    "อยากตายแล้ว ธุรกิจเจ๊ง",                                         # ฉุกเฉิน
    "ธุรกิจกำลังจะพังขาดทุนต่อเนื่อง เงินเหลือ3000 กู้ใครก็ไม่ได้แล้วกำลังล้ม",  # ตั้งหลักก่อน
    "เงินหมดแล้ว ร้านไปต่อไม่ไหว ไม่รู้จะทำยังไง",
    "ไม่ไหวแล้ว",                                                    # เรื่องใจ
    "มีคนชวนลงทุนคริปโต การันตีกำไรวันละ 2% จะเอาเงินเก็บทั้งหมดไปลง",  # มิจฉาชีพ
    "จะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้",                         # หยุด
    "ผู้รับเหมาจะไม่ใส่ราวกันตกที่ชั้น 8 เพราะงานต้องเสร็จไว",
    "จะเปิดร้านกาแฟสาขาสองใช้เงิน 5 แสน",                               # ถามต่อ
    "what does driftzero do",                                       # วิธีใช้
]


@pytest.mark.parametrize("t", CASES)
def test_every_answer_leaves_a_way_forward(t):
    assert _has_choice(lyla_voice(audit(t))), t


def test_follow_ups_leave_a_way_forward_too():
    a = audit("จะเปิดร้านกาแฟสาขาสองใช้เงิน 5 แสน")
    keys = [q["key"] for q in a["asks"]]
    for answer in ("ไม่รู้", "ขอยกเลิก ไม่ทำแล้ว", "อยากตายเลย",
                   "1. ถ้าพลาดเสียเงินลงทุน 2. ขั้นต่ำ 2 แสน 3. วันละ 1500 4. ผมเอง"):
        assert _has_choice(lyla_voice(follow_up(a["text"], keys, answer))), answer
    s = audit("ร้านจะเจ๊งแล้ว เหลือเงิน 1 หมื่น")
    for answer in ("วันละ 800", "ค่าเช่า 15000 ต้องจ่ายสิ้นเดือน", "ไม่รู้ ไม่ได้จด"):
        assert _has_choice(lyla_voice(follow_up(s["text"], [q["key"] for q in s["asks"]], answer))), answer


def test_a_stop_is_never_just_a_no():
    r = lyla_voice(audit("จะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้"))
    assert "ไม่ได้แปลว่าห้ามทำ" in r["lyla"]["th"]
