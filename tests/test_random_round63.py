"""รอบสุ่ม 63: ค้ามนุษย์/ติดในน้ำท่วมใน it tr ar hi tl ms"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['il capo ha preso il mio passaporto e non mi lascia tornare a casa', "l'acqua ci arriva al petto, siamo bloccati al piano di sopra", 'patronum pasaportumu aldı ve eve gitmeme izin vermiyor', 'su göğsümüze kadar geldi, üst katta mahsur kaldık', 'المدير أخذ جواز سفري ولا يسمح لي بالعودة', 'الماء وصل إلى صدورنا ونحن محاصرون في الطابق العلوي', 'मालिक ने मेरा पासपोर्ट रख लिया और घर नहीं जाने देता', 'पानी छाती तक आ गया है, हम ऊपर फंसे हैं', 'kinuha ng amo ang pasaporte ko at ayaw akong pauwiin', 'hanggang dibdib na ang tubig, naiipit kami sa itaas', 'majikan ambil pasport saya dan tak bagi balik', 'air dah paras dada, kami terperangkap di tingkat atas'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ho rinnovato il passaporto', 'pasaportumu yeniledim', 'جددت جواز سفري', 'पासपोर्ट बनवा लिया', 'nag-renew ako ng pasaporte', 'saya renew pasport'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
