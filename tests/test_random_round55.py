"""รอบสุ่ม 55: ผู้สูงอายุฉุกเฉินใน id fr de pt ru"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['nenek jatuh di kamar mandi tidak bisa bangun, tinggal sendiri', 'ayah diabetes, berkeringat, linglung, tidak menjawab', 'kakek pikun keluar rumah dari pagi belum pulang', 'ma grand-mère est tombée dans la salle de bain et ne peut pas se relever', 'mon père est diabétique, il transpire, il est confus et répond à peine', "mon grand-père atteint d'Alzheimer est parti ce matin et n'est pas revenu", 'Oma ist im Bad gestürzt und kommt nicht hoch', 'Papa ist Diabetiker, schwitzt, ist verwirrt und reagiert kaum', 'Opa mit Demenz ist seit heute früh weg', 'minha avó caiu no banheiro e não consegue levantar', 'meu pai é diabético, está suando, confuso e quase não responde', 'meu avô com demência saiu de manhã e não voltou', 'бабушка упала в ванной и не может встать', 'папа диабетик, потеет, спутанное сознание, почти не отвечает', 'дедушка с деменцией ушёл утром и не вернулся'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['nenek jalan-jalan ke pasar', 'ma grand-mère fait du jardinage', 'Oma backt Kuchen', 'meu avô foi pescar', 'дедушка пошёл на рыбалку'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
