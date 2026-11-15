"""รอบสุ่ม 45: สัญญาณหลังคำปลอบใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['大丈夫だよ、どうせすぐにみんな楽になるから', '全部大丈夫、母への手紙ももう書いた', '明日オンラインにいなくても探さないでね笑', '没事啦，反正很快大家就都轻松了', '一切都好，给妈妈的信已经写好了', '明天要是看不到我在线，别找我哈', '괜찮아, 어차피 곧 다들 편해질 거야', '다 괜찮아, 엄마한테 편지도 다 썼어', '내일 내가 접속 안 해도 찾지 마 ㅋㅋ', 'estoy bien, total pronto todos van a estar mejor', 'todo bien, ya le escribí la carta a mi mamá', 'si mañana no me ves conectada no me busques jaja', 'không sao đâu, dù sao mọi người cũng sắp nhẹ nhõm rồi', 'mọi thứ ổn, mình đã viết thư cho mẹ rồi', 'mai không thấy mình online thì đừng tìm nhé'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['大丈夫、明日旅行で山に行くから圏外', '母の日の手紙を書いた', '明天去露营没信号', '엄마 생신 편지 썼어', 'mañana voy al campamento, sin señal', '母に手紙を書いた', '给妈妈写了一封信', '엄마한테 편지 썼어', 'le escribí una carta a mi mamá', 'viết thư cho mẹ', 'no me busques en la fiesta jaja estaré en la cocina'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
