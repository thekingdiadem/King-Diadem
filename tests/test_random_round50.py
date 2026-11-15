"""รอบสุ่ม 50: พิมพ์ตกใจ อีโมจิ หลายภาษา (กันถอยหลัง)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['タクシーがドアをロックした😭助けて', '赤ちゃんを車に置き忘れた!!!暑い', '出租车把门锁了😭救命', '宝宝被玩具卡住喉咙!!!', '택시가 문을 잠갔어ㅠㅠ 살려줘', '아기가 장난감이 목에 걸렸어!!!', 'el taxi cerró las puertas 😭 ayuda', 'mi bebé se atragantó!!!', 'tài xế khóa cửa 😭 cứu', 'em bé bị hóc!!!', 'mein Haus brennt!!! 😱', 'ma maison brûle!!!'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['タクシー遅い😂', '宝宝好可爱😍', '택시 기다리는 중ㅋㅋ', 'el taxi llegó tarde jaja', 'đợi taxi lâu quá 😅'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
