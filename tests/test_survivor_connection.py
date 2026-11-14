"""ทุกคนไม่จำเป็นต้องอยู่คนเดียวตลอด และไม่จำเป็นต้องอยู่กับผู้อื่นตลอด"""
from ENGINE.realhuman_survivorengine import read_connection, RealHumanSurvivorEngine, HumanState
from core.kernel_voice import compose


def test_read_connection_both_sides():
    assert read_connection("ไม่ได้คุยกับใครมาสองอาทิตย์แล้ว เหงามาก") == "isolated"
    assert read_connection("อยู่กับคนทั้งวัน ไม่มีเวลาของตัวเองเลย อยากอยู่คนเดียวบ้าง") == "crowded"
    assert read_connection("I need some space, people all day") == "crowded"
    assert read_connection("เหงามาก แต่ก็อยากอยู่คนเดียว") is None
    assert read_connection("วันนี้กินข้าวอะไรดี") is None


def test_run_with_connection_adds_flag():
    out = RealHumanSurvivorEngine().run_with_connection(HumanState(), text="ไม่ได้คุยกับใครมาสองอาทิตย์แล้ว เหงามาก")
    assert out.connection == "isolated"
    assert "ISOLATED" in out.context_for_lyla
    out2 = RealHumanSurvivorEngine().run_with_connection(HumanState(), text="อยู่กับคนทั้งวัน อยากอยู่คนเดียวบ้าง")
    assert "NO_SOLITUDE" in out2.context_for_lyla


def test_kernel_respects_solitude_and_loneliness():
    a = compose("อยู่กับคนทั้งวัน ไม่มีเวลาของตัวเองเลย อยากอยู่คนเดียวบ้าง", footer=False)
    assert "ไม่จำเป็นต้องอยู่กับผู้อื่นตลอด" in a and "ความเหงาบอกว่า" not in a
    assert "nobody has to be with others" in compose("I need some space, people all day", footer=False)
    # สัญญาณอันตรายไม่ถูกตอบแบบ "อยากมีพื้นที่ส่วนตัว"
    c = compose("ไม่อยากเจอใครอีกแล้ว อยากหายไปจากโลก", footer=False)
    assert "ไม่จำเป็นต้องอยู่กับผู้อื่นตลอด" not in c
