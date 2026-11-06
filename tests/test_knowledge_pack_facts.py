"""ตัวเลขทุกตัวในชุดความรู้ (core/knowledge_pack.py) ต้องตรวจย้อนได้

เดิม tests/test_hotlines.py ไม่ได้อ่านไฟล์ชุดความรู้ เบอร์ต่างประเทศ (RAINN, NSPCC ฯลฯ) เลยไม่เคยผ่านทะเบียน
และเคยเขียน "หมอหนี้ 1443" ทั้งที่ 1443 คือคลินิกแก้หนี้ของ SAM · "เด็กอายุต่ำกว่า 15 ปี" ทั้งที่ ม.277 คือ "ไม่เกิน 15 ปี"
"""
import pytest

from core import hotlines as hl
from core import knowledge_pack as kp
from core import knowledge_pack_facts as kf
from core.kernel_voice import compose


@pytest.mark.parametrize("entry", kp.PACK, ids=[e[0] for e in kp.PACK])
def test_every_phone_number_is_in_the_hotline_registry(entry):
    unknown = kf.phones(kf.answer_text(entry)) - hl.all_numbers()
    assert not unknown, f"{entry[0]}: เบอร์ {sorted(unknown)} ไม่อยู่ใน core/hotlines.py — ตรวจกับเว็บทางการแล้วเพิ่ม"


@pytest.mark.parametrize("entry", kp.PACK, ids=[e[0] for e in kp.PACK])
def test_every_number_is_in_the_facts_registry(entry):
    missing = kf.numbers(kf.answer_text(entry)) - kf.keys_for(entry[0])
    assert not missing, f"{entry[0]}: ตัวเลข {sorted(missing)} ยังไม่อยู่ใน core/knowledge_pack_facts.py — เพิ่มพร้อมแหล่งอ้างอิง"


def test_registry_has_no_stale_entries():
    topics = {e[0]: kf.numbers(kf.answer_text(e)) for e in kp.PACK}
    for f in kf.FACTS:
        assert f.kind in kf.KIND_ORDER and f.claim and f.source
        if f.topic != "*":
            assert f.topic in topics, f.topic
            assert set(f.keys) <= topics[f.topic], (f.topic, set(f.keys) - topics[f.topic])


def test_extractor_reads_every_phone_format():
    t = "US 1-800-GAMBLER, UK GamCare 0808 8020 133 · text START to 678-678 · 88709 · โทร 1669 · ความดัน 180/120 · 600 บาท · 1,000 baht"
    assert kf.phones(t) == {"1-800-GAMBLER", "0808 8020 133", "678-678", "88709", "1669"}


def test_debt_numbers_are_named_correctly():
    out = compose("ติดพนันจนหมดเงินเดือน เป็นหนี้เยอะมาก") + compose("i've been gambling away my salary")
    th = next(e for e in kp.PACK if e[0] == "kp_gambling")
    text = " ".join(th[4][1])
    assert "คลินิกแก้หนี้ 1443" in text and "1213" in text and "หมอหนี้ 1443" not in text
    assert "1-800-GAMBLER" in out


def test_age_of_consent_matches_section_277():
    out = compose("ลูกสาว 14 มีแฟนอายุ 25")
    assert "ไม่เกิน 15 ปี" in out and "ต่ำกว่า 15 ปี" not in out
