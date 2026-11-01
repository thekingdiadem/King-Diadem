"""อริยสัจ 4 ต้องเห็นจากเรื่องจริงก่อนมรรค 8 — เจ้าของโปรเจกต์: "ต้องรู้เห็นความเป็นจริงอย่างอริยสัจสี่แจ่มแจ้งก่อน ไม่งั้นมรรค 8 ไม่ตรง"
เดิมขั้นอริยสัจ 4 เป็นแม่แบบเดียวกันทุกข้อความ ("ทุกข์ = ปัญหาจริงในประโยคเดียว · …") ระบบไม่ได้เห็นทุกข์ของเรื่องไหนเลย"""
import pytest

from core.kernel_voice import compose
from ENGINE.ariya_sacca import UNCLEAR, four_truths
from ENGINE.bodhipakkhiya_engine import guardian_check

HS = {"entropy": 40, "resource": 50, "stability": 60}


@pytest.mark.parametrize("text,dukkha", [
    ("นอนไม่หลับมาหลายวันแล้ว ทำยังไงดี", "นอนไม่หลับ"),
    ("หนี้บัตรเครดิต 50000 ผ่อนไม่ไหว", "หนี้"),
    ("จะโกหกลูกค้าเพื่อปิดการขาย", "พูดไม่จริง"),
    ("ตำรวจโทรมาบอกให้โอนเงินไปบัญชีปลอดภัย", "มิจฉาชีพ"),
    ("แมวหายไป 2 วันแล้ว", "สัตว์เลี้ยงหาย"),
])
def test_each_story_gets_its_own_suffering(text, dukkha):
    assert dukkha in four_truths(text)["dukkha"]


def test_not_one_template_for_everything():
    seen = {four_truths(t)["dukkha"] for t in ("นอนไม่หลับมาหลายวันแล้ว", "หนี้บัตรเครดิต 50000 ผ่อนไม่ไหว",
                                               "จะโกหกลูกค้าเพื่อปิดการขาย", "แมวหายไป 2 วันแล้ว")}
    assert len(seen) == 4


def test_users_own_because_is_the_cause_first():
    t = four_truths("อยากลาออกเพราะหัวหน้าด่าทุกวัน")
    assert t["samudaya"] == "ตามที่เล่า: หัวหน้าด่าทุกวัน" and t["clear"]


def test_unknown_is_said_not_guessed():
    t = four_truths("วันนี้อากาศดี")
    assert t["dukkha"] == UNCLEAR and not t["clear"]


def test_path_is_the_first_step_of_the_real_answer():
    text = "หนี้บัตรเครดิต 50000 ผ่อนไม่ไหว"
    assert "1) " + four_truths(text)["magga"] in compose(text)


def test_right_view_stands_on_the_truths():
    note = lambda t: {x["name"]: x["note"] for x in guardian_check(t, HS)["layers"][-1]["items"]}["สัมมาทิฏฐิ"]
    assert note("อยากลาออกเพราะหัวหน้าด่าทุกวัน") == "เห็นทุกข์และเหตุชัด"
    assert "เหตุยังไม่ชัด" in note("แมวหายไป 2 วันแล้ว")


def test_truths_reach_the_ai_and_the_panel(client, monkeypatch):
    from core.king_diadem_core import quick_assess
    assert "ทุกข์=หนี้มากกว่ากำลังผ่อน" in quick_assess("หนี้บัตรเครดิต 50000 ผ่อนไม่ไหว", HS)["wise_ctx"]
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": "หนี้บัตรเครดิต 50000 ผ่อนไม่ไหว"}).json()
    assert d["ariya"]["dukkha"] == "หนี้มากกว่ากำลังผ่อน"
    from tests._front import front_page
    assert "h + ariyaHTML(t) + maggaHTML(t)" in front_page()          # เห็นทุกข์ก่อน แล้วค่อยมรรค


@pytest.mark.parametrize("q,want", [
    ("สัมมาสมาธิคืออะไรนะ", "ตั้งใจมั่น"), ("อริยสัจ 4 คืออะไร", "สมุทัย"), ("อธิบายมรรค 8 หน่อย", "ศีล"),
    ("ไตรลักษณ์หมายถึงอะไร", "อนิจจัง"), ("ทางสายกลางคืออะไร", "สุดโต่ง"),
])
def test_dharma_questions_answered_without_ai(q, want):
    assert want in compose(q).split("\n")[0]


def test_sleepless_many_days_gets_the_sleep_answer():
    assert compose("นอนไม่หลับมาหลายวันแล้ว ทำยังไงดี").startswith("ไม่ได้นอนหลายวัน")


# ── ปรัชญาปารมิตาหฤทัยสูตร (เจ้าของโปรเจกต์มอบฉบับที่ตรวจกับต้นฉบับสันสกฤตแล้ว) ──
@pytest.mark.parametrize("q,want", [
    ("คะเต คะเต แปลว่าอะไร", "ไปถึงฝั่งแล้ว"), ("ความว่างคืออะไร", "ไม่ได้แปลว่าไม่มีอะไรเลย"),
    ("ขันธ์ 5 คืออะไร", "เวทนา"), ("หฤทัยสูตรคืออะไร", "ไม่หวาดกลัว"),
])
def test_heart_sutra_terms(q, want):
    assert want in compose(q).split("\n")[0]


def test_mantra_uses_the_corrected_reading():
    """ใช้ "โพธิ สวาหา" ตามสันสกฤต (bodhi svāhā) ไม่ใช่ "โบดิซัวฮา" ของบทที่ถอดผ่านสำเนียงจีน"""
    out = compose("คะเต คะเต แปลว่าอะไร")
    assert "ปาระสังคะเต โพธิ สวาหา" in out and "โบดิซัวฮา" not in out


def test_truths_are_a_guide_not_a_verdict():
    """หฤทัยสูตร: "ไม่มีทุกข์ สมุทัย นิโรธ มรรค" — อริยสัจ 4 ก็ว่าง ใช้ข้ามฟาก ไม่ใช่สิ่งที่ยึด"""
    from ENGINE.ariya_sacca import llm_hint
    assert "ห้ามตีตราผู้ใช้" in llm_hint(four_truths("หนี้บัตรเครดิต 50000 ผ่อนไม่ไหว"))
    from tests._front import front_page
    assert "ไม่ใช่คำตัดสิน" in front_page()
