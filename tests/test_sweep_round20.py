"""รอบหาบั๊ก 20: แพ้รุนแรงที่ไม่ได้พิมพ์ว่า "แพ้" · ผึ้งต่อยไม่ใช่การชกต่อย · คอแข็ง · ครรภ์เป็นพิษ · เบื่อโลก"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("t", ["กินกุ้งแล้วปากบวมหายใจลำบาก", "ปวดหัวมาก อาเจียนพุ่ง คอแข็ง",
                               "แม่ท้อง 7 เดือน ปวดหัว ตาพร่า ความดันสูง"])
def test_medical_emergencies(t):
    assert "health_emergency" in assess(t)["topics"]


@pytest.mark.parametrize("t", ["นอนตกหมอนคอแข็ง", "ฟันผุ ปากบวมนิดหน่อย"])
def test_not_emergencies(t):
    assert "health_emergency" not in assess(t)["topics"]


def test_bee_sting_is_first_aid_not_violence():
    a = assess("โดนผึ้งต่อยหลายตัว หน้าบวม")
    assert "first_aid" in a["topics"] and "violence" not in a["topics"]
    assert "เหล็กไน" in compose("โดนผึ้งต่อยหลายตัว หน้าบวม")


def test_punch_is_still_violence():
    assert "violence" in assess("โดนเพื่อนต่อยหน้า")["topics"]


def test_preeclampsia_step():
    assert "ครรภ์เป็นพิษ" in compose("แม่ท้อง 7 เดือน ปวดหัว ตาพร่า ความดันสูง")


def test_tired_of_the_world_is_a_warning():
    assert "warning" in assess("เบื่อโลก เบื่อทุกอย่าง")["topics"]
    assert "warning" not in assess("เบื่อโลกโซเชียลจัง")["topics"]


# ── พบจากทดสอบหนัก 100,000 ครั้ง: คำบอกลาที่คนอื่นพูดถึงตัวเอง ──
@pytest.mark.parametrize("t", ["เพื่อนบอกว่าพรุ่งนี้คงไม่มีฉันแล้ว", "แม่บอกว่าพรุ่งนี้คงไม่มีผมแล้ว"])
def test_someone_elses_farewell(t):
    a = assess(t)
    assert not a["crisis"] and "someone" in a["topics"]


@pytest.mark.parametrize("t", ["พรุ่งนี้คงไม่มีฉันแล้ว", "พี่บอกว่าถ้าฉันอยากตายให้โทรหา",
                               "เพื่อนบอกว่าพรุ่งนี้คงไม่มีฉันแล้ว ส่วนฉันก็อยากตายเหมือนกัน"])
def test_users_own_crisis_still_detected(t):
    assert assess(t)["crisis"]
