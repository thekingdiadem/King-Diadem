"""ความเร็วของตัวจับหลักกับข้อความยาว

เดิมข้อความยาว 4,000 ตัวอักษรใช้เวลาเกือบ 2 วินาที (กฎ 3 ตัวใช้ lookahead ที่ไล่สแกนทั้งข้อความซ้ำจากทุกตำแหน่ง
และข้อความซ้ำยาวๆ อย่าง "ไม่ไม่ไม่…" ทำให้กฎอื่นช้าตาม) — คนที่เล่าเรื่องยาวต้องไม่ต้องรอนาน
"""
import random
import time

from core.kernel_voice import assess
from core import thai_signals as T

random.seed(1)
_PARTS = ["วันนี้ไปทำงาน", "หัวหน้าด่า", "กลับบ้านดึก", "แฟนไม่คุยด้วย", "เงินเดือนไม่พอ", "ค่าเช่าขึ้น", "แม่ป่วย", "นอนไม่หลับ"]
LONG = " ".join(random.choice(_PARTS) + str(i) for i in range(400))[:4000]


def _ms(fn):
    start = time.process_time()
    fn()
    return (time.process_time() - start) * 1000


def test_lookahead_rules_scan_once_not_from_every_position():
    assert _ms(lambda: T.SCAM_WORLD_IMPERSONATE.search(LONG)) < 50
    assert _ms(lambda: T.SCAM_RECOVERY.search(LONG)) < 50


def test_repeated_text_is_fast():
    assess("x")
    assert _ms(lambda: assess(("จะ" + "ไม่" * 1500)[:4000])) < 300
    assert _ms(lambda: assess(("a " * 2000)[:4000])) < 300


def test_long_text_still_finds_the_crisis_at_the_end():
    a = assess(("เหนื่อยมาก " * 60) + " อยากตายแล้วจริงๆ")
    assert a["crisis"]


def test_scam_rules_still_work_after_anchoring():
    assert assess("มีคนโทรมาบอกว่าช่วยตามเงินที่โดนโกงคืนได้ ต้องจ่ายค่าธรรมเนียมก่อน").get("scam")
    assert assess("Công an gọi bảo chuyển tiền vào tài khoản an toàn, kết bạn zalo").get("scam")
