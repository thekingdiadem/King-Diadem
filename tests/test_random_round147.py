"""รอบสุ่ม 147: ชีวิตไม่มีความหมาย (ja ko es vi) และจดหมายลา (es vi) — เคยได้ 0
(ประโยคเขียนเองในรอบนี้ ไม่ได้มาจากชุดปิดตา) · ระดับเท่ากับ 活着没有意义 / 遗书 ที่มีอยู่แล้ว"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "No le encuentro sentido a nada, estoy agotado de vivir", "Sống chẳng còn ý nghĩa gì, tôi mệt mỏi quá rồi",
    "살아야 할 이유를 모르겠어요", "もう生きる意味がわからない、疲れた",
    "Escribí una carta de despedida para mi familia", "Tôi đã viết thư từ biệt gia đình",
])
def test_meaningless_life_and_farewell_letters_are_heard(q):
    assert assess(q)["risk_shown"] >= 60


@pytest.mark.parametrize("q", [
    "Esta reunión no tiene sentido, qué pérdida de tiempo", "このゲームの意味がわからない", "이 문제를 푸는 이유를 모르겠어요",
    "Escribí una carta de despedida para mi compañero que se jubila", "Tôi viết thư từ biệt cho lớp học trước khi chuyển trường",
])
def test_everyday_meaning_and_goodbyes_stay_calm(q):
    assert assess(q)["risk_shown"] < 60


def test_tired_of_living_in_a_place_is_not_a_crisis():
    """"cansado de vivir en esta ciudad" = เบื่อการอยู่ในเมืองนี้ ไม่ใช่อยากตาย (เทสต์เดิม test_passive_ideation_intl จับได้)"""
    assert assess("Estoy cansada de vivir en esta ciudad tan cara")["risk_shown"] < 60
