"""รอบสุ่ม 134: คนท้องโดนถีบท้อง · ยานอนหลับเกินจนปลุกไม่ตื่น · แผลสักติดเชื้อมีไข้สูง · โรคน้ำหนีบหลังดำน้ำ"""
import pytest
from core.kernel_voice import assess

REAL = ["คนท้อง 7 เดือนโดนสามีถีบท้อง", "ผู้สูงอายุกินยานอนหลับผิดขนาด ปลุกไม่ตื่น", "เพื่อนสักลายแล้วแขนบวมแดงร้อน มีไข้สูง",
        "เพื่อนดำน้ำแล้วขึ้นมาเจ็บข้อต่อ ปวดหัว ชา", "after scuba diving my friend has joint pain and numbness",
        "my pregnant wife was kicked in the stomach by her ex", "grandpa took too many sleeping pills and won't wake up"]
CALM = ["คนท้อง 7 เดือนไปตรวจครรภ์มา ลูกดิ้นดี", "ลูกในท้องถีบท้องแรงมาก", "เพื่อนสักลายใหม่สวยมาก แดงนิดหน่อย",
        "ไปดำน้ำมา สนุกมาก เห็นเต่าทะเล", "ดำน้ำมาแล้วหูอื้อนิดหน่อย", "ผู้สูงอายุกินยานอนหลับตามหมอสั่ง หลับสบาย"]


@pytest.mark.parametrize("t", REAL)
def test_missed_before_now_urgent(t):
    # 5 ข้อแรกเคยได้ 0
    assert assess(t)["risk_shown"] >= 80


@pytest.mark.parametrize("t", CALM)
def test_everyday_calm(t):
    # "ลูกในท้องถีบท้องแรงมาก" คือลูกดิ้น ไม่ใช่ความรุนแรง
    assert assess(t)["risk_shown"] < 60
