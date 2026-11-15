"""รอบสุ่ม 83: หอบหืด/อาหารติดคอใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['喘息の発作で吸入薬が効かない、数語しか話せない', '哮喘发作，喷了药也没用，只能说几个字', '천식 발작인데 흡입기가 안 들어, 몇 마디밖에 못 해', 'ataque de asma, el inhalador no funciona, solo puedo decir unas palabras', 'lên cơn hen, xịt thuốc không đỡ, chỉ nói được vài từ', '父が食べ物を喉に詰まらせて咳もできない、顔が青い', '爸爸吃东西噎住了，咳不出来，脸发紫', '아빠가 음식이 목에 걸려서 기침도 못 하고 얼굴이 파래', 'mi papá se atragantó con comida, no puede toser, se está poniendo azul', 'bố bị hóc thức ăn, không ho được, mặt tím tái'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['喘息だけど薬で落ち着いた', '有点哮喘，喷药后好了', '천식 약 먹고 괜찮아졌어', 'asma leve, ya estoy bien', 'hen nhẹ, xịt thuốc đỡ rồi'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
