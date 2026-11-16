"""รอบสุ่ม 101: เห็ดป่า · ผู้สูงอายุหลงหาย · เด็กนัดเจอคนจากเกม"""
import pytest
from core.kernel_voice import assess

REAL = [("เพื่อนกินเห็ดป่าแล้วอ้วกไม่หยุด", "health_emergency"), ("we ate wild mushrooms and can't stop vomiting", "health_emergency"),
        ("ยายหลงออกจากบ้านตั้งแต่เช้า ยังไม่กลับ", "missing"), ("ลูกสาว 14 นัดเจอผู้ชายในเกมคืนนี้", "online_grooming"),
        ("น้องอายุ 12 แอบไปเจอผู้ใหญ่ในเน็ต", "online_grooming")]
CALM = ["เก็บเห็ดป่ามาทำแกง อร่อยมาก", "กินเห็ดหอมแล้วอร่อย", "ยายออกไปตลาดตั้งแต่เช้า", "แม่ออกจากบ้านตั้งแต่เช้า ยังไม่กลับเพราะไปงานบวช",
        "ลูกนัดเจอเพื่อนในเกมที่โรงเรียน", "ลูกสาวนัดเจอเพื่อนร่วมห้อง"]


@pytest.mark.parametrize("q,topic", REAL)
def test_missed_before_now_caught(q, topic):
    # ทุกข้อเคยได้ 0
    a = assess(q)
    assert a["risk_shown"] >= 80 and topic in a["topics"]


@pytest.mark.parametrize("q", CALM)
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
