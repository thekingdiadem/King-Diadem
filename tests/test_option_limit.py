"""มาตรา 11 — คำตอบจาก LLM ต้องเสนอทางเลือกไม่เกิน 3 ทาง (เดิมหน้าเว็บจริงตอบ 5 กลยุทธ์)"""
from core.cosmic_latte_canon import MAX_OPTIONS, limit_options, offered_choices


FIVE = """ลองดูแบบนี้นะคะ
1. คุยกับหัวหน้าก่อน
   - เตรียมตัวเลขไปด้วย
2. หาข้อมูลตลาด
3. ลองทำเล็กๆ ก่อน
4. ขอคำปรึกษาเพื่อน
   - คนที่เคยทำ
5. ลาออกเลย

ไม่ว่าทางไหน คุณเป็นคนตัดสินใจเสมอค่ะ"""


def test_five_numbered_options_cut_to_three():
    out = limit_options(FIVE)
    assert "4." not in out and "5." not in out and "คนที่เคยทำ" not in out
    assert "1. คุยกับหัวหน้าก่อน" in out and "เตรียมตัวเลขไปด้วย" in out and "3. ลองทำเล็กๆ ก่อน" in out
    assert out.endswith("คุณเป็นคนตัดสินใจเสมอค่ะ")      # ย่อหน้าปิดท้ายยังอยู่
    assert offered_choices(out) <= MAX_OPTIONS + 1        # 3 ข้อ + bullet ย่อย 1


def test_short_lists_and_plain_text_unchanged():
    three = "1. ก\n2. ข\n3. ค"
    assert limit_options(three) == three
    assert limit_options("ไม่มีรายการ") == "ไม่มีรายการ"
    assert limit_options("") == ""


def test_app_applies_limit_before_canon_check(client):
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = FIVE
    r = client.post("/run", json={"input": "ช่วยวางกลยุทธ์หาลูกค้าให้หน่อย"}).json()
    assert "5. ลาออกเลย" not in r["ai_response"]
