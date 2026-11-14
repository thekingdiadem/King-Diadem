"""ความต้องการใต้คำพูด · โทนผู้ใช้ · ค่าเลือด · ผล DNA"""
import pytest
from core import human_needs as hn, lab_values as lab
from core.kernel_voice import compose


@pytest.mark.parametrize("q,need", [
    ("ทำงานหนักทุกวันแต่ไม่มีใครเห็นเลย", "seen"),
    ("พ่อแม่บังคับให้เรียนหมอ ไม่เคยได้เลือกเองเลย", "autonomy"),
    ("ทำอะไรก็ไม่ดีสักอย่าง รู้สึกล้มเหลว", "competence"),
    ("ตื่นมาก็เหมือนเดิมทุกวัน ทำไปเพื่ออะไร", "meaning"),
    ("ย้ายมาใหม่ ไม่มีเพื่อนเลย", "belonging"),
    ("กลัวว่าจะตกงาน ไม่มีเงินสำรองเลย", "safety"),
    ("nobody notices how hard I work", "seen"),
])
def test_needs(q, need):
    assert need in hn.needs(q)


def test_needs_silent_on_crisis_and_plain():
    assert hn.needs("อยากตาย ไม่มีใครเห็น") == []
    assert hn.needs("พรุ่งนี้ฝนตกไหม") == []


def test_register():
    assert hn.register("ทำไงดีอะ 555")["style"] == "casual"
    assert hn.register("รบกวนสอบถามค่ะ")["style"] == "polite"
    assert hn.register("ช่วยด้วย")["length"] == "short"
    assert hn.register("ทำไมเป็นแบบนี้วะ!!!")["heated"]
    h = hn.llm_hint("ทำไมเป็นแบบนี้วะ!!!")
    assert "นิ่งกว่า" in h and "ไทป์" not in h


def test_need_ack_in_kernel_reply_not_doubled():
    a = compose("พ่อแม่บังคับให้เรียนหมอ ไม่เคยได้เลือกเองเลย", footer=False)
    assert "มีสิทธิ์ได้เลือกเอง" in a
    b = compose("ทำงานหนักทุกวันแต่ไม่มีใครเห็นเลย หัวหน้าก็ไม่เคยชม", footer=False)
    assert "ความพยายามที่ไม่มีใครเห็น" in b and "ทำเต็มที่แล้วไม่มีใครเห็น" not in b
    assert "ความเหงาบอกว่า" not in b


def test_lab_reading_and_tiers():
    v = {k: g for k, _, g, *_ in lab.read("ผลตรวจสุขภาพ LDL 190 HDL 38 TG 220 น้ำตาล 108 HbA1c 6.1")}
    assert v == {"ldl": "high", "hdl": "watch", "tg": "high", "glucose": "watch", "hba1c": "watch"}
    r = compose("ผลเลือด เกล็ดเลือด 18,000 มีไข้สูงมา 3 วัน", footer=False)
    assert "ควรพบแพทย์วันนี้" in r and "แอสไพริน" in r and "อดอาหาร" not in r
    assert "go to hospital today" in compose("My blood test: potassium 6.4, creatinine 2.1, eGFR 35", footer=False)
    assert "ก้ำกึ่ง" in compose("ค่าตับ ALT 85 AST 60 ปกติไหม", footer=False)


@pytest.mark.parametrize("q", ["ใส่น้ำตาล 2 ช้อนในกาแฟ", "สูตรขนม น้ำตาล 100 กรัม", "Hb ทีมเราได้ 3 คะแนน", "na 5 คน"])
def test_lab_not_triggered_by_everyday_numbers(q):
    assert lab.read(q) == []


def test_hba1c_not_read_as_hb():
    ks = [k for k, *_ in lab.read("ผลตรวจ HbA1c 6.8")]
    assert ks == ["hba1c"]


def test_dna_risk_not_destiny():
    assert "ไม่ได้บอก \"โชคชะตา\"" in compose("ตรวจยีน BRCA1 แล้วเป็นบวก", footer=False)
    assert "risk, not destiny" in compose("My 23andMe says I carry BRCA2", footer=False)
