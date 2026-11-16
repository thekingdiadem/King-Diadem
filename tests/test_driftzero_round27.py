"""DriftZero รอบสุ่ม 27: โยนิโสมนสิการ 4 วิธี มองจากหลักฐานเดียวกับ DriftZero และอริยสัจ 4
เดิมโยนิโสบอก "ยังไม่มีส่วนไหนต่ำเกินเส้น" ขณะที่ DriftZero หยุดเพราะแผนข้ามเส้นขั้นต่ำ
และข้ออริยสัจ 4 เป็นแค่แม่แบบ "ทุกข์ = ปัญหาจริงในประโยคเดียว" ไม่ใช่เรื่องของผู้ใช้"""
from ENGINE.driftzero import stop_reasons
from ENGINE.yonisomanasikara_engine import four_ways


def _steps(t):
    return dict(four_ways(t)["steps"])


def test_analysis_sees_the_line_driftzero_sees():
    s = _steps("จะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้")
    assert "กำลังข้ามเส้น" in s["แยกแยะส่วนประกอบ"] and "ยังไม่มีส่วนไหน" not in s["แยกแยะส่วนประกอบ"]
    assert s["อริยสัจ 4"].startswith("ทุกข์ = แผนนี้อาจทำให้เสียสิ่งที่ย้อนกลับไม่ได้")


def test_scam_cause_is_named_and_scam_comes_first():
    s = _steps("มีคนชวนลงทุนคริปโต การันตีกำไรวันละ 2% จะเอาเงินเก็บทั้งหมดไปลง")
    assert "ยังไม่ชัด" not in s["สืบสาวเหตุปัจจัย"]
    assert stop_reasons("มีคนชวนลงทุนคริปโต การันตีกำไรวันละ 2% จะเอาเงินเก็บทั้งหมดไปลง")[0][0] == "F1"


def test_four_truths_step_is_about_the_user_not_a_template():
    s = _steps("นอนไม่หลับมาหลายคืน")
    assert "นอนไม่หลับ" in s["อริยสัจ 4"] and "ปัญหาจริงในประโยคเดียว" not in s["อริยสัจ 4"]
