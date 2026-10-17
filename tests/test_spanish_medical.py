"""ประโยคสเปนสั้นๆ ที่ไม่มีสระเครื่องหมาย ("mi madre no respira") เคยถูกเดาเป็นอังกฤษ → Risk 0 ไม่มีขั้นช่วยชีวิต"""
import pytest

from core.kernel_voice import assess, compose
from core.lang_signals import detect_lang


@pytest.mark.parametrize("t", ["mi madre no respira", "mi hijo no despierta", "mi abuela no reacciona",
                               "mi padre no responde", "mi padre sangra mucho"])
def test_short_spanish_emergency_is_caught_in_spanish(t):
    assert detect_lang(t) == "es"
    assert assess(t)["text_risk"] >= 50
    assert "112" in compose(t) or "911" in compose(t)


@pytest.mark.parametrize("t", ["mi novio no responde mis mensajes", "the madre restaurant is great"])
def test_not_an_emergency(t):
    assert assess(t)["text_risk"] < 50
