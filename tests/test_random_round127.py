"""รอบสุ่ม 127: สายเซฟตี้ขาด/นั่งร้านถล่ม มีคนห้อยอยู่"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ทำงานบนตึกแล้วสายเซฟตี้ขาด เพื่อนห้อยอยู่", "นั่งร้านถล่ม คนงานค้างอยู่ข้างบน", "the harness snapped and my coworker is dangling",
])
def test_worker_hanging_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["เชือกรองเท้าขาด", "สายกระเป๋าขาด ของตกเต็มพื้น", "ห้อยโมบายไว้ที่หน้าต่าง"])
def test_everyday_snaps_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
