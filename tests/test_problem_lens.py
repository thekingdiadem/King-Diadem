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
