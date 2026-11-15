"""รอบสุ่ม 46: สัตว์เลี้ยงฉุกเฉินใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['犬がチョコレートを一枚全部食べて震えている', '猫が花瓶のユリをかじった', '犬のお腹がパンパンに膨れて吐こうとしても何も出ない', '狗吃了一整块巧克力在发抖', '猫咬了花瓶里的百合', '狗肚子胀得很大，想吐又吐不出来', '강아지가 초콜릿을 한 판 다 먹고 떨고 있어', '고양이가 꽃병의 백합을 씹었어', '강아지 배가 빵빵하게 부풀고 토하려는데 아무것도 안 나와', 'mi perro se comió una barra entera de chocolate y está temblando', 'mi gato mordió un lirio del florero', 'la panza de mi perro está muy hinchada e intenta vomitar pero no sale nada', 'chó tôi ăn hết cả thanh sô cô la và đang run', 'mèo tôi cắn hoa ly trong bình', 'bụng chó căng phồng, cố nôn mà không ra gì'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['犬がおやつを食べた', '猫がユリの近くで寝てる', '狗狗吃了狗粮', '강아지가 산책을 좋아해', 'mi gato duerme mucho', 'chó tôi thích đi dạo'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
