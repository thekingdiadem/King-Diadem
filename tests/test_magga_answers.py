"""ตอนไม่มี AI คำตอบต้องทักเรื่องที่มรรค 8 จับได้ — เดิม "จะโกหกลูกค้าเพื่อปิดการขาย" ได้คำตอบธุรกิจทั่วไป
(ดูกระแสเงินสด หาจุดคุ้มทุน) ทั้งที่แผง Σ ขึ้น ✗ สัมมาวาจา"""
import pytest

from core.kernel_voice import compose, compose_council


@pytest.mark.parametrize("text,opening", [
    ("จะโกหกลูกค้าเรื่องคุณภาพสินค้าเพื่อปิดการขาย", "การโกหกอาจได้ผลวันนี้"),
    ("อยากจ้างคนเขียนรีวิวปลอมให้ร้าน", "การโกหกอาจได้ผลวันนี้"),
    ("จะจ่ายเงินใต้โต๊ะให้ได้งานประมูล", "ทางนี้ได้เงินเร็ว"),
    ("มีคนจ้างให้เปิดบัญชีม้า ได้ครั้งละ 3000", "ทางนี้ได้เงินเร็ว"),
    ("อยากแก้แค้นเพื่อนร่วมงานให้มันโดนไล่ออก", "อยากเอาคืน"),
    ("I want to lie to customers about quality to close the sale", "a lie might work today"),
])
def test_offline_answer_names_the_issue(text, opening):
    assert opening in compose(text)
    if not text.isascii():
        assert opening in compose_council(text)


def test_bank_mule_answer_points_to_the_hotline():
    assert "บัญชีม้า" in compose("มีคนจ้างให้เปิดบัญชีม้า ได้ครั้งละ 3000") and "1441" in compose("มีคนจ้างให้เปิดบัญชีม้า ได้ครั้งละ 3000")


@pytest.mark.parametrize("text", ["เพื่อนโกหกเรา ควรคุยกับเขายังไงดี", "แฟนโกหกเรื่องเงิน ทำยังไงดี",
                                  "อยากเปิดร้านกาแฟเล็กๆ ควรเริ่มยังไง", "โดนหัวหน้าด่าต่อหน้าคนอื่น"])
def test_being_lied_to_or_plain_questions_are_not_lectured(text):
    out = compose(text)
    assert "การโกหกอาจได้ผลวันนี้" not in out and "ทางนี้ได้เงินเร็ว" not in out and "อยากเอาคืน" not in out


def test_a_threat_against_the_user_is_not_their_revenge():
    """"คนแปลกหน้าในเกมขอรูปลูกสาว ขู่จะประจาน" — คนขู่คืออีกฝ่าย ไม่ใช่ผู้ใช้อยากเอาคืน"""
    out = compose("คนแปลกหน้าในเกมขอรูปโป๊ลูกสาว ขู่จะประจาน")
    assert "อยากเอาคืน" not in out
