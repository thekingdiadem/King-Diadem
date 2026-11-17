"""รอบสุ่ม 208 (เดิมเลข 138 ซึ่งซ้ำกับอีกแชท): รถตกน้ำ · พิษคาร์บอนมอนอกไซด์ · เด็กติดในตู้แช่ · เด็กปีนรั้วไฟฟ้า — และล้างรถไม่ใช่น้ำท่วม"""
import pytest
from core.kernel_voice import assess, compose

REAL = [("car went into the canal, water coming in, doors won't open", "car_water"), ("รถตกน้ำ น้ำเข้ารถ ประตูเปิดไม่ออก", "car_water"),
        ("whole family has headaches and nausea after running the generator indoors", "co_poison"),
        ("ทั้งบ้านปวดหัว คลื่นไส้ เวียนหัวหลังเปิดเครื่องปั่นไฟในบ้าน", "co_poison"),
        ("my friend fell asleep in a running car in a closed garage and won't wake up", "co_poison"),
        ("ลูกเล่นซ่อนแอบในตู้แช่เก่า ประตูปิดเปิดไม่ได้", "health_emergency"), ("เด็กปีนรั้วไฟฟ้า ตอนนี้ไม่ขยับ", "health_emergency")]
CALM = ["นอนพักในรถเปิดแอร์ที่ลานจอด", "ซื้อเครื่องปั่นไฟไว้ใช้ตอนไฟดับ", "ลูกเล่นซ่อนแอบในบ้านสนุกมาก", "รถตกหลุม ล้อแตก",
        "เด็กปีนรั้วโรงเรียนออกไปกินขนม", "ล้างรถเสร็จแล้ว น้ำเข้ารถนิดหน่อย"]


@pytest.mark.parametrize("t,topic", REAL)
def test_urgent_with_the_right_topic(t, topic):
    a = assess(t)
    assert a["risk_shown"] >= 85 and topic in a["topics"]


def test_co_reply_says_get_outside_first():
    # เดิมได้ "นั่งในท่าที่หายใจสบาย" — ทำให้คนยังอยู่ในห้องที่มีแก๊ส
    assert compose("ทั้งบ้านปวดหัว คลื่นไส้ เวียนหัวหลังเปิดเครื่องปั่นไฟในบ้าน", footer=False).startswith("ออกไปข้างนอก")
    assert compose("whole family has headaches and nausea after running the generator indoors", footer=False).startswith("Get everyone outside")


def test_car_in_water_reply_says_get_out_now():
    assert compose("car went into the canal, water coming in, doors won't open", footer=False).startswith("Get out of the car now")


@pytest.mark.parametrize("t", CALM)
def test_calm(t):
    assert assess(t)["risk_shown"] < 60
