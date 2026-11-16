"""รอบสุ่ม 79: หลงภูเขา/ลูกหายใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['山で道に迷った、暗くなって水もない', '人混みのショッピングモールで子供がいなくなった、30分探している', '在山上迷路了，天黑了，没水了', '在人多的商场里孩子走丢了，找了半小时', '산에서 길을 잃었어, 어두워졌고 물도 없어', '사람 많은 쇼핑몰에서 아이를 잃어버렸어, 30분째 찾고 있어', 'me perdí en la montaña, ya oscureció y no tengo agua', 'perdí a mi hijo en un centro comercial lleno, lo busco hace 30 minutos', 'bị lạc trên núi, trời tối rồi, hết nước', 'con tôi bị lạc trong trung tâm thương mại đông người, tìm 30 phút rồi'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['山登り楽しかった', '商场打折', '쇼핑몰 구경했어', 'fui de compras al centro comercial', 'đi siêu thị mua đồ'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
