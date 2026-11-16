"""รอบสุ่ม 111: รถคว่ำแล้วมีคนติดอยู่ ต้องได้ระดับฉุกเฉิน ไม่ใช่แค่ปฐมพยาบาล"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["รถคว่ำ คนขับติดอยู่ข้างใน", "รถตกคลอง แม่ยังติดอยู่ในรถ", "รถชนเสาไฟ คนขับหมดสติ"])
def test_trapped_after_crash_is_urgent(q):
    # "รถคว่ำ คนขับติดอยู่ข้างใน" เคยได้ 75
    assert assess(q)["risk_shown"] >= 80


def test_crash_everyone_out_is_calm():
    assert assess("รถคว่ำ ทุกคนออกมาได้ ไม่มีใครเจ็บ")["risk_shown"] < 60
