"""สภา 6 เสียงและ VEGA ต้องตอบจากเรื่องจริงของผู้ใช้ — เจ้าของโปรเจกต์: "สภาคำตอบผิวเผินมากๆ เวก้าด้วย"
เดิม: "เงินเดือน 35,000 เก็บ 300,000 อยากลาออกไปเปิดร้านกาแฟ" ได้ LYLA "เงินน้อยไม่ได้แปลว่าไม่มีทาง"
TITAN "แยกรายจ่ายเป็น 3 กอง" และ VEGA พูดเรื่องหางานใหม่ — ไม่มีเสียงไหนใช้ตัวเลขของผู้ใช้"""
import pytest

from core import decision_brief as db
from core.kernel_voice import compose

CAFE = "เป็นพนักงานบริษัทเงินเดือน 35,000 มีเงินเก็บ 300,000 อยากลาออกไปเปิดร้านกาแฟ ควรทำไหม"


def test_extracts_the_real_numbers_and_kind():
    f = db.extract(CAFE)
    assert f["nums"] == {"income": 35000, "savings": 300000} and set(f["kinds"]) == {"quit_job", "start_business"}
    assert db.extract("มีเงินเก็บ 5 แสน ลงทุนเปิดร้าน 2 แสน")["nums"] == {"savings": 500000, "invest": 200000}


def test_runway_and_floor_are_computed_not_guessed():
    a = db.analyze(CAFE)
    assert round(a["runway"], 1) == 8.6 and a["floor"] == 210000 and a["max_invest"] == 90000 and a["monthly_assumed"]
    b = db.analyze("เงินเดือน 40,000 ใช้จ่ายเดือนละ 20,000 เงินเก็บ 600,000 ลงทุนเปิดร้าน 300,000 ดีไหม")
    assert b["runway"] == 30 and b["runway_after"] == 15 and not b["monthly_assumed"]


def test_council_uses_the_users_numbers_and_gives_go_and_stop_conditions():
    out = compose(CAFE, voice_mode="council")
    for must in ("300,000", "8.6 เดือน", "90,000", "210,000", "เดินหน้าเมื่อ", "หยุดเมื่อ", "ลูกค้าต่อวัน", "ไม่ได้ใช้ AI"):
        assert must in out, must
    assert "เงินน้อย" not in out and "แยกรายจ่าย 30 วัน" not in out      # ประโยคกลางที่ผิดบริบทเดิม
    assert out.count("◈") == 1 and all(v in out for v in ("VEGA ◆", "PATICCA ☸", "TITAN ▲", "COSMOS ✦", "CIVIL ⬡"))


def test_vega_is_about_this_decision_not_job_hunting():
    out = compose(CAFE, voice_mode="vega")
    assert "8.6 เดือน" in out and "หยุดทันทีเมื่อ" in out and "สมัครวันละ" not in out and out.rstrip().endswith("ไม่ได้ใช้ AI")


def test_missing_numbers_are_named_not_invented():
    out = db.council("อยากลาออกไปเปิดร้านกาแฟ ควรทำไหม")
    assert "ยังขาดตัวเลขสำคัญ" in out and "เดือนถ้ารายได้หยุด" not in out


def test_dependents_and_irreversible_parts_change_the_advice():
    out = db.council("มีลูกสองคน เงินเก็บ 400,000 เงินเดือน 30,000 จะกู้เพิ่มแล้วทำสัญญาเช่าตึก 3 ปีเปิดร้านอาหาร ดีไหม")
    assert "สัญญาเช่า" in out and "กู้" in out and "คนในบ้าน" in out


@pytest.mark.parametrize("text", ["วันนี้กินอะไรดี", "เหนื่อยงานมากเลย"])
def test_ordinary_messages_keep_the_normal_council(text):
    assert not db.applies(text) and "เดินหน้าเมื่อ:\n" not in compose(text, voice_mode="council")


def test_a_crisis_is_never_turned_into_a_spreadsheet():
    out = compose("อยากตาย ลาออกดีไหม", voice_mode="council")
    assert "1323" in out and "เดินหน้าเมื่อ:\n" not in out


def test_ai_gets_the_computed_numbers_as_context():
    line = db.facts_line(db.analyze(CAFE))
    assert line.startswith("[DECISION BRIEF:") and "runway≈8.6" in line and "90,000" in line
    from core.llm_gemini import COUNCIL_SYSTEM, VEGA_SYSTEM
    assert "DECISION BRIEF" in COUNCIL_SYSTEM and "ห้ามตอบผิวเผิน" in COUNCIL_SYSTEM and "หยุดเมื่อ" in VEGA_SYSTEM
