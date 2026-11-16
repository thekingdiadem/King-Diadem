"""รอบสุ่ม 104: สัญญาณเตรียมตัว (สะสมยา · ยกของให้หมด) ต้องได้ระดับวิกฤตเท่ากันทั้งไทยและอังกฤษ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["เก็บยานอนหลับไว้เยอะแล้ว", "ยกของให้เพื่อนหมดแล้ว ไม่ต้องใช้อีก", "i gave away all my stuff, won't need it",
                               "i've been saving up my sleeping pills"])
def test_preparation_signs_are_crisis(q):
    # ฉบับไทยเคยได้ 65 ขณะที่ "saving up my sleeping pills" ได้ 95
    assert assess(q)["crisis"]


@pytest.mark.parametrize("q", ["ยกของให้เพื่อนหมดแล้วเพราะย้ายบ้าน", "ร้านขายยาเก็บยาไว้เยอะ", "แจกของเล่นเก่าให้หลานหมดแล้ว ลูกโตแล้วไม่ได้ใช้อีกแล้ว",
                               "ไม่อยากตื่นเช้าไปทำงานเลย", "เขียนจดหมายลาออกให้หัวหน้าแล้ว"])
def test_everyday_not_crisis(q):
    assert not assess(q)["crisis"]
