"""ยาตีกัน: แยกสารจากชื่อที่คนพิมพ์ แล้วบอกคู่ที่ต้องระวัง"""
import pytest
from core import drug_pairs as dp
from core.kernel_voice import compose


@pytest.mark.parametrize("q,a,b,lvl", [
    ("กินวาร์ฟารินอยู่ ปวดหัวกินไอบูโพรเฟนได้ไหม", "warfarin", "ibuprofen", "danger"),
    ("กินทิฟฟี่กับพาราพร้อมกันได้ไหม", "paracetamol", "para_combo", "danger"),
    ("พ่อกินไอโซซอร์ไบด์ จะกินไวอากร้าได้ไหม", "nitrate", "pde5", "danger"),
    ("กินยาไทรอยด์กับแคลเซียมพร้อมกันได้ไหม", "levothyroxine", "binder", "caution"),
    ("can I take tramadol with sertraline", "tramadol", "ssri", "caution"),
    ("กิน simvastatin อยู่ หมอให้ clarithromycin กินด้วยกันได้ไหม", "simvastatin", "macrolide", "danger"),
    ("กิน losartan กับเกลือโลโซเดียมได้ไหม", "acei_arb", "potassium", "danger"),
])
def test_known_pairs(q, a, b, lvl):
    _, pairs = dp.check(q)
    assert any({x, y} == {a, b} and l == lvl for x, y, l, *_ in pairs)


def test_unknown_pair_says_list_incomplete():
    o = compose("กินพาราเซตามอลกับเมทฟอร์มินด้วยกันได้ไหม", footer=False)
    assert "ไม่ครบทุกคู่" in o and "เภสัชกร" in o


def test_single_or_no_question_not_triggered():
    assert dp.reply("กินพาราเซตามอลอยู่") is None
    assert dp.reply("ไปเที่ยวพารากอนมา") is None


def test_polypharmacy_asks_which_drugs():
    assert "ยาอะไรกับยาอะไร" in compose("แม่อายุ 75 กินยาหลายตัวมาก กลัวยาตีกัน", footer=False)


def test_english_reply_uses_english_names():
    o = compose("can I take tramadol with sertraline", footer=False)
    assert "SSRI antidepressant" in o and "ยาต้านเศร้า" not in o
