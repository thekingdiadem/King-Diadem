"""โหมด DriftZero — ตรวจการตัดสินใจขององค์กร/โครงการตามเฟรมเวิร์คใน repo KING-DIADEM-DriftZero
เจ้าของโปรเจกต์อยากให้เป็นโหมดแยก (เหมือนโหมดสร้างภาพ) ไม่รวมกับการปรึกษา"""
import pytest

from ENGINE.driftzero import audit


def _stops(t):
    return [g["id"] for g in audit(t)["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("text,gate", [
    ("โรงงานจะปล่อยน้ำเสียลงคลองเพื่อลดต้นทุน", "E2"),
    ("บริษัทจะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้", "E2"),
    ("We will bet the company and max out the credit line", "E2"),
    ("ขายสินทรัพย์หลักเพื่อจ่ายปันผล", "E2"),
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
         "ต้นทุนเพิ่มวันละ 2,000 บาท ผู้รับผิดชอบคือผู้จัดการร้าน แผนสำรองคือปิดภายใน 6 เดือน "
         "ตอนนี้มีเงินสด 800,000 บาท เงินสดสำรองไม่ต่ำกว่า 200,000 บาท")
    a = audit(t)
    assert a["verdict"] == "pass" and not _stops(t)
    assert a["waterline"]["level"] == "above" and a["waterline"]["after"] == 500_000
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


def test_waterline_means_the_floor_not_just_water():
    """เจ้าของโปรเจกต์: Waterline ระดับองค์กร = เส้นขั้นต่ำที่ห้ามต่ำกว่า ไม่งั้นความเสียหายย้อนกลับไม่ได้
    คนถือเงินหลักล้าน/พันล้านอ่าน "เส้นน้ำ" แล้วจะงงว่าน้ำเกี่ยวอะไรกับองค์กร"""
    g = {x["id"]: x for x in audit("บริษัทจะใช้เงินสำรองทั้งหมดขยายสาขา")["gates"]}["E2"]
    assert g["status"] == "stop" and "น้ำ" not in g["name"]["th"] and "ย้อนกลับไม่ได้" in g["why"]["th"]
    asks = audit("บริษัทจะขยายสาขา")["asks"]
    assert any(q["th"].startswith("Waterline") and "ห้ามต่ำกว่า" in q["th"] for q in asks)
    assert [q["sop"] for q in asks] == sorted(q["sop"] for q in asks)


# ── Waterline gauge: เส้นวัดจม/รอด · Drift Zero reference · L0 ───────────────────
from ENGINE.waterline_gauge import gauge  # noqa: E402


@pytest.mark.parametrize("text,level", [
    ("บริษัทมีเงินสด 30 ล้าน จะใช้ 25 ล้านขยาย 10 สาขา เงินสดสำรองขั้นต่ำ 10 ล้าน", "below"),
    ("มีเงิน 1.2 พันล้าน ทุ่ม 800 ล้าน ห้ามต่ำกว่า 500 ล้าน", "below"),
    ("เงินสดคงเหลือ 5 ล้าน ลงทุน 1 ล้าน ไม่ต่ำกว่า 3.5 ล้าน", "near"),
    ("We have $2M cash, will invest 500k, floor 1M", "above"),
])
def test_gauge_says_above_near_or_below_water(text, level):
    assert gauge(text)["level"] == level


def test_below_water_is_stop_the_line_even_without_keywords():
    a = audit("บริษัทมีเงินสด 30 ล้าน จะใช้ 25 ล้านเปิดโรงงานใหม่ เงินสดสำรองขั้นต่ำ 10 ล้าน ผู้อนุมัติคือบอร์ด")
    e2 = {g["id"]: g for g in a["gates"]}["E2"]
    assert a["verdict"] == "stop" and e2["status"] == "stop"
    assert "ใต้ระดับน้ำ" in e2["why"]["th"] and "5 ล้าน" in e2["why"]["th"] and "10 ล้าน" in e2["why"]["th"]


def test_drift_rate_tells_days_until_the_floor():
    g = gauge("เงินสดคงเหลือ 5 ล้าน ไม่ต่ำกว่า 3.5 ล้าน ขาดทุนเดือนละ 300,000 บาท")
    assert g["burn_per_day"] == 10_000 and g["days_to_floor"] == 150
    a = audit("เงินสดคงเหลือ 5 ล้าน ลงทุน 1 ล้าน ไม่ต่ำกว่า 3.5 ล้าน ขาดทุนวันละ 100,000 บาท")
    assert {g["id"]: g for g in a["gates"]}["E2"]["status"] == "stop"      # อีก 5 วันจะแตะเส้น


def test_no_rate_unit_no_guess():
    assert gauge("เงินสด 5 ล้าน ขั้นต่ำ 2 ล้าน ขาดทุน 100,000")["burn_per_day"] is None


def test_floor_without_current_asks_how_much_now():
    asks = audit("บริษัทจะขยายสาขา ขั้นต่ำ 2 ล้าน")["asks"]
    assert any("ตอนนี้มีเท่าไหร่" in q["th"] for q in asks)


def test_gauge_is_drawn_in_the_check_sheet():
    from tests._front import front_page
    page = front_page()
    assert "function wlGauge(w)" in page and "h += wlGauge(a.waterline)" in page
