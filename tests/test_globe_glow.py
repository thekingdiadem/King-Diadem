"""ลูกโลกหน้าแชท: ไฟเมืองเรืองแสงสีทอง + ภาพ 4K สำหรับเครื่องที่ไหว
เจ้าของโปรเจกต์อยากให้ "เรืองแสงแบบในรูป ละเอียดขึ้น" — เดิมใช้ภาพ 2K อย่างเดียว เมฆเป็นบล็อกตอนโลกใหญ่เต็มจอ"""
from tests._front import front_page


def test_city_lights_glow_from_a_blurred_mip():
    p = front_page()
    assert "texture2D(uLights,uv,2.)" in p                 # รัศมีรอบเมือง (bloom ราคาถูก)


def test_4k_only_after_first_paint_and_only_on_capable_devices():
    p = front_page()
    assert "function loadHi()" in p and "setTimeout(loadHi" in p
    for guard in ("MAX_TEXTURE_SIZE) < 4096", "conn.saveData", "mem < 4"):
        assert guard in p, guard
    assert "'/static/earth/day_4k.jpg', null, '/static/earth/clouds_4k.jpg'" in p   # ไฟเมือง 4K จางเกินเมื่อย่อ — คงไฟล์ 2K
