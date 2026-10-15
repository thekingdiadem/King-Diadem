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


def test_money_breakdown_is_not_cut():
    """เดิมรายการค่าใช้จ่าย 5 ข้อถูกตัดเหลือ 3 แต่ "รวม 17,500" ยังอยู่ — ตัวเลขไม่ตรงกัน"""
    t = ("ค่าใช้จ่ายต่อเดือน:\n1. ค่าเช่า 5,000 บาท\n2. ค่าอาหาร 6,000 บาท\n3. ค่าเดินทาง 2,000 บาท\n"
         "4. ค่าน้ำไฟ 1,500 บาท\n5. ค่าโทรศัพท์ 3,000 บาท\nรวม 17,500 บาท")
    assert limit_options(t) == t


def test_first_aid_steps_are_not_cut():
    t = "ขั้นตอนปฐมพยาบาล:\n1. ตั้งสติ\n2. โทร 1669\n3. ห้ามเลือด\n4. ยกส่วนที่เจ็บให้สูง\n5. รอทีมแพทย์"
    assert limit_options(t) == t


def test_blank_line_before_closing_paragraph_kept():
    out = limit_options(FIVE)
    assert "\n\nไม่ว่าทางไหน" in out
