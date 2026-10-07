"""รอบหาบั๊ก 17: อาการฉุกเฉินที่หลุด · ปฐมพยาบาลภาษาอังกฤษ · สึนามิ/ดินถล่ม · งานหลอกต่างประเทศ/บัญชีม้า"""
import pytest

from core.kernel_voice import assess


@pytest.mark.parametrize("t", ["หายใจลำบาก ตัวเขียว", "ปวดท้องน้อยขวาอย่างรุนแรง", "เลือดออกทางช่องคลอดตอนท้อง",
                               "my baby has a fever of 40"])
def test_medical_emergencies(t):
    assert "health_emergency" in assess(t)["topics"]


def test_not_emergencies():
    assert "health_emergency" not in assess("สีเขียวตัวนี้สวย")["topics"]
    assert "health_emergency" not in assess("ปวดท้อง")["topics"]


@pytest.mark.parametrize("t", ["I think I broke my arm", "got bitten by a dog"])
def test_english_first_aid(t):
    assert "first_aid" in assess(t)["topics"]


@pytest.mark.parametrize("t,kind", [("house is shaking", "quake"), ("tsunami warning", "quake"), ("สึนามิ", "quake"),
                                    ("landslide near my village", "storm")])
def test_disasters(t, kind):
    assert (assess(t)["disaster"] or {}).get("kind") == kind


def test_tsunami_gets_coast_steps():
    from core.engine_bridge import analyze
    steps = " ".join(analyze("สึนามิ")["data"]["disaster"]["steps"])
    assert "ที่สูง" in steps


def test_shaking_from_music_is_not_quake():
    assert not assess("the room is shaking with music")["disaster"]


@pytest.mark.parametrize("t", ["มีคนขอให้รับพัสดุแทนแล้วได้เงิน", "ได้งานต่างประเทศ ไม่ต้องใช้ประสบการณ์ เงินเดือนแสน",
                               "รับเปิดบัญชีแลกเงิน"])
def test_job_scams_and_mule_accounts(t):
    assert "job" in assess(t)["scam"]


def test_real_overseas_work_is_fine():
    assert not assess("ทำงานต่างประเทศมา 5 ปี")["scam"]
