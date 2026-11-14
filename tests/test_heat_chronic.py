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


@pytest.mark.parametrize("q,must", [
    ("เป็นไขมันพอกตับ ต้องทำไง", "ย้อนกลับได้"),
    ("เป็นโรคหัวใจ ออกกำลังกายได้ไหม", "ไม่ใช่ควรหยุด"),
    ("เป็นหอบหืด พ่นยาไม่ค่อยดีขึ้น", "ยาควบคุม"),
    ("เป็นไทรอยด์เป็นพิษ", "TSH"),
    ("เป็นโรคลมชัก ขับรถได้ไหม", "ไม่ควรขับ"),
    ("แม่อายุ 75 กินยาหลายตัวมาก กลัวยาตีกัน", "brown bag"),
    ("เป็นถุงลมโป่งพอง", "1600"),
    ("เป็นไมเกรนบ่อย", "ยาป้องกัน"),
    ("กินยาลดไขมันแล้วปวดกล้ามเนื้อ", "สแตติน"),
    ("เป็นภูมิแพ้ จามทุกเช้า", "น้ำเกลือ"),
    ("เป็นไซนัสอักเสบ ปวดหน้าผาก น้ำมูกเขียว", "ไม่ต้องใช้ยาปฏิชีวนะ"),
    ("I have diabetes, how do I manage it", "HbA1c"),
    ("I have high blood pressure and keep forgetting my pills", "don't double up"),
    ("my sinus infection won't go away", "10 days"),
])
def test_chronic_batch2(q, must):
    assert must in compose(q, footer=False)


def test_sinus_spreading_to_eye_is_urgent():
    o = compose("เป็นไซนัส ตาบวมแดง มองเห็นภาพซ้อน", footer=False)
    assert "ไปโรงพยาบาลวันนี้" in o and "(70/100)" in o


def test_ya_tee_kan_is_drug_interaction_not_violence():
    assert "violence" not in assess("แม่อายุ 75 กินยาหลายตัวมาก กลัวยาตีกัน")["topics"]
    assert "ทำร้าย" in compose("พ่อตีแม่", footer=False)


@pytest.mark.parametrize("q", ["เป็นโรคหัวใจ แน่นหน้าอก เหงื่อแตก", "ลูกเป็นลมชัก กำลังชักอยู่"])
def test_chronic_batch2_emergencies(q):
    assert assess(q)["risk_shown"] >= 75 or "1669" in compose(q, footer=False)
