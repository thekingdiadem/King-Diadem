"""เรื่องด่วนที่ซ่อนท้ายเรื่องเล่ายาวๆ ต้องไม่หลุด"""
import pytest

from core.kernel_voice import assess


@pytest.mark.parametrize("text", [
    "วันนี้ไปทำงานปกติ หัวหน้าดุนิดหน่อย กลับบ้านมากินข้าว แล้วก็คิดว่าคืนนี้จะกินยาให้หมดแผงเลย",
    "เรื่องเงินก็เครียด เรื่องงานก็เครียด แฟนก็ทิ้ง ไม่รู้จะอยู่ไปทำไม",
])
def test_buried_self_harm_is_a_crisis(text):
    assert assess(text)["crisis"]


@pytest.mark.parametrize("text", ["จะกินยาให้หมดแผงตามหมอสั่ง", "ไม่รู้จะอยู่บ้านทำไม ว่างมาก"])
def test_ordinary_sentences_are_not(text):
    assert not assess(text)["crisis"]
