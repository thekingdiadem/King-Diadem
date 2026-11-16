"""รอบสุ่ม 62: คนท้อง/ทารกใน it tr ar hi tl ms"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['incinta di 8 mesi, forte mal di testa e vista offuscata', 'il mio bambino di 2 settimane ha la febbre', '8 aylık hamileyim, şiddetli baş ağrısı ve bulanık görme', '2 haftalık bebeğim ateşlendi', 'حامل في الشهر الثامن وصداع شديد ورؤية ضبابية', 'طفلي عمره أسبوعان وعنده حمى', '8 महीने की गर्भवती हूं, तेज़ सिरदर्द और धुंधला दिख रहा है', 'मेरा 2 हफ्ते का बच्चा बुखार में है', '8 buwan akong buntis, matinding sakit ng ulo at malabo ang paningin', 'nilalagnat ang 2 linggong sanggol ko', 'hamil 8 bulan, sakit kepala teruk dan penglihatan kabur', 'bayi saya 2 minggu demam'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['incinta e ho voglia di gelato', 'hamileyim ve çok mutluyum', 'أنا حامل وسعيدة', 'मैं गर्भवती हूं और खुश हूं', 'buntis ako at masaya', 'saya hamil dan gembira'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
