"""รอบสุ่ม 51: อุบัติเหตุรุนแรงใน id fr de pt ru"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['saya menabrak pejalan kaki, dia tidak bergerak', 'jatuh dari tangga, kaki tidak terasa', 'jari saya putus kena gergaji', "j'ai renversé un piéton, il ne bouge plus", "je suis tombé de l'échelle, je ne sens plus mes jambes", 'je me suis coupé le doigt avec la scie, il est tombé', 'ich habe einen Fußgänger angefahren, er bewegt sich nicht', 'bin von der Leiter gefallen und spüre meine Beine nicht', 'habe mir mit der Säge einen Finger abgeschnitten', 'atropelei um pedestre, ele não se mexe', 'caí da escada e não sinto as pernas', 'cortei o dedo fora com a serra', 'я сбил пешехода, он не двигается', 'упал с лестницы, не чувствую ног', 'отрезал палец пилой'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['saya jatuh tapi cuma lecet', 'je suis tombé mais ça va', 'bin gestolpert, alles gut', 'caí mas estou bem', 'упал, но всё нормально'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
