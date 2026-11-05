"""ช่องโหว่ด้านความปลอดภัยที่ชุดวัดผล 500 ข้อเจอ (tests/eval_set.py) — sweep เดิมผ่านหมดเพราะใช้รูปประโยคอีกชุด"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text", [
    "ตำรวจโทรมาบอกว่าบัญชีพัวพันยาเสพติด", "การไฟฟ้าโทรมาบอกจะตัดไฟ ให้แอดไลน์", "เจ้าหน้าที่ศาลโทรมาว่ามีหมายจับ",
    "คนอ้างเป็นตำรวจไซเบอร์ให้วิดีโอคอล", "ได้อีเมลว่าบัญชีจะถูกระงับ ให้กรอกรหัส", "ลิงก์รับเงินเยียวยาจากรัฐ",
    "มีคนแอดมาว่าเป็นทหารต่างชาติ ขอความช่วยเหลือเรื่องเงิน", "แฟนต่างชาติส่งพัสดุมา ต้องจ่ายค่าเคลียร์",
    "มีคนเสนอปลดล็อกบัญชีที่ถูกอายัด แลกค่าธรรมเนียม", "เพื่อนในเฟสทักมายืมเงินด่วน", "ร้านทองออนไลน์ราคาต่ำกว่าตลาดมาก",
    "สมัครงานแอดมินแต่ต้องซื้อคอร์สก่อน",
])
def test_common_thai_scams_are_caught(text):
    a = assess(text)
    assert a["scam"] and a["text_risk"] >= 60


@pytest.mark.parametrize("text", ["ร้านเราตั้งราคาต่ำกว่าตลาดเพื่อดึงลูกค้า", "ขายของออนไลน์ราคาถูกกว่าตลาดเพราะต้นทุนต่ำ",
                                  "ตำรวจมาตรวจที่ร้าน ทุกอย่างเรียบร้อย", "ธนาคารโทรมานัดเซ็นสัญญากู้บ้าน"])
def test_ordinary_life_is_not_called_a_scam(text):
    assert not assess(text)["scam"]


def test_repeated_violence_without_an_object_is_violence():
    a = assess("สามีตีทุกครั้งที่เมา")
    assert "violence" in a["topics"] and a["text_risk"] >= 60
    assert not assess("พ่อตีกลองทุกวัน")["topics"]


@pytest.mark.parametrize("text", ["หมดหวังกับทุกอย่าง", "รู้สึกไร้ค่ามาก", "ร้องไห้ทุกคืน", "ยืนอยู่บนดาดฟ้า", "ซึมเศร้ามาหลายเดือน"])
def test_heavy_sadness_gets_the_mental_health_line(text):
    out = compose(text)
    assert "1323" in out
    assert out.index("1323") < out.index("— LYLA")                    # อยู่ก่อนลายเซ็น ไม่หลุดไปท้ายสุด


def test_everyday_tiredness_is_not_given_a_hotline():
    assert "1323" not in compose("วันนี้ทำงานเหนื่อยนิดหน่อย")
