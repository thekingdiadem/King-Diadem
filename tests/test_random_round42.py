"""รอบสุ่ม 42: ติดอยู่ในภัยพิบัติ + ถามวิธีเตรียมตัว ใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['水位が胸まで来た、祖母が歩けない、二階に閉じ込められている', '地震でエレベーターに閉じ込められた', '土砂崩れで隣の家が埋まった、下から声がする', '水已经淹到胸口了，奶奶走不动，被困在楼上', '地震了，我被困在电梯里', '山体滑坡埋了邻居家，下面有人在喊', '물이 가슴까지 찼어, 할머니가 못 걸어, 2층에 갇혔어', '지진 나서 엘리베이터에 갇혔어', '산사태로 옆집이 묻혔어, 밑에서 사람 소리가 나', 'el agua nos llega al pecho, mi abuela no puede caminar, estamos atrapados arriba', 'hubo un terremoto y estoy atrapado en el ascensor', 'un deslave sepultó la casa de al lado, se oyen gritos debajo', 'nước ngập tới ngực, bà không đi được, bị kẹt trên lầu', 'động đất, tôi bị kẹt trong thang máy', 'sạt lở đất vùi nhà hàng xóm, nghe tiếng người bên dưới'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['地震のニュースを見た', '地震来了怎么准备', '지진 대비 방법', 'cómo prepararse para un terremoto', 'cách chuẩn bị khi có động đất'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
