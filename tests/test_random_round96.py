"""รอบสุ่ม 96: คาราโอเกะ/สะกดผิดเพิ่มเติม"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ma mai hai jai, chuay duay', 'look kin ya ma laew pen sib med', 'sami tee chan tuk keun', 'dek jom nam mai hai jai', 'pls help my dad cant breath', 'my frend took to many pils', 'ther is a fire in my apartmnt, cant get out', 'my husbnd hits me evry night'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ma kin kao gan', 'look sao suay mak', 'tee nee arai', 'my frend is coming over', 'took my pills as usual'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
