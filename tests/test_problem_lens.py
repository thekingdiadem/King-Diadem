"""เลนส์ปัญหา (core/problem_lens.py) — มองให้ทะลุก่อนตอบ

เจ้าของโปรเจกต์: "ทำให้ระบบเรามองทะลุทุกปัญหา ตอบอย่างมีเหตุผล ส่วนโทนแต่ละตัวไม่เหมือนกัน"
ไล่อ่าน 20 เรื่องชีวิตจริงตอนไม่มี AI: 6 เรื่องอ่านผิดคนหรือผิดเรื่อง 7 เรื่องได้แม่แบบกลางที่ใช้ได้กับทุกเรื่อง
และ VEGA ตอบเหมือน LYLA ทุกตัวอักษร ต่างแค่ลายเซ็น
"""
import re

import pytest

from core import problem_lens as L

# ประโยคที่ใช้ตอนเขียนเลนส์ + ประโยคชุดใหม่ที่เขียนต่างกัน (กันการท่องข้อสอบ)
POS = {
    "caregiver_load": ["แม่ป่วยติดเตียง ต้องลาออกมาดูแล แต่เงินเก็บใกล้หมด พี่น้องไม่ช่วยเลย",
                       "สามีป่วยเป็นมะเร็ง ต้องลาออกมาดูแลไหม เงินไม่พอ",
                       "My dad has dementia and I may have to quit my job to care for him, my siblings won't help"],
    "family_addiction": ["พ่อติดเหล้า เมาแล้วด่าแม่ทุกคืน", "แม่เล่นพนันจนเป็นหนี้ เอาเงินเก็บของหนูไปหมด",
                         "พี่ชายติดยา มาขอเงินแม่ทุกวัน", "My husband drinks every night and yells at the kids"],
    "breakup_received": ["แฟนขอเลิกเพราะบอกว่าเบื่อ ทั้งที่คบกันมา 7 ปี", "เมียขอหย่า บอกว่าหมดรักแล้ว",
                         "My boyfriend broke up with me out of nowhere"],
    "inlaw_spouse": ["ทะเลาะกับแม่สามีเรื่องเลี้ยงลูก สามีไม่เข้าข้าง", "ครอบครัวสามีดูถูกฉัน แต่สามีไม่ปกป้องเลย",
                     "My mother-in-law criticizes everything and my husband never takes my side"],
    "comparison": ["อายุ 35 ยังไม่มีอะไรเป็นของตัวเอง รู้สึกตามคนอื่นไม่ทัน",
                   "อายุ 30 แล้วยังไม่มีบ้าน ไม่มีรถ เห็นเพื่อนแต่งงานกันหมด รู้สึกล้มเหลว",
                   "I keep comparing myself to friends on Instagram and feel worthless"],
    "credit_stolen": ["โดนเพื่อนร่วมงานเอาผลงานไปเสนอเป็นของตัวเอง", "หัวหน้าเอางานที่ฉันทำไปพรีเซนต์เป็นของตัวเอง",
                      "My manager took credit for my project in the meeting"],
    "late_sleep": ["นอนตีสามทุกคืน ตื่นมาไม่สดชื่น ทำงานพลาดบ่อย", "หลับตีสี่ทุกวัน ตื่นไปเรียนไม่ไหว",
                   "I go to bed at 3 am every night and feel tired all day at work"],
    "car_arrears": ["ผ่อนรถไม่ไหวแล้ว ค้างมาสองงวด", "ขาดส่งรถมาสามเดือนแล้ว กลัวโดนยึด",
                    "I'm behind on my car loan, missed two payments"],
    "study_decision": ["อยากเรียนต่อปริญญาโทแต่กลัวเสียเวลาสองปี", "อายุ 40 แล้วเรียน ป.โท คุ้มไหม",
                       "Is a master's degree worth it at 35?"],
    "go_independent": ["อยากออกจากงานประจำไปเป็นฟรีแลนซ์ รายได้ตอนนี้ 25000", "อยากลาออกไปทำธุรกิจของตัวเอง แต่กลัวไม่มีรายได้",
                       "I want to quit my job to go freelance as a designer"],
    "choose_two": ["มีคนมาจีบสองคน ไม่รู้จะเลือกใคร", "คุยอยู่สองคน ไม่รู้จะเลือกใครดี", "Torn between two guys, both are nice"],
    "runway": ["บริษัทเงินเหลืออีก 3 เดือน นักลงทุนเงียบ", "My startup has 4 months of runway and investors stopped replying"],
}

# ห้ามจับ: วิกฤต การทำร้ายร่างกาย การข่มขู่ และเรื่องที่ใช้คำคล้ายกันแต่เป็นเรื่องอื่น
NEG = ["อยากตาย ไม่อยากอยู่แล้ว", "พ่อเมาแล้วตีแม่ทุกคืน", "พ่อติดเหล้า เมาแล้วต่อยแม่", "แฟนเลิกแล้วขู่จะปล่อยคลิป",
       "แม่ป่วย หายใจไม่ออก ตัวเขียว", "ซื้อรถใหม่ดีไหม เงินเดือน 30000", "นอนไม่หลับมาหลายวัน", "สวัสดีค่ะ",
       "สามีดีมากเลย ขอบคุณที่ช่วยนะ", "I can't sleep at all", "my dad hit my mom again tonight",
       "How do I compare two phones?", "อายุ 35 ควรมีเงินเก็บเท่าไร", "ป่วยเป็นไข้ ไปหาหมอดีไหม",
       "พ่อป่วยติดเตียง ตีหัวตัวเองจนเลือดออก ดูแลไม่ไหว",
       # มีคำตอบที่ดีอยู่แล้ว ไม่ต้องให้เลนส์แย่ง: คนดูแลเหนื่อย (caregiver) · พ่อแก่ขับรถไม่ไหว · เรียนต่อต่างประเทศ
       "แม่เป็นอัลไซเมอร์ ดูแลไม่ไหว", "พ่อแก่แล้ว ขับรถไม่ไหว แต่ไม่ยอมเลิกขับ", "เรียนต่อที่ออสเตรเลียดีไหม"]


def _lang(x):
    return "en" if x.isascii() else "th"


@pytest.mark.parametrize("key,text", [(k, x) for k, xs in POS.items() for x in xs])
def test_lens_reads_the_real_problem(key, text):
    assert (L.find(text, _lang(text)) or {}).get("key") == key


@pytest.mark.parametrize("text", NEG)
def test_lens_leaves_crisis_and_other_topics_alone(text):
    assert L.find(text, _lang(text)) is None


def test_physical_harm_words_do_not_hide_inside_other_thai_words():
    """ภาษาไทยไม่เว้นวรรค — "ติดเ*ตี*ยง" และ "สา*มีด*ูถูก" เคยทำให้เลนส์คิดว่าเป็นการทำร้ายแล้วถอยไป"""
    P = re.compile(L._PHYSICAL)
    for w in ("ติดเตียง", "เตรียมตัว", "ตีสาม", "ตีนเปล่า", "สามีดูถูก", "มีดีอะไร", "ตบแต่งบ้าน", "ไม่มีดนตรี", "ตีความ"):
        assert not P.search(w), w
    for w in ("ตีแม่", "โดนตี", "ต่อยหน้า", "ตบหน้า", "เตะท้อง", "เอามีดจี้", "ทุบตี", "ฆ่าตัวตาย", "เลือดออก", "ตีกัน"):
        assert P.search(w), w


def test_every_lens_answers_who_why_and_three_steps():
    for lz in L.LENSES:
        for side in ("th_d", "en_d"):
            if side not in lz:
                continue
            d = lz[side]
            assert d["open"] and len(d["paths"]) == 3 and d["ask"].strip().endswith("?"), (lz["key"], side)
            assert d.get("vega") and d["vega"] != d["open"][0], (lz["key"], side)


def test_vega_opens_with_structure_lyla_with_the_person():
    t = "อยากออกจากงานประจำไปเป็นฟรีแลนซ์ รายได้ตอนนี้ 25000"
    lyla, vega = L.find(t, "th", "lyla"), L.find(t, "th", "vega")
    assert lyla["open"] != vega["open"] and "ตัวแปร" in vega["open"][0]
    assert lyla["paths"] == vega["paths"]          # ข้อเท็จจริงไม่เปลี่ยนตามคนพูด


def _run(client, text, who="lyla"):
    """ตอบจากสมการ (AI ปลอมทำเหมือนโควตาหมด) — เลนส์คือสิ่งที่ผู้ใช้ได้ตอนไม่มี AI"""
    from tests.conftest import FAKE_LLM
    FAKE_LLM["mode"] = "fail"
    try:
        return client.post("/run", json={"input": text, "persona_ui": who, "voice_mode": who}).json()
    finally:
        FAKE_LLM["mode"] = "ok"


def test_caregiver_is_not_treated_as_the_patient(client):
    """เดิมได้ "ร่างกายส่งสัญญาณมาแล้ว · ไข้สูงไม่ลด หายใจลำบาก" เหมือนผู้ใช้ป่วยเอง"""
    r = _run(client, "แม่ป่วยติดเตียง ต้องลาออกมาดูแล แต่เงินเก็บใกล้หมด พี่น้องไม่ช่วยเลย")["ai_response"]
    assert "แบกคนเดียว" in r and "หายใจลำบาก" not in r


def test_family_addiction_protects_the_parent_not_lectures_the_user(client):
    """เดิมได้วิธีเลิกเหล้า "ลบแอป/ไม่ซื้อติดบ้าน" เหมือนผู้ใช้ติดเอง"""
    r = _run(client, "พ่อติดเหล้า เมาแล้วด่าแม่ทุกคืน")["ai_response"]
    assert "คุณไม่ได้เป็นคนติด" in r and "1300" in r and "ลบแอป" not in r


def test_vega_voice_differs_from_lyla(client):
    t = "ผ่อนรถไม่ไหวแล้ว ค้างมาสองงวด"
    ly, ve = _run(client, t, "lyla"), _run(client, t, "vega")
    assert ve["persona"] == "VEGA" and ly["ai_response"].split("\n")[0] != ve["ai_response"].split("\n")[0]
    assert "เส้นตาย" in ve["ai_response"]


def test_council_reads_the_problem_and_gives_a_fitting_verdict(client):
    """เดิมสภาให้ TITAN แนะนำผู้ใช้สังเกตการดื่มของตัวเอง และมติ "เดินหน้าได้" กับเรื่องพ่อเมาด่าแม่"""
    r = _run(client, "พ่อติดเหล้า เมาแล้วด่าแม่ทุกคืน", "council")["ai_response"]
    assert "มติสภา: ความปลอดภัยของคนในบ้านมาก่อน" in r and "เดินหน้าได้" not in r


def test_english_lens(client):
    r = _run(client, "I keep comparing myself to friends on Instagram and feel worthless")["ai_response"]
    assert "highlight reel" in r and "Let's lay this out step by step" not in r


def test_crisis_still_wins_over_the_lens(client):
    r = _run(client, "แฟนขอเลิก ฉันไม่อยากอยู่แล้ว อยากตาย")
    assert "1323" in r["ai_response"] and "การตัดสินใจครั้งนี้ไม่ได้อยู่ในมือคุณ" not in r["ai_response"]


# ── คลังปัญหา 394 เรื่อง (core/problem_lens_more.py) ──────────────────────────
# ประโยคที่เขียนใหม่เหมือนคนพิมพ์จริง ไม่ได้มาจากแม่แบบที่ใช้ตอนเขียนเลนส์
HELD_OUT = {
    "heart_signs": ["ช่วงนี้ขึ้นบันไดนิดเดียวก็เหนื่อยง่ายมาก", "หัวใจเต้นเร็วบ่อยๆ ตอนนั่งเฉยๆ"],
    "lump_wait": ["คลำเจอก้อนที่คอ หมอนัดรอผลชิ้นเนื้อสองอาทิตย์ กลัวมาก"],
    "not_eating": ["เครียดจนกินข้าวไม่ลงมาเป็นอาทิตย์แล้ว"],
    "low_mood": ["เศร้ามาสามเดือนแล้ว ไม่รู้ว่าเป็นอะไร", "ช่วงนี้ไม่มีความสุขกับอะไรเลย"],
    "worry": ["คิดวนเรื่องเดิมทั้งคืน หยุดไม่ได้"],
    "anger": ["ช่วงนี้ขี้โมโหมาก หงุดหงิดใส่ลูกตลอด"],
    "burnout": ["ไม่มีไฟทำงานแล้ว ตื่นมาก็อยากลาออก"],
    "kin_refuse_doctor": ["แม่เจ็บเข่ามาเป็นปี แต่ไม่ยอมไปโรงพยาบาลเพราะกลัวเสียเงิน", "พ่อเป็นซึมเศร้า ไม่ยอมไปหาหมอ"],
    "find_carer": ["ยายเป็นอัลไซเมอร์ ไม่มีคนดูแลตอนกลางวัน", "พ่อป่วยติดเตียง ต้องหาคนดูแล"],
    "kin_jobless": ["น้องชายตกงาน ขอมาอยู่ด้วยที่ห้อง"],
    "kin_belittle": ["แม่ชอบพูดว่าหนูโง่ ไม่ได้เรื่องสักอย่าง"],
    "silent_treatment": ["สามีไม่พูดกับฉันมาสองสัปดาห์แล้ว"],
    "controlling_partner": ["แฟนห้ามไปเจอเพื่อน แล้วขอรหัสไลน์", "แฟนหึงหวงมาก ขอดูโทรศัพท์ทุกวัน"],
    "cheating": ["จับได้ว่าสามีมีกิ๊กที่ทำงาน"],
    "ghosted": ["คนที่คุยด้วยอ่านไม่ตอบมาสามวันแล้ว"],
    "no_raise": ["อยู่บริษัทนี้มาห้าปี เงินเดือนไม่เคยขึ้นเลย"],
    "guarantor": ["เป็นคนค้ำให้ญาติซื้อรถ ตอนนี้โดนไฟแนนซ์ทวง"],
    "tax": ["ยื่นภาษีไม่เป็นเลย ต้องทำยังไง"],
    "noisy_neighbor": ["ห้องข้างๆ เปิดเพลงดังถึงตีสอง"],
    "mule_police": ["ได้หมายเรียกจากตำรวจ บอกว่าบัญชีเราเป็นบัญชีม้า", "โดนตำรวจเรียกเพราะบัญชีถูกใช้รับเงินโกง"],
    "kys_deduct": ["ผ่อน กยศ ไม่ไหวแล้ว ค้างมานาน", "โดนหักเงินเดือนเพราะหนี้ กยศ."],
    "lease_cancel": ["อยากย้ายออกก่อนครบสัญญา เช่าคอนโดไว้หนึ่งปี"],
    "job_hunt": ["ยื่นใบสมัครไปห้าสิบที่ ไม่มีใครเรียกเลย"],
    "relocation_offer": ["ได้ข้อเสนองานใหม่เงินเดือนมากกว่า 30% แต่ต้องย้ายจังหวัด"],
}


@pytest.mark.parametrize("key,text", [(k, x) for k, xs in HELD_OUT.items() for x in xs])
def test_lens_generalises_to_new_wording(key, text):
    assert (L.find(text) or {}).get("key") == key


@pytest.mark.parametrize("text,must", [
    ("ไม่อยากอยู่แล้ว เศร้ามาสองเดือน", "1323"),                       # วิกฤตมาก่อนเลนส์ซึมเศร้า
    ("แฟนห้ามไปเจอเพื่อน แล้วตบหน้าฉัน", "ความปลอดภัยของคุณมาก่อน"),   # ลงมือแล้ว = ความปลอดภัย ไม่ใช่เลนส์การควบคุม
    ("เจ็บหน้าอกตอนนี้ หายใจไม่ออก ใจสั่น", "แพทย์"),                    # ฉุกเฉิน ไม่ใช่เลนส์ใจสั่นบ่อย
])
def test_urgent_cases_are_not_taken_by_a_lens(text, must):
    from core.kernel_voice import compose
    assert must in compose(text)


@pytest.mark.parametrize("text", ["ห้องข้างๆ มีเสียงผู้หญิงกรีดร้องให้ช่วยด้วย",
                                  "ได้ยินเสียงเด็กร้องไห้จ้าจากบ้านข้างๆ ทุกคืน มีเสียงตีด้วย"])
def test_hearing_someone_in_danger_next_door_gets_witness_steps(text):
    """เดิม "ห้องข้างๆ มีเสียงผู้หญิงกรีดร้องให้ช่วยด้วย" ได้แม่แบบกลาง "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน" """
    from core.kernel_voice import compose
    r = compose(text)
    assert "191" in r and "ขอเรียงเรื่องนี้" not in r


def test_trailing_stressed_does_not_replace_the_real_problem():
    """"ปวดหลังเรื้อรังมาหลายเดือน เครียดมาก" เคยได้ "ตอนนี้ไม่ต้องแก้ทุกอย่าง" แทนเรื่องปวดหลัง"""
    from core.kernel_voice import compose
    for q in ("ปวดหลังเรื้อรังมาหลายเดือน", "เพื่อนร่วมงานนินทาลับหลัง", "ค้ำประกันให้เพื่อน แล้วเพื่อนหนี"):
        assert compose(q).split("\n")[0] == compose(q + " เครียดมาก").split("\n")[0], q


def test_kys_deduction_is_not_called_illegal():
    """เดิมได้ "ค่าจ้างเป็นสิทธิ์ของคุณ ทวงได้" — การหักเงินเดือนใช้หนี้ กยศ. นายจ้างต้องทำตามกฎหมาย"""
    from core.kernel_voice import compose
    r = compose("โดนหักเงินเดือนเพราะหนี้ กยศ. ทำยังไงดี")
    assert "ตามกฎหมาย" in r and "ทวงได้โดยไม่ต้องจ้างทนาย" not in r


def test_agency_hotlines_are_the_right_ones():
    """เลนส์ชุดสองเคยเขียน "กรมการจัดหางาน 1506" — 1506 คือประกันสังคม กรมการจัดหางานคือ 1694"""
    import pathlib
    src = "".join(p.read_text(encoding="utf-8") for p in pathlib.Path("core").glob("problem_lens*.py"))
    assert "จัดหางาน 1506" not in src and "จัดหางาน (สายด่วน 1506" not in src
    assert "กรมการจัดหางาน 1694" in src and "ประกันสังคม 1506" in src


# ── ชุดที่ 3: คลังรอบสอง 225 เรื่อง (16 ด้านที่ยังไม่เคยลอง) ──────────────────────
BANK2 = {
    "passport_seized": "ทำงานที่ญี่ปุ่น นายจ้างยึดพาสปอร์ต",
    "overseas_job_scam": "นายหน้าเก็บเงินไปทำงานเกาหลี แล้วหายไป",
    "loan_shark": "มีหนี้นอกระบบ ดอกวันละพัน",
    "debt_harass": "โดนแอปเงินกู้ทวงหนี้ โทรหาเพื่อนทุกคน",
    "deceased_debt": "สามีเสีย มีหนี้ทิ้งไว้ ต้องจ่ายไหม",
    "inheritance_dispute": "พ่อเสียไม่ได้ทำพินัยกรรม พี่น้องแย่งมรดก",
    "funeral_cost": "ต้องจัดงานศพแต่ไม่มีเงิน",
    "car_claim": "รถชนกันเล็กน้อย คู่กรณีไม่ยอมจ่าย",
    "insurance_denied": "ประกันไม่ยอมจ่ายค่ารักษา",
    "eviction": "เจ้าของบ้านให้ย้ายออกภายในสัปดาห์",
    "home_arrears": "ผ่อนบ้านไม่ไหว กลัวโดนยึด",
    "miscarriage": "แท้งลูกเมื่อเดือนก่อน ยังทำใจไม่ได้",
    "lgbt_self": "เป็นเกย์ ไม่กล้าบอกที่บ้าน",
    "child_came_out": "ลูกสาวบอกว่าชอบผู้หญิง ไม่รู้จะทำตัวยังไง",
    "elder_wander": "ยายหลงลืมบ่อย ออกจากบ้านแล้วหลงทาง",
    "online_harass": "มีคนเอารูปไปทำแอคปลอม",
    "gig_income": "ขับไรเดอร์ รายได้ลดลงครึ่งหนึ่ง",
    "farm_loss": "น้ำท่วมนาเสียหายหมด",
    "karma_fortune": "หมอดูบอกว่าปีนี้ดวงตก ควรทำอะไร",
}


@pytest.mark.parametrize("key,text", list(BANK2.items()))
def test_bank2_problems_reach_their_lens(key, text):
    """ผ่านตัวประกอบคำตอบจริง ไม่ใช่แค่ตัวจับเลนส์ — เดิมหลายเรื่องถูกด่านอื่นแย่งไป"""
    from core.kernel_voice import compose
    lz = L.find(text)
    assert lz and lz["key"] == key
    assert compose(text).split("\n")[0] == lz["open"][0]


@pytest.mark.parametrize("text,must,mustnt", [
    ("รถชนกัน เลือดออกเยอะ คู่กรณีหนี", "แพทย์", "เรื่องหลักฐาน"),             # มีคนเจ็บ → การแพทย์ก่อน
    ("โดนรถชนท้าย คอเคล็ด คู่กรณีไม่ยอมเคลม", "", "ถ้าทุกคนปลอดภัยแล้ว"),
    ("โอนเงินให้คนขายของออนไลน์แล้วโดนบล็อก", "แจ้ง", "นายหน้า"),             # ถูกโกงจริง → ขั้นตอนตามเงินคืน
])
def test_declared_urgent_takeover_stays_narrow(text, must, mustnt):
    from core.kernel_voice import compose
    r = compose(text)
    assert must in r and mustnt not in r


def test_lost_pet_is_not_triggered_by_loan_words():
    """"เงิ*นก*ู้" + "ทวง*หนี*้" เคยถูกอ่านเป็น "นกหนี" → ได้คำตอบสัตว์เลี้ยงหาย"""
    from core.kernel_voice import compose
    assert "สัตว์เลี้ยง" not in compose("โดนแอปเงินกู้ทวงหนี้ โทรหาเพื่อนทุกคน")
    assert "สัตว์เลี้ยง" in compose("นกแก้วบินหนีไปจากบ้าน")


# ── ภาษาอังกฤษ (core/problem_lens_en.py) — คลัง 164 เรื่องเคยได้ "Let's lay this out step by step." 78% ──
EN_BANK = {
    "caregiver_load": "my mom is bedridden and I had to quit my job to care for her, savings almost gone",
    "loan_shark": "I borrowed from a loan shark and the interest is insane",
    "deceased_debt": "my husband died and left debts, do I have to pay",
    "kin_belittle": "my parents call me a failure all the time",
    "car_arrears": "I'm two payments behind on my car loan",
    "retire_savings": "I'm 60 and don't have enough saved to retire",
    "child_dream": "my kid wants to drop out to be a youtuber",
    "miscarriage": "I had a miscarriage last month and can't stop crying",
    "kys_deduct": "I'm drowning in student loan payments",
}


@pytest.mark.parametrize("key,text", list(EN_BANK.items()))
def test_english_problems_reach_their_lens(key, text):
    from core.kernel_voice import compose
    lz = L.find(text, "en")
    assert lz and lz["key"] == key
    assert lz["open"][0] in compose(text)      # อาจมีประโยครับความรู้สึกนำหน้า (core/person_reading.py)


@pytest.mark.parametrize("text,start", [
    ("I'm drowning in student loan payments", "Student loan payments"),       # สำนวน ไม่ใช่คนจมน้ำ
    ("my son is drowning in the pool", "Get help to them"),                     # จมน้ำจริง ยังต้องได้ขั้นตอนช่วยชีวิต
    ("my dad drinks every night and beat my mom tonight", "What's happening at home is violence"),
    ("I owe a loan shark and he said he'll break my legs", "Being threatened"),
    ("my husband hits me", "Your safety comes first."),
    ("my partner checks my phone and won't let me see friends", "A relationship shouldn't make you ask permission"),
])
def test_english_danger_never_goes_to_a_lens(text, start):
    """ด่านกลาง: ทำร้ายร่างกาย อาวุธ หรือขู่ทำร้าย → ทุกเลนส์ถอย (เดิมตัวกันมีแต่ภาษาไทย)"""
    from core.kernel_voice import compose
    assert compose(text).startswith(start)


def test_thai_danger_gate_covers_threats_too():
    assert L.find("เจ้าหนี้นอกระบบขู่จะทำร้ายถ้าไม่จ่าย") is None
    assert L.find("มีหนี้นอกระบบ ดอกวันละพัน")["key"] == "loan_shark"


def test_english_passport_seizure_is_named_as_trafficking():
    """มีคำตอบภาษาอังกฤษเดิมที่บอกตรงว่าอาจเป็นการค้ามนุษย์ — เลนส์ไม่ต้องแย่ง แต่ต้องไม่หลุดไปเรื่องอื่น"""
    from core.kernel_voice import compose
    assert "trafficking" in compose("my employer took my passport")
