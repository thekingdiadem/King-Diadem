"""รอบสุ่ม 84: หอบหืด/อาหารติดคอในอีก 11 ภาษา"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['serangan asma, inhaler tidak membantu, hanya bisa bicara beberapa kata', "crise d'asthme, la ventoline ne marche pas, je ne peux dire que quelques mots", 'Asthmaanfall, das Spray hilft nicht, kann nur wenige Worte sprechen', 'crise de asma, a bombinha não funciona, só consigo falar algumas palavras', 'приступ астмы, ингалятор не помогает, могу сказать только пару слов', 'mio padre si sta strozzando col cibo, non riesce a tossire, diventa blu', 'babam yemekte boğuluyor, öksüremiyor, morarıyor', 'أبي يختنق بالطعام ولا يستطيع السعال وأصبح أزرق', 'पापा के गले में खाना फंस गया, खांस नहीं पा रहे, नीले पड़ रहे', 'nabulunan sa pagkain ang tatay ko, hindi makaubo, nangingitim', 'ayah tercekik makanan, tak boleh batuk, muka jadi biru'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['asma ringan, sudah baikan', "un peu d'asthme, ça va", 'leichtes Asthma, alles gut', 'asma leve, já passou', 'лёгкая астма, всё нормально'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
