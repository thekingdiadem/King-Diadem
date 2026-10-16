"""ภาษาจีน ญี่ปุ่น เกาหลี สเปน: ถูกขู่ฆ่า · ถูกขัง · ถูกหลอกโอนเงิน · ไม่มีอะไรกินหลายวัน — เคยได้ Risk 0 ทั้งสี่ภาษา"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text,kind,needle", [
    ("他说要杀了我", "violence", "110"), ("我被关在房间里", "violence", "110"), ("我被骗了转账", "scam", "转账"), ("我好饿，三天没吃饭", "basic", "12345"),
    ("殺すと脅された", "violence", "110"), ("詐欺にあった", "scam", "#9110"), ("三日間何も食べていない", "basic", "福祉"),
    ("죽인다고 협박받았어요", "violence", "112"), ("사기 당했어요", "scam", "112"), ("사흘 동안 아무것도 못 먹었어요", "basic", "129"),
    ("me amenazaron de muerte", "violence", "112"), ("me estafaron", "scam", "banco"), ("no he comido en tres días", "basic", "banco de alimentos"),
])
def test_urgent_in_other_languages(text, kind, needle):
    a = assess(text)
    assert a["text_risk"] >= 70 and kind in (a.get("intl_urgent") or [])
    assert needle in compose(text)
