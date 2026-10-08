"""รอบหาบั๊ก 21: ตัวเลขยาวติดกันทำให้ regex ไล่ย้อนแบบกำลังสอง (เดิม "1"×4000 ใช้ 1.2–1.7 วินาที)"""
import time

import pytest

from core.engine_bridge import analyze
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("t", ["1" * 8000, "9" * 8000 + " มื้อ", "ก" * 4000 + "1" * 4000])
def test_long_digit_runs_stay_fast(t):
    # แบบกำลังสองที่ 8000 ตัวใช้หลายวินาที — แบบเส้นตรงไม่ถึงครึ่งวินาที
    s = time.perf_counter()
    assess(t), compose(t, route="survival"), analyze(t)
    assert time.perf_counter() - s < 2.0


@pytest.mark.parametrize("t,needle", [
    ("เหลือเงิน 500 บาท ข้าว 3 มื้อ", "อาหาร 3 มื้อ"),
    ("กู้นอกระบบ 10000 ดอก 20% ต่อเดือน", "ดอก 240%"),
    ("หนี้บัตร 20000 ดอก 2.5%", "ดอก 2.5%"),
])
def test_numbers_still_read_correctly(t, needle):
    assert needle in " ".join(analyze(t)["lines"])


@pytest.mark.parametrize("t,topic", [("น้องกินแชมพูเข้าไป", "overdose"),
                                     ("พ่อปวดท้องรุนแรง ท้องแข็ง", "health_emergency"),
                                     ("ลูกสาวคุยกับผู้ชายในเกม เขาขอรูปเปลือย", "sextortion")])
def test_detected(t, topic):
    assert topic in assess(t)["topics"]


def test_pregnancy_tightening_is_not_an_emergency():
    assert "health_emergency" not in assess("ท้อง 8 เดือน ท้องแข็งบ่อย")["topics"]


def test_daily_profit_promise_is_a_red_flag():
    assert "guarantee" in assess("ผมโดนทักมาให้ลงทุนทองคำ กำไรวันละ 5%")["offer_flags"]


def test_impersonator_asking_to_add_line():
    assert assess("มีคนอ้างเป็นเจ้าหน้าที่ไฟฟ้า ให้แอดไลน์")["scam"]
