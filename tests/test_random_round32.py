"""รอบสุ่ม 32: ถูกน้ำพัด · แก๊สรั่ว · เด็กในรถร้อน ใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['川で子供が流された', 'ガス臭い、部屋中', '赤ちゃんを車に置き忘れた、暑い', '孩子被河水冲走了', '家里有很浓的煤气味', '把宝宝忘在车里了，很热', '아이가 강물에 떠내려갔어', '집에서 가스 냄새가 심하게 나', '아기를 더운 차 안에 두고 왔어', 'la corriente se llevó a mi hijo en el río', 'huele mucho a gas en la casa', 'dejé al bebé en el coche al sol', 'con tôi bị nước cuốn trôi', 'nhà có mùi gas rất nặng', 'tôi bỏ quên em bé trong xe nóng'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['川で遊んだ、楽しかった', 'ガス代が高い', '今天去河边玩了', '가스비가 너무 비싸', 'el precio del gas subió', 'hôm nay đi chơi ở sông'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["con tôi bị nước cuốn trôi", "tôi bỏ quên em bé trong xe nóng"])
def test_vietnamese_guessed_as_en_or_es_still_answered_in_vietnamese(q):
    from core.kernel_voice import compose
    assert compose(q, footer=False).startswith("Đây là tình huống khẩn cấp")
