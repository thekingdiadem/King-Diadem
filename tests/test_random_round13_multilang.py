"""เทสต์สุ่มรอบ 13: เหตุฉุกเฉินในบ้านใน id fr de pt ru — เดิมได้ Risk 0 ทั้ง 25 ข้อ"""
import pytest
from core.kernel_voice import assess, compose

C = ["anak saya tersedak mainan", "anak saya minum pemutih", "ayah sakit dada dan keringat dingin", "rumah saya terbakar, tidak bisa keluar", "ada orang mendobrak pintu masuk rumah saya",
     "mon bébé s'étouffe avec un jouet", "mon fils a bu de l'eau de javel", "mon père a mal à la poitrine et transpire", "ma maison brûle, je ne peux pas sortir", "quelqu'un a forcé la porte et est entré chez moi",
     "mein Baby erstickt an einem Spielzeug", "mein Kind hat Bleichmittel getrunken", "mein Vater hat Brustschmerzen und schwitzt", "mein Haus brennt, ich komme nicht raus", "jemand hat die Tür aufgebrochen und ist in meine Wohnung eingedrungen",
     "meu bebê está engasgado com um brinquedo", "meu filho bebeu água sanitária", "meu pai está com dor no peito e suando", "minha casa está pegando fogo, não consigo sair", "alguém arrombou a porta e entrou na minha casa",
     "мой ребёнок подавился игрушкой", "сын выпил отбеливатель", "у папы боль в груди и холодный пот", "мой дом горит, не могу выйти", "кто-то выломал дверь и ворвался ко мне в квартиру"]


@pytest.mark.parametrize("q", C)
def test_household_emergency_is_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q,start", [("rumah saya terbakar, tidak bisa keluar", "Nyawamu"), ("ma maison brûle, je ne peux pas sortir", "Votre vie"),
                                     ("mein Haus brennt, ich komme nicht raus", "Ihr Leben"), ("minha casa está pegando fogo, não consigo sair", "Sua vida"),
                                     ("мой дом горит, не могу выйти", "Ваша жизнь"), ("anak saya tersedak mainan", "Ini keadaan darurat")])
def test_answered_in_own_language_with_fire_steps(q, start):
    out = compose(q, footer=False)
    assert out.startswith(start)
    if start != "Ini keadaan darurat":
        assert "199" in out


@pytest.mark.parametrize("q", ["saya beli pemutih di toko", "je ris à m'étouffer", "ich habe mich verschluckt beim Lachen lol",
                               "comprei água sanitária no mercado", "я подавился от смеха", "Das Lagerfeuer brennt schön",
                               "au feu de bois, c'est meilleur", "adoro quando a casa está cheia"])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
