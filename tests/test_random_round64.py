"""รอบสุ่ม 64: ยาทั้งขวด/ตกนั่งร้านใน it tr ar hi tl ms"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['mio figlio ha bevuto tutta la bottiglia di sciroppo per la tosse', "un collega è caduto dall'impalcatura", 'oğlum bütün öksürük şurubunu içti', 'iş arkadaşım iskeleden düştü', 'ابني شرب زجاجة دواء الكحة كلها', 'زميلي سقط من السقالة', 'बेटे ने खांसी की पूरी बोतल पी ली', 'मेरा साथी मचान से गिर गया', 'ininom ng anak ko ang buong bote ng gamot sa ubo', 'nahulog sa scaffolding ang katrabaho ko', 'anak saya minum sebotol penuh ubat batuk', 'rakan sekerja jatuh dari perancah'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['mio figlio ha la tosse', 'oğlum öksürüyor', 'ابني عنده كحة', 'बेटे को खांसी है', 'may ubo ang anak ko', 'anak saya batuk sikit'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
