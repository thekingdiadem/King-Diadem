"""รอบสุ่ม 48: คนท้อง/หลังคลอด/ทารกใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['妊娠8ヶ月、ひどい頭痛と目がかすむ、足がむくむ', '生後2週間の赤ちゃんが熱があってミルクを飲まない', '出産後、1時間ごとにナプキンがびっしょり', '怀孕8个月，头很痛，看东西模糊，脚肿', '两周大的宝宝发烧不吃奶', '产后每小时都要换湿透的卫生巾', '임신 8개월인데 두통이 심하고 눈이 침침하고 발이 부어', '생후 2주 아기가 열이 나고 젖을 안 먹어', '출산 후 한 시간마다 패드가 흠뻑 젖어', 'tengo 8 meses de embarazo, dolor de cabeza fuerte, visión borrosa y pies hinchados', 'mi bebé de 2 semanas tiene fiebre y no quiere comer', 'después del parto empapo una toalla cada hora', 'mang thai 8 tháng, đau đầu dữ dội, mờ mắt, phù chân', 'con 2 tuần tuổi bị sốt, không chịu bú', 'sau sinh cứ mỗi giờ lại thấm đẫm băng vệ sinh'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['妊娠5ヶ月、つわりが少し', '宝宝睡得很多正常吗', '임신 중 먹으면 좋은 음식', 'estoy embarazada y tengo antojos', 'bé ngủ nhiều có sao không'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
