"""เรื่องด่วนในภาษาอื่น (เวียดนาม พม่า เขมร ลาว อาหรับ ฮินดี รัสเซีย ฯลฯ) เคยได้ Risk 0"""
import pytest

from core.kernel_voice import assess, compose

URGENT = ["mẹ tôi không thở được", "အမေ အသက်မရှူနိုင်ဘူး", "ប្តីវាយខ្ញុំ", "ແມ່ຫາຍໃຈບໍ່ໄດ້", "زوجي يضربني",
          "माँ साँस नहीं ले रही", "мама не дышит", "hindi makahinga ang nanay ko", "kocam beni dövüyor", "mia madre non respira"]
CRISIS = ["သေချင်တယ်", "ខ្ញុំចង់ស្លាប់", "ຂ້ອຍຢາກຕາຍ", "gusto ko nang mamatay", "saya nak mati", "voglio morire", "ölmek istiyorum"]
CALM = ["je veux mourir de rire", "hp ku mau mati", "aku tidak sadar kalau sudah malam", "necesito ayuda con mi tarea", "Привет как дела"]


@pytest.mark.parametrize("t", URGENT)
def test_world_urgent(t):
    assert assess(t)["text_risk"] >= 85, t
    assert "1)" in compose(t)


@pytest.mark.parametrize("t", CRISIS)
def test_world_crisis(t):
    assert assess(t)["crisis"], t


@pytest.mark.parametrize("t", ["救命", "助けて", "살려주세요", "ayuda", "помогите", "ကယ်ပါ"])
def test_world_help_word(t):
    assert assess(t)["text_risk"] >= 50, t


@pytest.mark.parametrize("t", CALM)
def test_world_calm(t):
    assert assess(t)["text_risk"] < 50, t
