"""รอบสุ่ม 49: คนท้อง/หลังคลอด/ทารกใน id fr de pt ru"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['anak saya tersedak permen, tidak bisa bernapas', 'bayi saya demam padahal baru 2 minggu', 'istri saya hamil 8 bulan sakit kepala hebat dan pandangan kabur', 'mon bébé de 2 semaines a de la fièvre', 'enceinte de 8 mois, mal de tête violent et vision floue', "après l'accouchement je remplis une serviette chaque heure", 'mein 2 Wochen altes Baby hat Fieber', 'schwanger im 8. Monat, starke Kopfschmerzen und verschwommenes Sehen', 'nach der Geburt blute ich jede Stunde eine Binde durch', 'meu bebê de 2 semanas está com febre', 'grávida de 8 meses com dor de cabeça forte e visão embaçada', 'depois do parto encho um absorvente por hora', 'мой ребёнок двух недель с температурой', 'беременность 8 месяцев, сильная головная боль и всё плывёт перед глазами', 'после родов прокладка промокает каждый час'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['bayi saya tidur nyenyak', "je suis enceinte et j'ai des envies", 'Babynahrung Empfehlungen', 'grávida e com desejos', 'беременность протекает хорошо'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60


def test_german_im_is_not_rewritten_as_english_im():
    from core.thai_signals import canon_text
    assert canon_text("schwanger im 8. Monat") == "schwanger im 8. Monat"
    assert canon_text("im so tired u know") == "i'm so tired you know"
