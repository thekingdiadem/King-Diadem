"""ภาษาอื่นของเว็บ (es vi zh ko ja): เรื่องที่ฉบับไทย/อังกฤษจับได้แล้ว แต่ภาษาอื่นเคยหลุด 9 จาก 20"""
import pytest
from core.kernel_voice import assess

REAL = ["alguien está golpeando mi puerta a las 3 am", "có người lạ đập cửa nhà tôi lúc 2 giờ sáng", "con tôi nuốt pin",
        "我老公每天晚上打我", "半夜有陌生人砸我家门", "새벽 2시에 모르는 사람이 문을 두드려요", "夫が毎晩殴ってくる",
        "夜中に知らない人がドアを叩いている", "母が転んで起き上がれない",
        "mi esposo me pega todas las noches", "chồng tôi đánh tôi mỗi đêm", "남편이 매일 밤 때려요"]
CALM = ["alguien está golpeando la puerta, es el cartero", "bạn tôi gõ cửa lúc 2 giờ chiều", "我老公每天晚上打游戏", "半夜邻居家砸核桃",
        "새벽에 택배 기사님이 문을 두드려요", "夫が毎晩ゲームしてる", "夜中に猫がドアを叩いている", "母が転んだけど大丈夫だった",
        "con tôi thay pin", "mi esposo toca la batería todas las noches", "笑死我了", "死ぬほど眠い"]


@pytest.mark.parametrize("t", REAL)
def test_danger_in_other_languages_is_caught(t):
    assert assess(t)["risk_shown"] >= 80


@pytest.mark.parametrize("t", CALM)
def test_everyday_in_other_languages_is_calm(t):
    assert assess(t)["risk_shown"] < 60
