"""BIO-AXIOM: พันธุกรรมของสัตว์ใน world model ต่อเข้าแชท"""
import pytest
from WORLD_MODEL import bio_axiom as B
from WORLD_MODEL.small_animal_model import SMALL_ANIMALS
from core.kernel_voice import compose


def test_every_small_animal_has_genetics_entry():
    """ทุกสัตว์ในทะเบียนสัตว์เล็กต้องมีข้อมูลพันธุกรรม (ตัวเลขหรือ None ที่บอกว่าต่างตามชนิด)"""
    missing = [k for k in SMALL_ANIMALS if k not in B.ANIMALS]
    assert not missing, missing


def test_chromosome_values_are_sane():
    for k, a in B.ANIMALS.items():
        assert a["chromosomes"] is None or 4 <= a["chromosomes"] <= 120, k
        assert a["sex"] in (None, "XY", "ZW", "haplodiploid", "TSD"), k
    assert B.VERIFIED is False                      # ยังไม่มีผู้เชี่ยวชาญตรวจ


@pytest.mark.parametrize("q,must", [
    ("แมวสามสีทำไมเป็นตัวเมีย", "โครโมโซม X"),
    ("หมามีโครโมโซมกี่แท่ง", "78 แท่ง"),
    ("ล่อทำไมเป็นหมัน ม้าผสมลา", "63 แท่ง"),
    ("ไก่กำหนดเพศยังไง", "ZW"),
    ("why are calico cats female", "two X chromosomes"),
    ("เม่นแคระมีโครโมโซมกี่แท่ง", "ต่างกันตามชนิด"),
])
def test_genetics_answers(q, must):
    assert must in compose(q, footer=False)


@pytest.mark.parametrize("q", ["หมาข้างบ้านเห่าทั้งคืน", "แมวป่วย ไม่กินข้าว", "ขอลาออกจากงาน"])
def test_not_triggered_without_genetics_question(q):
    assert B.reply(q) is None
