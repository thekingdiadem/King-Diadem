"""DriftZero รอบสุ่ม 22: ความเร็ว — ตัวด่านเองใช้ไม่ถึง 5 ms แต่ DriftZero เคยเรียกตัวจับหลักซ้ำหลายรอบต่อข้อความ
ตอนนี้อ่านครั้งเดียวแล้วใช้ซ้ำ (ส่วนตัวจับหลักที่ช้ากับข้อความยาวมาก ๆ เป็นงานแยก)"""
import time

from ENGINE import driftzero as D


def test_kernel_is_read_once_per_text():
    D._read.cache_clear()
    t = "ร้านจะเจ๊งแล้ว เหลือเงิน 1 หมื่น ไม่รู้จะทำยังไง"
    D.audit(t)
    D.audit(t)                                           # ส่งซ้ำ (กดส่งสองครั้ง / รอบต่อที่ตรวจข้อความเดิม)
    info = D._read.cache_info()
    assert info.misses == 1 and info.hits >= 1


def test_gates_alone_stay_fast_on_long_text():
    t = ("จะ" + "ไม่" * 1500)[:4000]
    start = time.process_time()
    for _, _, _, rx, _, _ in D.GATES:
        rx.search(t)
    assert time.process_time() - start < 0.5
