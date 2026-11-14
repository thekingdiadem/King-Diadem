"""เทสต์แบบสุ่ม (พ.ย. 2026): ข้อความหลายรูปแบบที่เคยได้คำตอบทั่วไปหรือผิดเรื่อง"""
import pytest
from core.kernel_voice import assess, compose

GEN = ("ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน", "Let's lay this out step by step.")


@pytest.mark.parametrize("q,must", [
    ("ไข้ขึ้น 39 ปวดตัว ปวดกระบอกตา", "ไข้เลือดออก"),
    ("มีคนโทรมาบอกว่าเป็นตำรวจ บอกว่าบัญชีเราพัวพันยาเสพติด", "แก๊งคอลเซ็นเตอร์"),
    ("บ้านน้ำท่วม ของเสียหายหมด", "ตัดไฟ"),
    ("มีผื่นแดงคันทั้งตัวหลังกินกุ้ง", "1669"),
    ("ตั้งท้องไม่ได้ตั้งใจ อายุ 17", "1663"),
    ("พ่อเป็นอัลไซเมอร์ จำใครไม่ได้แล้ว", "กิจวัตร"),
    ("เวียนหัวบ้านหมุนตอนลุกจากเตียง", "ปากเบี้ยว"),
    ("เมียชอบด่า ดูถูก", "ไม่ใช่เรื่องปกติ"),
    ("เพื่อนชวนเล่นยา", "1165"),
    ("ลูกเอายาบ้ามาที่บ้าน", "1165"),
    ("แม่ป่วยติดเตียง ต้องดูแลคนเดียว", "รพ.สต."),
    ("นอนบ่หลับเลยมื้อนี้", "ตื่นเวลาเดิม"),
    ("แพ้ท้องหนักมาก", "24 ชั่วโมง"),
    ("มีคนเอารูปเราไปโพสต์", "แคปหน้าจอ"),
    ("ซื้อของในshopeeไม่ได้ของ", "ห้ามกด"),
    ("ข้างห้องเสียงดังทุกคืน", "นิติบุคคล"),
    ("ลืมรหัสธนาคาร", "มิจฉาชีพ"),
    ("my dog died yesterday", "grief is real"),
    ("my boss yells at me every day", "1546"),
    ("im broke af", "essentials"),
    ("OMG I passed my exam!!!", "Congratulations"),
])
def test_specific_answers(q, must):
    o = compose(q, footer=False)
    assert must in o and not o.startswith(GEN), o[:120]


def test_sudden_vision_loss_is_emergency():
    q = "ตาข้างขวามัวๆ ทันที"
    assert assess(q)["risk_shown"] >= 80 and "1669" in compose(q, footer=False)


@pytest.mark.parametrize("q", ["เหนื่อย", "ทำไมต้องเป็นเรา", "งงชีวิต"])
def test_short_feelings_not_generic(q):
    assert not compose(q, footer=False).startswith(GEN)


def test_english_only_lenses_are_reachable():
    from core import problem_lens
    assert problem_lens.find("my dog died yesterday", "en")["key"] == "pet_died"
