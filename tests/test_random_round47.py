"""รอบสุ่ม 47: อุบัติเหตุในที่ทำงานใน ja zh ko es vi"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['工場で同僚が足場から落ちた', 'クレーンが人の上に倒れた', '機械に同僚の腕が巻き込まれた', '同事从脚手架上摔下来了', '吊车倒下压到人了', '机器把同事的手臂卷进去了', '동료가 비계에서 떨어졌어', '크레인이 사람 위로 넘어졌어', '기계에 동료 팔이 말려 들어갔어', 'mi compañero se cayó del andamio', 'la grúa cayó encima de alguien', 'la máquina atrapó el brazo de mi compañero', 'đồng nghiệp ngã từ giàn giáo', 'cần cẩu đổ đè lên người', 'máy cuốn tay đồng nghiệp vào'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['株価が落ちた', '同事升职了', '동료랑 점심 먹었어', 'mi compañero renunció', 'đồng nghiệp nghỉ phép'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
