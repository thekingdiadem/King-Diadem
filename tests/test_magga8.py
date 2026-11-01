"""มรรคมีองค์ 8 ต้องตรวจได้จริงครบ 8 องค์

เดิมชั้นมรรคมีแค่ 3 ข้อ (ศีล/สมาธิ/ปัญญา) — "จะโกหกลูกค้า" ได้ PEACE ทุกข้อผ่าน,
"โกรธมาก จะลาออกเดี๋ยวนี้" สมาธิผ่าน, โดนหลอกโอนเงินก็มรรคผ่านหมด
ตอนนี้แยก 8 องค์ อ่านจากข้อความจริง และมรรคข้อใดไม่ผ่าน = ไม่ให้ PEACE (Final Governance Lock)
"""
import pytest

from ENGINE.bodhipakkhiya_engine import guardian_check

HS = {"entropy": 40, "resource": 50, "stability": 60}
EIGHT = ["สัมมาทิฏฐิ", "สัมมาสังกัปปะ", "สัมมาวาจา", "สัมมากัมมันตะ",
         "สัมมาอาชีวะ", "สัมมาวายามะ", "สัมมาสติ", "สัมมาสมาธิ"]


def test_layer_has_all_eight_factors_in_order():
    g = guardian_check("วันนี้อากาศดี", HS)
    assert [x["name"] for x in g["layers"][-1]["items"]] == EIGHT
    assert list(g["magga"]) == EIGHT and all(g["magga"].values()) and g["peace"]


@pytest.mark.parametrize("text,factor", [
    ("จะโกหกลูกค้าเรื่องคุณภาพสินค้าเพื่อปิดการขาย", "สัมมาวาจา"),
    ("อยากจ้างคนเขียนรีวิวปลอมให้ร้าน", "สัมมาวาจา"),
    ("อยากแก้แค้นเพื่อนร่วมงานให้มันโดนไล่ออก", "สัมมาสังกัปปะ"),
    ("จะจ่ายเงินใต้โต๊ะให้ได้งานประมูล", "สัมมาอาชีวะ"),
    ("มีคนจ้างให้เปิดบัญชีม้า ได้ครั้งละ 3000", "สัมมาอาชีวะ"),
    ("โกรธมาก จะลาออกเดี๋ยวนี้เลยไม่สนอะไรแล้ว", "สัมมาสมาธิ"),
    ("ตำรวจโทรมาบอกให้โอนเงินไปบัญชีปลอดภัย", "สัมมาสติ"),
    ("มั่นใจ 100% ว่าหุ้นตัวนี้ขึ้นแน่ จะเอาเงินเก็บทั้งหมดไปลง", "สัมมาทิฏฐิ"),
])
def test_each_missed_case_now_fails_the_right_factor_and_is_not_peace(text, factor):
    g = guardian_check(text, HS)
    assert g["magga"][factor] is False, g["failed"]
    assert not g["peace"]


@pytest.mark.parametrize("text", [
    "วันนี้อากาศดี", "ขอสูตรแกงเขียวหวาน", "อยากรู้ว่าควรเรียนต่อโทดีไหม",
    "อยากเปิดร้านกาแฟเล็กๆ ควรเริ่มยังไง", "เพื่อนโกหกเรา ควรคุยกับเขายังไงดี",
])
def test_ordinary_questions_pass_all_eight(text):
    g = guardian_check(text, HS)
    assert all(g["magga"].values()), g["failed"]


# ── ให้ผู้ใช้เห็นได้จริง: เดิมคิดแล้วไม่เคยแสดง (app.js ไม่มีคำว่ามรรคเลย) ─────────────────
def test_run_returns_the_eight_factors(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": "จะโกหกลูกค้าเรื่องคุณภาพสินค้าเพื่อปิดการขาย"}).json()
    m = {x["name"]: x for x in d["magga"]}
    assert list(m) == EIGHT and m["สัมมาวาจา"]["ok"] is False and m["สัมมาวาจา"]["note"]


def test_crisis_answers_skip_the_panel(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    assert "magga" not in client.post("/run", json={"input": "อยากตาย"}).json()


def test_trace_panel_shows_magga_and_every_text_translates():
    import pathlib
    import re
    from tests._front import front_page
    page = front_page()
    assert "row('มรรค 8'" in page and "d.magga" in page
    root = pathlib.Path(__file__).resolve().parent.parent
    i18n = (root / "static" / "i18n.js").read_text(encoding="utf-8")
    g = guardian_check("วันนี้อากาศดี", HS)
    texts = {"มรรค 8", "ผ่านครบ 8 องค์"}
    src = (root / "ENGINE" / "bodhipakkhiya_engine.py").read_text(encoding="utf-8")
    block = src[src.index("# 6 มรรค 8"):src.index("    ]\n    out = []")]
    texts |= set(re.findall(r'"([^"\n]*[ก-๙][^"\n]*)"', block)) - {"มรรคมีองค์ 8"}
    texts |= {x["name"] for x in g["layers"][-1]["items"]}
    missing = [t for t in texts if f"'{t}':" not in i18n]
    assert not missing, missing
