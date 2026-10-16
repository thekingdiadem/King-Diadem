"""พิมพ์แบบคนจริง: ไม่ใส่วรรณยุกต์ · เว้นวรรคทุกตัว · "ม่" แทน "ไม่" · "ลุก" แทน "ลูก" — เรื่องด่วนต้องไม่หลุด และเรื่องธรรมดาต้องไม่ตื่นตูม"""
import pytest

from core.kernel_voice import assess
from core.thai_signals import normalize_mixed, retone


@pytest.mark.parametrize("text,min_risk", [
    ("อ ย า ก ต า ย", 95), ("ม่อยากมีชีวิตอยู่แล้ว", 95), ("ไมอยากมีชีวิตอยูแลว", 95), ("อยากฆาตัวตาย", 95),
    ("ลูกไมหายใจ", 85), ("ลูกม่หายใจ", 85), ("ล ู ก ไ ม ่ ห า ย ใ จ", 85), ("เลือดออกไมหยุด", 85), ("ลุกชัก", 85),
    ("ถูกขมขืน", 75), ("พอเจ็บหนาอก", 85), ("ยายปากเบียว พูดไมชัด", 85), ("ถูกขังไวในหอง", 75),
])
def test_hurried_typing_still_gets_help(text, min_risk):
    assert assess(text)["text_risk"] >= min_risk


@pytest.mark.parametrize("text", ["อานขาวคนถูกแทงแลวสะเทือนใจ", "อยากหายไปเทียวทะเล", "แมวกัดเลนไมเขาเนือ", "หิวจะตาย", "ไปกินขาวกัน"])
def test_toneless_everyday_text_stays_calm(text):
    a = assess(text)
    assert not a["crisis"] and a["text_risk"] < 60


@pytest.mark.parametrize("text", ["ใหม่กว่า", "แม่ไปตลาด", "สีม่วง", "ผ้าม่าน", "ลุกไม่ขึ้น", "สวัสดีครับ"])
def test_repair_leaves_real_words_alone(text):
    assert normalize_mixed(text) == text


def test_retone_never_breaks_words_without_tones():
    assert retone("อยากตาย") == "อยากตาย"
