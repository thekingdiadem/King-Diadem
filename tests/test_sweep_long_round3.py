"""ไล่หาบั๊กรอบยาว 3 (หลัง PR #73): ค่าจ้างค้าง/หักเงินเดือน/ประกันสังคม · มิจฉาชีพอ้างตำรวจ · บัตรถูกรูด
· หัวกระแทกแล้วอาเจียน · แพ้ผึ้ง · ลูกติดเกม · ซื้อรถ/คอนโด · เปลี่ยนงาน · สัตว์เลี้ยงโดนรถชน · อังกฤษ"""
import pytest

from core.kernel_voice import compose


@pytest.mark.parametrize("text,needle,bad", [
    ("ไม่ได้รับเงินเดือนมา 2 เดือนแล้ว", "1546", "หักเงินเก็บทันที"),
    ("ถูกหักเงินเดือนเพราะมาสาย", "หักค่าจ้างเป็นค่าปรับ", "หักเงินเก็บทันที"),
    ("นายจ้างไม่ส่งประกันสังคม", "SSO Connect", "เขียนสิ่งที่เกิดขึ้น"),
])
def test_wage_problems_are_labor_rights(text, needle, bad):
    out = compose(text)
    assert needle in out and bad not in out


def test_police_impersonation_call_is_a_scam():
    out = compose("มีคนโทรมาอ้างเป็นตำรวจ บอกว่าบัญชีพัวพันยาเสพติด")
    assert "มิจฉาชีพ" in out and "1441" in out


def test_unknown_card_charge_is_not_debt_payoff():
    out = compose("ถูกเรียกเก็บค่าบัตรเครดิตที่ไม่ได้ใช้")
    assert "อายัดบัตร" in out and "โปะ" not in out


def test_head_injury_with_vomiting():
    out = compose("ลูกตกบันได หัวโน อาเจียน")
    assert "ไปโรงพยาบาลตอนนี้" in out and "24 ชั่วโมง" in out


def test_bee_sting_anaphylaxis():
    assert "อะดรีนาลีน" in compose("ถูกผึ้งต่อย หน้าบวม หายใจลำบาก")


def test_child_gaming_is_addressed_to_the_parent():
    out = compose("ลูกติดเกมจนไม่ยอมนอน")
    assert "ตกลงกติกาด้วยกัน" in out and "ไม่พกบัตร" not in out


@pytest.mark.parametrize("text,needle", [("จะซื้อรถคันแรก เงินเดือน 20,000", "20% ของรายได้"),
                                         ("อยากซื้อคอนโด ผ่อนเดือนละ 15,000 เงินเดือน 35,000", "30–35% ของรายได้")])
def test_big_purchase_affordability_rule(text, needle):
    assert needle in compose(text)


def test_changing_jobs_is_about_the_job():
    out = compose("อยากเปลี่ยนงาน แต่กลัวเงินเดือนลด")
    assert "ยังไม่ลาออกจนกว่า" in out and "หักเงินเก็บทันที" not in out


def test_family_opener_no_longer_says_keep_distance():
    assert "ระยะห่างเลือกได้" not in compose("ทำงานหนักจนไม่มีเวลาให้ครอบครัว")


@pytest.mark.parametrize("text,needle", [("my dog was hit by a car", "vet"), ("หมาโดนรถชน", "โรงพยาบาลสัตว์"),
                                         ("I want to start a small business", "break-even"),
                                         ("my mom has dementia and keeps getting lost", "ID bracelet")])
def test_more_topics(text, needle):
    assert needle in compose(text)
