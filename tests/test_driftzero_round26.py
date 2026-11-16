"""DriftZero รอบสุ่ม 26: DriftZero · อริยสัจ 4 · ปฏิจจสมุปบาท · สภา 6 เสียง — ต้นเหตุต้องมาจากหลักฐานเดียวกัน
เดิมปฏิจจสมุปบาทตอบ "อวิชชา" ทุกเคส และอริยสัจ 4 ตอบ "ยังไม่ชัด" ทั้งที่ DriftZero เห็นเหตุชัดแล้ว"""
import pytest
from ENGINE.ariya_sacca import four_truths
from ENGINE.paticcasamuppada_engine import detect_root_cause
from core.kernel_voice import compose_council


def test_sunk_cost_is_clinging():
    assert detect_root_cause("จะลงทุนเพิ่มเพราะลงไปแล้ว 2 ล้าน ถ้าหยุดตอนนี้เสียดาย")["root"] == "clinging"


@pytest.mark.parametrize("t", ["จะเอาบ้านไปจำนองเพื่อลงทุนคริปโต", "บริษัทจะไม่จ่ายค่าโอที เพื่อลดต้นทุน"])
def test_four_truths_cause_is_seen_when_driftzero_sees_it(t):
    assert four_truths(t)["samudaya"] != "ยังไม่ชัด"


def test_council_names_the_trade_when_a_line_is_crossed():
    c = compose_council("บริษัทจะไม่จ่ายค่าโอที เพื่อลดต้นทุน", footer=False)
    assert "แลกสิ่งที่ย้อนกลับไม่ได้" in c.split("PATICCA")[1].split("TITAN")[0]


def test_cutting_costs_to_survive_is_not_called_craving():
    # คนที่ประหยัดเพื่อเอาตัวรอดต้องไม่โดนบอกว่าต้นเหตุคือความอยากได้
    assert detect_root_cause("ต้องลดต้นทุนค่ากินเพราะเงินเดือนไม่พอ")["root"] != "craving"
