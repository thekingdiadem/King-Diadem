"""จุดอ่อนที่ชุดปิดตา (tests/blind) ชี้ให้เห็น — แก้เป็นกลุ่มรูปประโยค และเทสต์ด้วยประโยคใหม่ที่ไม่อยู่ในข้อสอบ
(ชุดปิดตาห้ามจูน: ถ้าแก้ให้ตรงข้อสอบทีละข้อ คะแนนจะดูดีแต่ระบบไม่ได้เก่งขึ้นจริง)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    # อยากตายแบบอ้อม "ชีวิตไม่มีความหมาย / เหนื่อยกับการมีชีวิต / เขียนจดหมายลาตาย" — es vi ko ja
    "La verdad ya no le encuentro sentido a vivir", "Estoy cansada de vivir así", "ya no tiene sentido seguir",
    "Anh ấy viết thư tuyệt mệnh rồi", "cuộc sống không còn ý nghĩa gì, mệt quá",
    "살아갈 이유가 없어요", "요즘 사는 게 아무 의미가 없어", "生きる意味が分からない、疲れた",
])
def test_indirect_suicidal_thoughts_are_crisis(q):
    assert assess(q)["crisis"]


@pytest.mark.parametrize("q", ["Con ăn kẹo bị mắc họng, khó thở", "Bé nuốt đồng xu bị mắc, không ho ra được",
                               "奶奶差点晕倒，现在说话不清楚", "妈妈晕倒了", "แม่ปากเบี้ยว พูดไม่ชัด แขนอ่อนแรง",
                               "พ่อพูดไม่ชัดเพราะเพิ่งทำฟัน แต่แขนขวาอ่อนแรง", "我把药全吃了", "Mi mamá no responde y no respira"])
def test_real_emergencies_stay_urgent(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "no le veo sentido a seguir con este proyecto", "estoy cansado de vivir en esta ciudad", "이 옷은 살 이유가 없어",
    "この映画は意味がない", "Xe bị mắc kẹt trong bùn", "Con bị mắc mưa về nhà",
    "ยิ้มทีไรปากเบี้ยวข้างนึงตั้งแต่เกิด", "พูดไม่ชัดเพราะเพิ่งถอนฟัน ยาชายังไม่หมด", "ล้มเบาๆ ไม่เจ็บ",
    "I burned my tongue a little on the soup", "我的药吃完了，明天去医院再拿", "Mi computadora se congeló y no responde",
    "my phone froze and is not responding", "看综艺笑到差点晕倒",
])
def test_everyday_stays_calm(q):
    r = assess(q)
    assert r["risk_shown"] < 60 and not r["crisis"]
