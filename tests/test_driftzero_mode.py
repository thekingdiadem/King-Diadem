"""โหมด DriftZero — ตรวจการตัดสินใจขององค์กร/โครงการตามเฟรมเวิร์คใน repo KING-DIADEM-DriftZero
เจ้าของโปรเจกต์อยากให้เป็นโหมดแยก (เหมือนโหมดสร้างภาพ) ไม่รวมกับการปรึกษา"""
import pytest

from ENGINE.driftzero import audit


def _stops(t):
    return [g["id"] for g in audit(t)["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("text,gate", [
    ("บริษัทจะย้ายโรงงานไปริมแม่น้ำเพื่อลดต้นทุน", "E2"),
    ("จ้างบริษัทของภรรยาผมทำระบบบำบัด", "K13"),
    ("ลงทุนไปเยอะแล้ว ถอยไม่ได้แล้ว ต้องทำต่อ", "K7"),
    ("ต้องได้กำไรสูงสุดในไตรมาสนี้", "K4"),
    ("โครงการนี้ไม่มีความเสี่ยงเลย มั่นใจ 100%", "K11"),
    ("พบสารเคมีรั่วในไลน์ผลิต แต่ยังอยากเดินเครื่องต่อ", "K12"),
    ("ทำ PR ให้ดูเหมือนรักษ์โลก แต่ไม่ต้องบอกใครเรื่องน้ำเสีย", "K8"),
    ("We will maximize profit and ignore the team", "K4"),
    ("The supplier is an unknown source with no certificates", "K14"),
])
def test_each_gate_catches_its_pattern(text, gate):
    assert gate in _stops(text)
    assert audit(text)["verdict"] == "stop"


def test_complete_plan_passes_but_still_needs_a_human():
    t = ("ร้านกาแฟจะเปิดสาขาที่ 2 งบ 300,000 บาท ความเสี่ยงคือยอดขายไม่ถึง 500 แก้ว/วัน "
         "ต้นทุนเพิ่มวันละ 2,000 บาท ผู้รับผิดชอบคือผู้จัดการร้าน แผนสำรองคือปิดภายใน 6 เดือน")
    a = audit(t)
    assert a["verdict"] == "pass" and not _stops(t)
    assert "เซ็นรับผิดชอบ" in a["summary"]["th"]
    assert not a["sop"][6]["done"]                       # SOP 7 ตรวจหลังทำ — ระบบทำแทนคนไม่ได้


def test_missing_information_is_asked_not_guessed():
    a = audit("บริษัทจะขยายสาขา")
    assert a["verdict"] == "ask"
    sops = {q["sop"] for q in a["asks"]}
    assert {1, 2, 3, 6} <= sops                          # รายละเอียด · ผลเสีย · DHD · คนรับผิดชอบ
    assert any("DHD" in q["th"] for q in a["asks"])


def test_same_text_same_result():
    t = "โรงงานจะปล่อยน้ำเสียลงคลองเพื่อประหยัด"
    assert audit(t) == audit(t)


def test_life_in_danger_goes_to_help_not_gates():
    a = audit("อยากตาย ไม่ไหวแล้ว")
    assert a["verdict"] == "urgent" and not a["gates"]
    assert "1323" in a["summary"]["th"]


def test_personal_story_is_pointed_to_talk_mode():
    assert audit("แมวหายไปสองวันแล้ว")["note"]


def test_every_gate_explains_itself_in_two_languages():
    a = audit("ฮั้วประมูล ล็อกสเปก ปล่อยน้ำเสียลงแม่น้ำ ขยายทั่วประเทศทันที")
    for g in a["gates"]:
        assert g["name"]["th"] and g["name"]["en"]
        if g["status"] == "stop":
            assert g["why"]["th"] and g["why"]["en"]


def test_endpoint_is_free_and_needs_no_ai(client):
    r = client.post("/api/driftzero", json={"input": "จ้างบริษัทของภรรยาผมทำระบบบำบัดน้ำเสียลงแม่น้ำ"})
    assert r.status_code == 200
    a = r.json()["audit"]
    assert a["verdict"] == "stop" and "K13" in [g["id"] for g in a["gates"] if g["status"] == "stop"]
    assert client.post("/api/driftzero", json={"input": ""}).status_code == 400


def test_mode_switch_is_on_the_front_page():
    from tests._front import front_page
    page = front_page()
    assert 'id="mode-seg"' in page and 'data-m="dz"' in page and 'data-m="img"' in page
    assert "'/api/driftzero'" in page and "'/api/image/generate'" in page
