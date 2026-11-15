"""รอบสุ่ม 38: แท็กซี่ล็อกประตู · ใส่ยาในเครื่องดื่ม · กลิ่นแก๊ส ใน id fr de pt ru"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['sopir taksi mengunci pintu dan tidak mau menurunkan saya', 'ada orang asing memasukkan sesuatu ke minuman saya, pusing sekali', 'bau gas sangat kuat di rumah', 'le chauffeur de taxi a verrouillé les portes et ne me laisse pas descendre', "un inconnu a mis quelque chose dans mon verre, j'ai la tête qui tourne", "ça sent fort le gaz dans l'appartement", 'der Taxifahrer hat die Türen verriegelt und lässt mich nicht aussteigen', 'ein Fremder hat mir etwas ins Getränk getan, mir ist sehr schwindelig', 'es riecht stark nach Gas in der Wohnung', 'o taxista trancou as portas e não me deixa sair', 'um estranho colocou algo na minha bebida, estou muito tonta', 'está com cheiro forte de gás em casa', 'таксист заблокировал двери и не выпускает меня', 'незнакомец подсыпал что-то в мой напиток, сильно кружится голова', 'в квартире сильно пахнет газом'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['harga gas naik lagi', 'le prix du gaz augmente', 'Gaspreise steigen', 'o preço do gás subiu', 'цены на газ выросли'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
