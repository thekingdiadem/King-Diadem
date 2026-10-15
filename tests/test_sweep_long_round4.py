"""ไล่หาบั๊กรอบยาว 4: ไข้เลือดออก · ขาดสุรา · ติดค้างกลางทาง/หลงป่า · ถูกควบคุม (อังกฤษ) · ครูตีลูก
· ตำรวจขอเงิน · โอที · ขอขึ้นเงินเดือน · โควิดอยู่คนเดียว · กินยาผิดเวลา · ผ่าตัด · ใบสั่ง · เพื่อน · อายุ 17 อยากออกจากบ้าน"""
import pytest

from core.kernel_voice import compose


@pytest.mark.parametrize("text,needle", [
    ("เป็นไข้เลือดออก เกล็ดเลือดต่ำ", "ห้ามกินไอบูโพรเฟน"),
    ("อยากเลิกเหล้า แต่ลงแดง มือสั่น", "อย่าหยุดเองคนเดียวทันที"),
    ("รถเสียกลางทาง ตอนกลางคืนคนเดียว", "แชร์ location"),
    ("หลงทางในป่า แบตใกล้หมด", "1362"),
    ("my partner checks my phone and won't let me see friends", "coercive control"),
    ("ลูกโดนครูตี", "ผู้อำนวยการโรงเรียน"),
    ("โดนตำรวจเรียกตรวจ ขอเงิน", "1599"),
    ("หัวหน้าให้ทำโอทีทุกวันไม่จ่ายเงิน", "1.5 เท่า"),
    ("อยากขอเงินเดือนขึ้น ควรพูดยังไง", "ผลงาน 3 ข้อ"),
    ("ติดโควิด อยู่คนเดียว", "94%"),
    ("ยายกินยาผิดเวลา", "ห้ามกินเพิ่มเป็นสองเท่า"),
    ("หมอให้ผ่าตัด แต่ไม่แน่ใจ", "second opinion"),
    ("ได้ใบสั่งจราจร ไม่ได้ทำผิด", "ptm.police.go.th"),
    ("เพื่อนสนิทไม่คุยด้วยแล้ว ไม่รู้ทำอะไรผิด", "อย่าเพิ่งตัดสินจากความเงียบ"),
    ("อยากย้ายออกจากบ้าน อายุ 17", "1387"),
    ("can I get a refund if a flight is cancelled", "chargeback"),
])
def test_specific_answers(text, needle):
    out = compose(text)
    assert needle in out
    assert "เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว" not in out and "Write what happened in one sentence" not in out


def test_teacher_case_is_not_addressed_as_the_victim():
    assert "ความปลอดภัยของคุณมาก่อนทุกเรื่อง" not in compose("ลูกโดนครูตี")


def test_raise_request_is_not_savings_advice():
    assert "หักเงินเก็บทันที" not in compose("อยากขอเงินเดือนขึ้น ควรพูดยังไง")
