"""เทสต์สุ่มรอบ 11: มีคนพังประตูบุกเข้าบ้าน — เดิมได้ Risk 0 ทั้ง 5 ภาษา (เดี่ยวๆ และระหว่างทำกิจกรรม)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "誰かがドアをこじ開けて入ってきた", "ドラマを見ていたら、誰かがドアをこじ開けて入ってきた",
    "有人撬开门闯进我家", "玩游戏的时候，有人撬开门闯进我家",
    "누가 문을 부수고 들어왔어", "게임하다가 누가 문을 부수고 들어왔어",
    "alguien entró a la fuerza en mi casa", "viendo una serie, alguien entró a la fuerza en mi casa",
    "có người phá cửa xông vào nhà tôi", "Đang xem phim thì có người phá cửa xông vào nhà tôi",
])
def test_break_in_is_heard(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ゲームで敵がドアを壊して入ってきた笑", "我把门撬开了，因为钥匙丢了", "문을 따고 들어왔어 열쇠를 잃어버려서",
                               "entré a la fuerza en mi casa porque perdí las llaves", "Tôi phá cửa vào nhà vì mất chìa khóa"])
def test_locked_out_of_own_home_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
