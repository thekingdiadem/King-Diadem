"""เทสต์สุ่มรอบ 9: เหตุฉุกเฉินจริงที่เกิดระหว่างดูละคร/ซีรีส์/สารคดี — เดิมถูกลดเหลือ 20 เพราะคำว่า "ละคร" """
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "นั่งดูละครกับพ่อ พ่อเจ็บหน้าอก เหงื่อแตก หายใจไม่ออก", "ดูสารคดีอยู่ ลูกสำลักของเล่น หายใจไม่ได้",
    "ดูซีรีส์อยู่ แฟนเมากลับมาต่อยหน้าเรา เลือดออก", "ดูซีรีส์อยู่กับแม่ จู่ๆ แม่ล้มหัวฟาดพื้น ไม่รู้สึกตัว",
    "we were watching a documentary when dad started slurring and his face drooped",
    "I was watching a movie and my chest started hurting badly, sweating", "my chest hurts badly and I am sweating",
])
def test_real_emergency_while_watching_is_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", [
    "ในซีรีส์พระเอกโดนยิงตาย เศร้ามาก", "ละครเรื่องนี้นางเอกหัวใจวาย", "ดูละครเรื่องนี้อยู่ นางเอกโดนตบ สะใจมาก",
    "watching a documentary about strokes, so interesting", "we were watching a movie where the character gets shot",
    "my chest hurts after coughing a lot, no other symptoms", "chest day at the gym, sweating a lot",
])
def test_stories_on_screen_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
