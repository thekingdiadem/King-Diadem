"""DriftZero รอบสุ่ม 7: อ่านตัวเลขแบบที่คนพูดจริง"""
import pytest
from ENGINE.waterline_gauge import gauge


@pytest.mark.parametrize("t,cur", [("มีเงิน 3 แสนห้า จะใช้ 2 แสน", 350000), ("มีเงิน 1 ล้านสอง ขั้นต่ำ 5 แสน", 1200000),
                                   ("my restaurant is about to collapse, $500 left", 500), ("20 dollars remaining", 20),
                                   ("มีเงิน 3 แสน ห้าคนในทีม", 300000)])
def test_spoken_amounts(t, cur):
    # "3 แสนห้า" เคยอ่านได้ 300,000 · "$500 left" เคยอ่านไม่ออกเลย · "3 แสน ห้าคน" ต้องไม่กลายเป็น 350,000
    assert gauge(t)["current"] == cur
