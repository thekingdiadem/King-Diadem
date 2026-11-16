"""DriftZero รอบสุ่ม 25: ส่งข้อความเดียวกันเข้า DriftZero · อริยสัจ 4 · สภา 6 เสียง แล้วดูว่าเห็นตรงกันไหม

เจ้าของโปรเจกต์: "การจะเข้าใจและมองทะลุ ต้องไม่ใช่สิ่งที่คิดไปเอง ไม่ว่าจะคนหรือระบบ"
เดิม "จะใช้เงินสำรองทั้งหมดขยาย 10 สาขา" DriftZero หยุด แต่อริยสัจ 4 บอกว่า "ยังไม่ชัด"
และสภาบอกว่า "ความเสี่ยงยังไม่ชัด" — ต่างคนต่างเห็นจากหลักฐานคนละชุด
"""
import pytest
from ENGINE.driftzero import audit
from ENGINE.ariya_sacca import four_truths
from core.kernel_voice import compose_council

CROSS_LINE = ["จะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้", "โรงงานจะเอากากอุตสาหกรรมไปทิ้งที่บ่อร้างเพราะถูกกว่าส่งกำจัด"]


@pytest.mark.parametrize("t", CROSS_LINE)
def test_all_three_see_the_same_line(t):
    assert audit(t)["verdict"] == "stop"
    f = four_truths(t)
    assert f["key"] == "driftzero" and f["dukkha"] != "ยังไม่ชัด"
    c = compose_council(t, footer=False)
    assert "ความเสี่ยงสูง — DriftZero" in c and "เดินหน้าได้" not in c.split("มติสภา")[1]


def test_crisis_and_scam_agree_everywhere():
    t = "อยากตายแล้ว ธุรกิจเจ๊ง"
    assert audit(t)["verdict"] == "urgent" and four_truths(t)["key"] == "crisis"
    s = "มีคนชวนลงทุนคริปโต การันตีกำไรวันละ 2% จะเอาเงินเก็บทั้งหมดไปลง"
    assert audit(s)["verdict"] == "stop" and four_truths(s)["key"] == "scam"


def test_personal_burnout_is_not_judged_by_gates_in_the_council():
    # คนที่เล่าว่าหมดไฟไม่ได้กำลังวางแผนอะไร — สภาไม่ควรยกด่าน H1 มาพูด
    c = compose_council("ทำงานหนักจนหมดไฟ ไม่ได้นอนมาหลายวัน", footer=False)
    assert "DriftZero" not in c


def test_ordinary_plan_keeps_its_own_reading():
    t = "จะเปิดร้านกาแฟสาขาสองใช้เงิน 5 แสน"
    assert four_truths(t)["key"] == "business" and "DriftZero" not in compose_council(t, footer=False)
