"""รอบสุ่ม 110: แฟนเก่าดักรอหน้าที่พัก/ที่ทำงาน = ถูกตามคุกคาม"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["แฟนเก่าดักรอหน้าคอนโดทุกคืน", "ผัวเก่ามาเฝ้าหน้าที่ทำงานทุกเย็น",
                               "my ex keeps showing up outside my work every night"])
def test_ex_waiting_outside_is_urgent(q):
    # เคยได้ 65 ขณะที่ "มีคนตามสะกดรอยทุกวัน" ได้ 85
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["แฟนเก่าทักมาอวยพรวันเกิด", "แฟนเก่ามารอหน้าบ้านเพื่อคืนของ", "my ex keeps showing up in my dreams"])
def test_ordinary_ex_is_calm(q):
    assert assess(q)["risk_shown"] < 60
