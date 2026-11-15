"""รอบสุ่ม 39: เป็นภาระ+ยกของ · ลูกทำร้ายตัวเอง ใน id fr de pt ru"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['saya tidak mau jadi beban lagi, semua barang sudah saya berikan', "je ne veux plus être un fardeau, j'ai donné toutes mes affaires", 'ich habe alle meine Sachen verschenkt und will niemandem mehr zur Last fallen', 'não quero mais ser um peso, dei todas as minhas coisas', 'я раздал все свои вещи, не хочу больше быть обузой', 'anak saya menyayat tangannya dan menutupinya dengan lengan panjang', 'ma fille se scarifie les bras', 'meine Tochter ritzt sich die Arme', 'minha filha está se cortando nos braços', 'моя дочь режет себе руки'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['saya berikan baju lama ke panti asuhan', "j'ai donné mes vieux vêtements à une association", 'ich habe alte Kleidung gespendet', 'doei roupas velhas para caridade', 'отдал старую одежду в благотворительность'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
