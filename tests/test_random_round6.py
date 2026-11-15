"""เทสต์สุ่มรอบ 6 (ไทย): ฝากฝังแบบไม่มีกำหนดกลับ · ขู่ฆ่า — เดิมได้ Risk 0"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["ฝากดูแลแมวด้วยนะ ถ้าเราไม่อยู่", "ฝากดูแลลูกด้วยนะ ถ้าฉันไม่อยู่แล้ว",
                               "แฟนขู่ว่าถ้าเลิกจะฆ่า", "สามีขู่ว่าจะเอาให้ตาย"])
def test_now_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ["ฝากดูแลแมวด้วยนะ ไปเที่ยวเชียงใหม่สามวัน", "ฝากเลี้ยงหมาตอนเราไม่อยู่ ไปทำงานต่างจังหวัด",
                               "แฟนขู่ว่าจะเลิก", "ซื้อเชือกกระโดดมาออกกำลังกาย", "เขียนจดหมายลาออกยังไงดี",
                               "อยากหลับยาวๆ วันเสาร์ ทำงานเหนื่อยทั้งอาทิตย์"])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["เกมนี้บอสขู่จะฆ่าเราหมด", "หนังเรื่องนี้พระเอกขู่จะฆ่าเรา", "หนังเรื่องนี้มีฉากลักพาตัว"])
def test_violence_inside_games_and_movies_is_not_an_emergency(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["ดูหนังเรื่องนี้อยู่ แฟนขู่จะฆ่าฉัน", "ดูหนังกับแฟน แล้วแฟนขู่จะฆ่าฉันจริงๆ", "โดนลักพาตัว"])
def test_real_threats_next_to_a_movie_are_still_heard(q):
    assert assess(q)["risk_shown"] >= 65
