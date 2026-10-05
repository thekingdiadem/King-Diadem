"""รอบหาบั๊ก 2 (~100 ข้อความจริง): เรื่องที่เคยได้ Risk 0 คำตอบทั่วไป หรือเข้าหัวข้อผิด"""
import pytest

from core.kernel_voice import assess, compose
from core.llm_gemini import detect_crisis, scrub_internal
from ENGINE.risk_engine import evaluate_risk
from tests.conftest import FAKE_LLM


def _top(text):
    return (assess(text)["topics"] or [None])[0]


# ── ช่วยคนอื่นที่อยากตาย — ไม่ใช่วิกฤตของผู้ใช้เอง ───────────────────────────
@pytest.mark.parametrize("text", ["เพื่อนบอกว่าอยากตาย ทำยังไงดี", "แม่บอกว่าไม่อยากอยู่แล้ว",
                                  "เห็นคนจะกระโดดสะพาน", "my friend wants to die"])
def test_third_party_crisis_gets_helper_guidance(text):
    a = assess(text)
    assert not a["crisis"] and a["topics"][0] == "someone" and a["text_risk"] >= 90
    assert "grief" not in a["topics"]                   # "เพื่อน…อยากตาย" เคยตรง GRIEF
    assert not detect_crisis(text)                      # LLM ไม่ใช้ CRISIS_SYSTEM ที่คุยกับผู้ใช้เหมือนเขาอยากตาย
    r = compose(text)
    assert "1323" in r and "ฉันได้ยินสิ่งที่คุณพูด" not in r


def test_bridge_jumper_gets_emergency_numbers_first():
    r = compose("เห็นคนจะกระโดดสะพาน")
    assert "191" in r.split("\n1)")[1].split("\n")[0]


@pytest.mark.parametrize("text", ["เพื่อนบอกว่าอยากตาย แล้วฉันก็อยากตายเหมือนกัน",
                                  "พี่บอกว่าถ้าฉันอยากตายให้โทรหา"])
def test_users_own_crisis_still_caught_next_to_third_party(text):
    assert assess(text)["crisis"] and evaluate_risk(text)["self_harm"] and detect_crisis(text)


def test_hyperbole_is_not_third_party_crisis():
    assert not assess("เขาบอกว่าหิวจะตาย")["topics"]


# ── ล่วงละเมิด · ความรุนแรงที่ไม่มีคำว่าถูก/โดน · แบล็กเมล์ ───────────────────
def test_sexual_abuse_detected_with_child_hotline():
    a = assess("พ่อเลี้ยงจับตัวหนู")
    assert a["topics"][0] == "sexual_abuse" and a["text_risk"] >= 85
    r = compose("พ่อเลี้ยงจับตัวหนู")
    assert "1387" in r and "ไม่ใช่ความผิด" in r


@pytest.mark.parametrize("text", ["ผัวเมาแล้วอาละวาด", "ครูทำร้ายนักเรียน"])
def test_violence_without_passive_marker(text):
    assert _top(text) == "violence" and assess(text)["text_risk"] >= 85


@pytest.mark.parametrize("text", ["แฟนขู่จะปล่อยคลิป", "มีคนแบล็กเมล์ขอเงิน", "ถูกแอบถ่าย"])
def test_sextortion_says_dont_pay(text):
    assert _top(text) == "sextortion"
    r = compose(text)
    assert "ไม่จ่ายเงิน" in r and "หลักฐาน" in r


def test_verbal_abuse_by_parent_gets_kind_words_and_hotlines():
    r = compose("แม่ด่าทุกวันว่าเป็นตัวถ่วง")
    assert "ไม่ใช่ความจริงเกี่ยวกับตัวคุณ" in r and "1387" in r


# ── เจ็บป่วย/บาดเจ็บฉุกเฉิน ─────────────────────────────────────────────
@pytest.mark.parametrize("text,word", [("เวียนหัว พูดไม่ชัด แขนซ้ายชา", "สโตรก"),
                                       ("ตั้งครรภ์ 8 เดือน เลือดออก", "ฝากครรภ์"),
                                       ("ลูกไข้สูง 40 องศา", "เช็ดตัว"),
                                       ("ลูกกินเหรียญเข้าไป", "ห้ามล้วงคอ"),
                                       ("ปวดหัวรุนแรงที่สุดในชีวิต", "1669")])
def test_medical_emergencies(text, word):
    a = assess(text)
    assert a["topics"][0] == "health_emergency" and a["text_risk"] >= 85
    r = compose(text)
    assert "1669" in r and word in r


@pytest.mark.parametrize("text,word", [("โดนงูกัด", "ห้ามกรีด"), ("โดนหมากัด", "พิษสุนัขบ้า"),
                                       ("น้ำร้อนลวกมือ", "20 นาที"), ("ไฟช็อต", "ตัดไฟก่อน"),
                                       ("รถชน มีคนบาดเจ็บ", "อย่าขยับคนเจ็บ")])
def test_first_aid(text, word):
    assert _top(text) == "first_aid"
    assert word in compose(text)


def test_electric_shock_is_not_money():
    assert "money" not in assess("ไฟช็อต")["topics"]


def test_panic_checks_heart_first():
    assert _top("แพนิคบ่อย หายใจไม่ทัน") == "panic"
    assert "1669" in compose("แพนิคบ่อย หายใจไม่ทัน").split("\n1)")[1].split("\n")[0]


def test_stop_antidepressants_says_talk_to_doctor():
    a = assess("กินยาซึมเศร้าอยู่ อยากหยุดยา")
    assert a["topics"][0] == "stop_meds"
    assert "อย่าหยุดยาเองทันที" in compose("กินยาซึมเศร้าอยู่ อยากหยุดยา")


# ── ความปลอดภัยอื่น ──────────────────────────────────────────────────
def test_drunk_driving():
    assert _top("พ่อกินเหล้าแล้วขับรถ") == "drunk_drive" and "191" in compose("พ่อกินเหล้าแล้วขับรถ")


@pytest.mark.parametrize("text", ["ยายหลงลืมออกจากบ้านหายไป", "ลูกหายไปตั้งแต่เมื่อวาน"])
def test_missing_person_no_need_to_wait(text):
    assert _top(text) == "missing"
    r = compose(text)
    assert "ไม่ต้องรอครบ 24 ชั่วโมง" in r and "191" in r


# ── สิทธิแรงงาน · ที่อยู่ · หนี้ ─────────────────────────────────────────
@pytest.mark.parametrize("text", ["หัวหน้าให้ทำโอทีไม่จ่ายเงิน", "นายจ้างไม่จ่ายเงินเดือนสองเดือนแล้ว",
                                  "โดนเลิกจ้างไม่ได้ค่าชดเชย"])
def test_labor_rights_hotline(text):
    assert _top(text) == "labor" and "1546" in compose(text)


def test_eviction_tonight_is_shelter_not_job():
    a = assess("โดนไล่ออกจากห้องเช่าคืนนี้")
    assert a["topics"][0] == "basic" and "job" not in a["topics"]
    assert "1300" in compose("โดนไล่ออกจากห้องเช่าคืนนี้")


def test_rent_arrears_is_housing():
    assert _top("ค่าเช่าค้างสามเดือน จะโดนไล่ออกจากห้อง") == "housing"


def test_fired_from_job_still_job():
    assert "job" in assess("โดนไล่ออกจากงาน")["topics"]


def test_loan_app_harassment_is_illegal():
    a = assess("แอปเงินกู้โทรประจาน")
    assert a["topics"][0] == "debt" and a["text_risk"] >= 55
    assert "พ.ร.บ.การทวงถามหนี้" in compose("แอปเงินกู้โทรประจาน")


# ── งานหลอก · แชร์ลูกโซ่ · การติด ─────────────────────────────────────
@pytest.mark.parametrize("text", ["ถูกชวนไปทำงานต่างประเทศ เงินดี ไม่ต้องมีประสบการณ์",
                                  "มีคนเสนองานพิมพ์ข้อความที่บ้าน รายได้วันละ 1500 ต้องจ่ายค่าสมัครก่อน"])
def test_job_scams(text):
    a = assess(text)
    assert "job" in a["scam"] and a["text_risk"] >= 75
    r = compose(text)
    assert "งานหลอก" in r and "วางสาย" not in r


def test_trafficking_offer_points_to_department_of_employment():
    assert "1694" in compose("ถูกชวนไปทำงานต่างประเทศ เงินดี ไม่ต้องมีประสบการณ์")


def test_ponzi_without_percent_sign():
    assert assess("แชร์ลูกโซ่ ได้ดอก 20 ต่อเดือน")["offer_flags"] == ["guarantee"]
    assert not assess("กู้นอกระบบ ดอก 20 ต่อเดือน")["offer_flags"]


@pytest.mark.parametrize("text", ["ซื้อหวยทุกงวดหมดเดือนละ 3000", "อยากเลิกบุหรี่", "เพื่อนชวนเสพยา",
                                  "คนในบ้านติดยา"])
def test_addiction_gaps(text):
    assert _top(text) == "addiction"


# ── คุยเล่น ───────────────────────────────────────────────────────────
@pytest.mark.parametrize("text,word", [("ขอบใจนะ", "ยินดี"), ("ฝันดี", "ฝันดี"), ("555", "หัวเราะ"),
                                       ("เบื่อ", "ช่วงว่าง"), ("ว่าง", "ช่วงว่าง")])
def test_small_talk_is_warm_not_a_plan(text, word):
    r = compose(text)
    assert word in r and "ขอเรียงเรื่องนี้" not in r and "1)" not in r


# ── อังกฤษ ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("text,topic,word", [("I took too many pills", "overdose", "poison"),
                                             ("I'm being bullied at school", "bullying", "evidence"),
                                             ("someone is threatening me online", "sextortion", "evidence"),
                                             ("I can't pay my rent", "housing", "landlord")])
def test_english_urgent_topics(text, topic, word):
    assert _top(text) == topic
    r = compose(text)
    assert word in r and "Let's lay this out" not in r


# ── ไม่จับผิด ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("text", ["หนูกัดเล็บบ่อย", "ดื่มกาแฟแล้วขับรถไปทำงาน", "หน้าชาไปเลยตอนโดนแซว",
                                  "นั่งนานจนขาชา", "พี่หายไปไหนมา", "จะลงรูปในไอจี", "จะส่งรูปให้เพื่อนดู",
                                  "ตำรวจจับตัวคนร้ายได้แล้ว", "พี่เตะฟุตบอลทุกเย็น", "พ่อต่อยมวยเก่ง", "แม่ตบยุง",
                                  "พ่อชอบดูฟุตบอล", "แม่ให้ซ้อมเปียโน", "ดูข่าวรถชนบนทางด่วน", "ช็อตนี้สวยมาก",
                                  "พ่อไม่กลับบ้านเพราะไปต่างจังหวัด"])
def test_everyday_phrases_no_alarm(text):
    a = assess(text)
    assert a["text_risk"] == 0 and not a["crisis"] and not a["relationship"]
    assert not set(a["topics"]) & {"violence", "sexual_abuse", "sextortion", "first_aid", "missing",
                                   "drunk_drive", "panic", "someone", "money", "health"}


@pytest.mark.parametrize("text", ["พ่อตีหัวผม", "แฟนตบหน้า", "ผัวซ้อมจนเลือดออก"])
def test_real_violence_still_flagged(text):
    assert assess(text)["relationship"] == "collapse_risk"


# ── /run: บริบทถึง LLM และไม่หลุดถึงผู้ใช้ ───────────────────────────────
@pytest.mark.parametrize("text,tag", [("เพื่อนบอกว่าอยากตาย ทำยังไงดี", "ผู้ใช้กำลังช่วยคนอื่น"),
                                      ("พ่อเลี้ยงจับตัวหนู", "ผู้ใช้อาจถูกล่วงละเมิด"),
                                      ("แฟนขู่จะปล่อยคลิป", "ผู้ใช้ถูกขู่ปล่อยคลิป"),
                                      ("โดนงูกัด", "เรื่องเร่งด่วนต่อชีวิต"),
                                      ("กินยาซึมเศร้าอยู่ อยากหยุดยา", "ผู้ใช้อยากหยุดยาที่แพทย์สั่ง"),
                                      ("หัวหน้าให้ทำโอทีไม่จ่ายเงิน", "1546")])
def test_run_passes_context_to_llm(client, text, tag):
    d = client.post("/run", json={"input": text}).json()
    assert tag in FAKE_LLM["prompts"][-1]
    assert d["route"] in ("general", "risk", "survival", "collapse")


@pytest.mark.parametrize("tag", ["[ผู้ใช้กำลังช่วยคนอื่นที่อาจอยากทำร้ายตัวเอง: …]", "[ผู้ใช้อาจถูกล่วงละเมิดทางเพศ: …]",
                                 "[ผู้ใช้ถูกขู่ปล่อยคลิป/รูป: …]", "[เรื่องเร่งด่วนต่อชีวิต/ร่างกาย: …]",
                                 "[ผู้ใช้อยากหยุดยาที่แพทย์สั่ง: …]"])
def test_new_context_tags_are_scrubbed(tag):
    assert "ผู้ใช้" not in scrub_internal(f"ฟังอยู่นะคะ\n{tag}\nค่อยๆ ไปด้วยกันค่ะ").replace("ฟังอยู่", "")
