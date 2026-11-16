"""รอบสุ่ม 61: สโตรก/สำลักใน it tr ar hi tl ms"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['mio padre parla in modo confuso e non riesce ad alzare il braccio sinistro', 'mio figlio sta soffocando con un giocattolo', 'babam anlamsız konuşuyor ve sol kolunu kaldıramıyor', 'oğlum oyuncakla boğuluyor', 'أبي يتكلم كلامًا غير مفهوم ولا يستطيع رفع ذراعه اليسرى', 'ابني يختنق بلعبة', 'पापा उल्टा-सीधा बोल रहे हैं और बायां हाथ नहीं उठा पा रहे', 'मेरा बेटा खिलौने से घुट रहा है', 'ang tatay ko ay hindi maintindihan magsalita at hindi maiangat ang kaliwang braso', 'nabulunan ang anak ko', 'ayah cakap merepek dan tak boleh angkat tangan kiri', 'anak saya tercekik mainan'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['mio padre parla tanto', 'babam çok konuşuyor', 'أبي يحب الكلام', 'पापा बहुत बात करते हैं', 'madaldal ang tatay ko', 'ayah suka bercakap'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
