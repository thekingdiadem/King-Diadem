"""รอบหาบั๊ก 18: กินยาเกินขนาดที่หลุด/กินยาครบชุดที่ถูกจับผิด · ถูกขัง · งานกดไลค์ต้องโอนก่อน · ระดับความเสี่ยง HIGH→CRITICAL"""
import pytest

import app
from core.kernel_voice import assess


@pytest.mark.parametrize("t", ["กินยานอนหลับไปทั้งแผง", "กลืนยาไปหมดแผง", "กินยาไปเยอะมาก ตอนนี้มึนๆ",
                               "took a whole bottle of pills", "ลูกชายกินยาของแม่ไปทั้งแผง", "กินยานอนทั้งแผงไปแล้ว"])
def test_overdose_detected(t):
    assert "overdose" in assess(t)["topics"]


@pytest.mark.parametrize("t", ["กินยาฆ่าเชื้อหมดแผงแล้ว ยังไม่หายเลย", "กินยาครบทั้งแผงตามที่หมอสั่ง",
                               "กินยาคุมหมดแผงแล้ว ประจำเดือนยังไม่มา", "กินยาคุมหมดแผง ต้องเริ่มแผงใหม่วันไหน"])
def test_finishing_a_course_is_not_overdose(t):
    a = assess(t)
    assert "overdose" not in a["topics"]
    assert (a["text_risk"] or 0) < 35


@pytest.mark.parametrize("t", ["สามีขังฉันไว้ในบ้าน", "โดนกักขังอยู่ในห้อง"])
def test_confinement_is_violence(t):
    assert "violence" in assess(t)["topics"]


@pytest.mark.parametrize("t", ["แม่ขังหมาไว้ในบ้าน", "โดนขังในเกม"])
def test_confinement_false_positives(t):
    assert "violence" not in assess(t)["topics"]


@pytest.mark.parametrize("t", ["งานออนไลน์กดไลค์ได้เงิน แต่ต้องโอนเงินก่อน",
                               "รับงานรีวิวสินค้า ต้องโอนเงินมัดจำก่อนถึงจะได้ค่าคอม",
                               "ทำภารกิจกดออเดอร์ ต้องเติมเงินก่อนถอนได้",
                               "มีคนทักมาให้ทำงานพิเศษ กดไลค์ยูทูบได้วันละ 1000"])
def test_task_scams(t):
    assert "job" in assess(t)["scam"]


@pytest.mark.parametrize("t", ["ช่วยเขียนรีวิวร้านอาหารให้หน่อย", "อยากหางานเสริมทำช่วงเย็น"])
def test_ordinary_jobs_are_not_scams(t):
    assert not assess(t)["scam"]


@pytest.mark.parametrize("ctx,t_risk,expect", [
    ("[Risk: HIGH]", 90, "[Risk: CRITICAL จากข้อความ]"),   # เดิมค้างที่ HIGH
    ("", 90, "[Risk: CRITICAL จากข้อความ]"),
    ("[Risk: LOW]", 40, "[Risk: MEDIUM จากข้อความ]"),
    ("[Risk: MEDIUM]", 60, "[Risk: HIGH จากข้อความ]"),
    ("[Risk: MEDIUM]", 40, "[Risk: MEDIUM]"),
    ("[Risk: HIGH]", 60, "[Risk: HIGH]"),
    ("[Risk: CRITICAL]", 60, "[Risk: CRITICAL]"),             # ไม่ลดระดับ
    ("[Risk: HIGH]", 10, "[Risk: HIGH]"),
])
def test_text_risk_raises_level(ctx, t_risk, expect):
    assert app._risk_ctx_from_text(ctx, t_risk) == expect
