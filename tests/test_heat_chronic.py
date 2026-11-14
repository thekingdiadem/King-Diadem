"""เพลียแดด/ฮีทสโตรก และโรคประจำตัว (ไต เบาหวาน ความดัน เกาต์)"""
import pytest
from core.kernel_voice import assess, compose


def test_heat_exhaustion_is_caution_not_zero():
    o = compose("ร้อนมาก เวียนหัว คลื่นไส้ ทำงานอยู่หน้างาน", footer=False)
    assert "ควรระวัง (65/100)" in o and "ฮีทสโตรก" in o
    assert "(65/100)" in compose("felt dizzy working in the heat", footer=False)


def test_heatstroke_still_urgent_and_plain_heat_calm():
    assert assess("ทำงานกลางแดด 38 องศา เพื่อนหน้ามืด ตัวร้อนจัด พูดไม่รู้เรื่อง")["risk_shown"] >= 85
    assert assess("วันนี้ร้อนมาก อยากกินไอติม")["risk_shown"] < 60


@pytest.mark.parametrize("q,must", [
    ("หมอบอกว่าไตเสื่อมระยะเริ่มต้น ต้องทำยังไง", "ชะลอได้จริง"),
    ("เป็นโรคไตระยะ 3 กินอะไรได้บ้าง", "ระยะ 3 ขึ้นไปมักต้องคุมโปรตีน"),
    ("เป็นโรคไต ทำงานกลางแดดได้ไหม", "NSAIDs"),
    ("ไตวาย ต้องฟอกไตไหม", "ไม่ใช่จุดจบ"),
    ("เป็นเบาหวาน ต้องดูแลตัวเองยังไง", "HbA1c"),
    ("เป็นความดันสูง ลืมกินยาบ่อย", "ไม่ต้องกินเบิ้ล"),
    ("เป็นเกาต์ ปวดนิ้วโป้งเท้า", "กรดยูริก"),
    ("I have early kidney disease, what should I do", "slowed"),
])
def test_chronic_lenses(q, must):
    assert must in compose(q, footer=False)


@pytest.mark.parametrize("q", ["เป็นความดันสูง ปวดหัวรุนแรงมาก ตามัว", "เป็นเบาหวาน ใจสั่นเหงื่อแตก น้ำตาลต่ำมาก",
                               "เป็นโรคไต เจ็บหน้าอก หายใจไม่ออก"])
def test_chronic_emergencies_stay_urgent(q):
    assert assess(q)["risk_shown"] >= 75
