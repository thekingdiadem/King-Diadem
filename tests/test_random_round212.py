"""รอบสุ่ม 212: ภาษาต่างประเทศ (es vi ko ja zh) — เรื่องด่วน 10 แบบ และเรื่องธรรมดาที่ใช้คำคล้ายกัน 10 แบบ ระบบแยกได้ครบ ล็อกไว้ไม่ให้ถอยหลัง"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "Mi hijo se tragó una pila de botón", "Bố tôi đột nhiên méo miệng, nói ngọng, tay yếu", "아기가 열이 나고 경련을 해요",
    "おじいちゃんが急にろれつが回らなくなった", "我爸胸口剧痛，出冷汗", "Mi novio me amenazó con un cuchillo",
    "Chồng tôi đánh tôi, tôi đang trốn trong nhà tắm", "남편이 때려서 피가 나요", "彼氏に殴られて逃げてきた", "有人一直跟踪我到家门口",
])
def test_urgent_in_other_languages(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "Mi hijo compró pilas nuevas para el control", "Bố tôi đang nói chuyện điện thoại", "아기가 낮잠을 잘 자요",
    "おじいちゃんが畑で野菜を作ってる", "我爸今天去爬山了", "Mi novio me regaló un cuchillo de cocina",
    "Chồng tôi nấu ăn rất ngon", "남편이 요리했어요", "彼氏とケンカしたけど仲直りした", "有人在门口送快递",
])
def test_everyday_in_other_languages(q):
    assert assess(q)["risk_shown"] < 60
