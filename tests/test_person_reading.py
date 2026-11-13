"""อ่านคน (core/person_reading.py) — ตำรามนุษย์เล่มแรก: MBTI
เจ้าของโปรเจกต์: "สอนให้รู้จักมนุษย์ ตำรามนุษย์เล่มแรกก็ MBTI" — ไม่เดาไทป์ แต่ตอบในแบบที่คนนั้นรับได้ดีที่สุด"""
import pytest

from core.person_reading import adapt_main, llm_hint, read


@pytest.mark.parametrize("text,want", [
    ("ผ่อนรถค้างสองงวด ต้องทำอะไรบ้าง กี่วันจะโดนยึด", {"info": "S"}),
    ("ทำไมคนเราถึงชอบเอาตัวเองไปวัดกับคนอื่น", {"info": "N"}),
    ("อยากเรียนโท ขอข้อดีข้อเสียตรงๆ", {"decide": "T"}),
    ("แฟนขอเลิก รู้สึกเจ็บมาก ร้องไห้ทั้งคืน", {"decide": "F"}),
    ("I feel so lonely and heartbroken", {"decide": "F"}),
    ("ต้องตัดสินใจภายในสัปดาห์นี้ ควรเลือกอะไร", {"life": "J"}),
    ("ยังไม่แน่ใจ อยากรู้ว่ามีทางไหนบ้าง", {"life": "P"}),
])
def test_reads_what_the_message_asks_for(text, want):
    r = read(text)
    for k, v in want.items():
        assert r[k] == v, (text, r)


@pytest.mark.parametrize("text", [
    "อยากเรียนต่อปริญญาโทแต่กลัวเสียเวลาสองปี",      # "กลัว" แบบลังเล ไม่ใช่คนที่อยากให้ฟังก่อน
    "ปวดหลังเรื้อรังมาหลายเดือน เจ็บหลังทุกวัน",       # "เจ็บ" ทางกาย
    "สวัสดี",
])
def test_weak_signals_change_nothing(text):
    assert read(text) == {"info": None, "decide": None, "life": None}


def test_crisis_is_never_adapted():
    assert read("แฟนขอเลิก ไม่อยากอยู่แล้ว") == {"info": None, "decide": None, "life": None}
    assert llm_hint(read("I want to kill myself, which one should I pick")) == ""


def test_adapting_keeps_the_facts_and_steps():
    main = {"open": ["แก่นของเรื่อง"], "paths": ["ก", "ข", "ค"], "ask": "คำถาม?", "vega": "ตัวแปรที่ตัดสิน"}
    f = adapt_main(main, {"decide": "F"})
    t = adapt_main(main, {"decide": "T"})
    j = adapt_main(main, {"life": "J"})
    assert f["paths"] == t["paths"] == j["paths"] == main["paths"]
    assert f["open"][0].endswith("แก่นของเรื่อง") and f["open"][0] != "แก่นของเรื่อง"
    assert "ตัวแปรที่ตัดสิน" in t["open"][0]
    assert j["ask"] != main["ask"]
    assert main["open"] == ["แก่นของเรื่อง"]                         # ไม่แก้ dict ต้นฉบับ


def test_hint_never_names_a_type():
    h = llm_hint({"info": "N", "decide": "T", "life": "J"})
    assert h and "ห้ามพูดถึงบุคลิกหรือไทป์" in h
    for typ in ("MBTI", "INTJ", "ENFP", "ไทป์ของผู้ใช้คือ"):
        assert typ not in h


def test_same_problem_reads_differently_by_how_it_is_asked():
    from core.kernel_voice import compose
    base = "อยากเรียนต่อปริญญาโทแต่กลัวเสียเวลาสองปี"
    plain, logic, feel = compose(base), compose(base + " ขอข้อดีข้อเสียตรงๆ"), compose("แฟนขอเลิก รู้สึกเจ็บมาก ร้องไห้ทั้งคืน")
    assert "สรุปเชิงเหตุผล" in logic and "สรุปเชิงเหตุผล" not in plain
    assert feel.startswith("ฟังแล้วรู้สึกได้ว่าเรื่องนี้หนักกับใจคุณจริงๆ")
    assert not plain.startswith("ฟังแล้วรู้สึกได้")
