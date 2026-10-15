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


@pytest.mark.parametrize("text", ["อยากเลิกเหล้า แต่ลงแดง มือสั่น", "เป็นไข้เลือดออก เกล็ดเลือดต่ำ"])
def test_withdrawal_and_dengue_warning_are_answered_after_quota(client, app_module, text):
    """เดิม Risk 0 — โควตาหมดแล้วได้หน้าจ่ายเงิน ทั้งที่อาการขาดสุราชักได้ และไข้เลือดออกช็อกได้"""
    from core.kernel_voice import assess
    assert assess(text)["text_risk"] >= 75
    for i in range(app_module.FREE_DAILY_RUNS):
        client.post("/run", json={"input": f"ทำงานเหนื่อย {i}"})
    r = client.post("/run", json={"input": text})
    assert r.status_code == 200 and r.json().get("answer_source") == "kernel"


def test_dengue_without_warning_signs_is_not_escalated():
    from core.kernel_voice import assess
    assert assess("เป็นไข้เลือดออกหายแล้ว")["text_risk"] < 75


@pytest.mark.parametrize("text", ["พ่อเมาแล้วตีแม่ทุกคืน", "แม่โดนพ่อเลี้ยงตบ"])
def test_child_witnessing_violence_at_home(text):
    """เดิมตอบเหมือนผู้ใช้เป็นคนถูกตี ("ความปลอดภัยของคุณมาก่อนทุกเรื่อง · บาดเจ็บโทร 1669")"""
    out = compose(text)
    assert "เห็นคนในบ้านถูกทำร้าย" in out and "อย่าเข้าไปห้ามเอง" in out and "1387" in out


def test_user_being_hit_is_still_safety():
    assert "ความปลอดภัยของคุณมาก่อน" in compose("พ่อตีผม")
