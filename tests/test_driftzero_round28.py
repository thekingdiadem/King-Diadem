"""DriftZero รอบสุ่ม 28: ผู้พิทักษ์โพธิปักขิยธรรมต้องไม่บอก "PEACE — ดำเนินการได้" กับแผนที่ DriftZero หยุด
ตัวนี้ทำงานก่อนส่งให้ AI ทุกครั้ง — ถ้าบอก AI ว่าสงบ แต่ DriftZero บอกว่าต้องหยุด ระบบจะพูดขัดกันเอง"""
import pytest
from ENGINE.bodhipakkhiya_engine import guardian_check, llm_hint

DANGER = ["จะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้", "โรงงานจะเอากากอุตสาหกรรมไปทิ้งที่บ่อร้างเพราะถูกกว่าส่งกำจัด",
          "ผู้รับเหมาจะไม่ใส่ราวกันตกที่ชั้น 8 เพราะงานต้องเสร็จไว", "รถรับส่งนักเรียนจะไม่มีครูเช็กเด็กก่อนล็อกรถ",
          "บริษัทจะโอนเงินให้ซัพพลายเออร์ตามอีเมลที่บอกว่าเปลี่ยนเลขบัญชีใหม่"]


@pytest.mark.parametrize("t", DANGER)
def test_guardian_does_not_say_peace_to_crossing_plans(t):
    g = guardian_check(t)
    assert not g["peace"] and g["final_verdict"].startswith(("PAUSE", "STOP")) and g["driftzero"]
    assert "DriftZero" in llm_hint(g) and "อย่าบอกว่าดำเนินการได้" in llm_hint(g)


@pytest.mark.parametrize("t", ["จะเปิดร้านกาแฟสาขาสองใช้เงิน 5 แสน", "วันนี้อากาศดี"])
def test_ordinary_text_keeps_peace(t):
    g = guardian_check(t)
    assert g["peace"] and not g["driftzero"]
