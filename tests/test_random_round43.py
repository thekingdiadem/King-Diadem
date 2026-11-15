"""รอบสุ่ม 43: อุบัติเหตุรุนแรงใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['車で歩行者をはねた、動かない', 'はしごから落ちて足の感覚がない', 'のこぎりで指を切り落とした', '开车撞到行人了，他一动不动', '从梯子上摔下来，腿没有知觉了', '锯子把手指锯断了', '차로 보행자를 쳤어, 안 움직여', '사다리에서 떨어졌는데 다리에 감각이 없어', '톱에 손가락이 잘렸어', 'atropellé a un peatón y no se mueve', 'me caí de la escalera y no siento las piernas', 'me corté un dedo con la sierra, se desprendió', 'tôi tông phải người đi bộ, họ không cử động', 'ngã từ thang xuống, không cảm thấy chân', 'bị cưa đứt ngón tay'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['車をぶつけた、バンパーがへこんだだけ', '摔了一跤，膝盖擦破点皮', '넘어져서 무릎이 까졌어', 'choqué el coche, solo un rayón', 'té xe, chỉ trầy xước nhẹ'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
