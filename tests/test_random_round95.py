"""รอบสุ่ม 95: คำผิดตอนตกใจ: ไม่ใส่สระ คาราโอเกะ สะกดผิด"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['แมไมหายใจ ชวยดวย', 'ลกกลนยาไปทงแผง', 'บานไฟไหม ออกไมได', 'อยากตายแลว', 'สามตีหน ชวยดวย', 'mae mai hai jai chuay duay', 'yak tai laew', 'ban fai mai ok mai dai', 'mom not breating help', 'my sun swalowed bleech', 'i wnat to dye', 'somone breakin in my hous'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ไปกนขาวกน', 'mai pen rai', 'sabai dee mai', 'i luv u mom', 'going to the store brb'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
