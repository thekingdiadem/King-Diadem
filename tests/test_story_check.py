"""ตรวจความสมเหตุสมผลของเรื่องที่เล่า (core/story_check) — ชี้จุดที่ไม่ตรงกัน + สิ่งที่เช็กได้ · ไม่ตัดสินว่าใครโกหก

เจ้าของโปรเจกต์อยากให้ AI "จับคนโกหกได้" — ไม่มีระบบไหนรู้ว่าใครโกหกจากข้อความ ระบบที่ฟันผิดทำลายความสัมพันธ์จริง
สิ่งที่ทำได้และคมกว่า: บอกว่าตรงไหนไม่ตรงกัน และควรขอดูหลักฐานอะไร
"""
import pytest

from core.story_check import check, llm_hint, reply_block

CASES = [
    ("แฟนบอกว่าเงินเดือน 50,000 แต่สลิปที่เห็นแค่ 30,000", "number", "แฟน"),
    ("สามีบอกว่าไปประชุมที่เชียงใหม่ทั้งอาทิตย์ แต่เพื่อนเห็นเขาที่สยาม", "place_time", "สามี"),
    ("นายหน้าการันตีกำไร 10% ต่อเดือน ไม่มีความเสี่ยง", "too_good", "นายหน้า"),
    ("เขาบอกว่าต้องโอนวันนี้ ห้ามบอกใคร", "pressure", ""),
    ("ผู้รับเหมาไม่ยอมให้ดูสัญญา ให้โอนเข้าบัญชีส่วนตัว", "no_proof", "ผู้รับเหมา"),
    ("ตอนแรกเขาบอกว่าเป็นหมอ ตอนนี้บอกว่าเป็นวิศวกร", "shifting", ""),
    ("แฟนหาว่าฉันคิดไปเอง ทั้งที่เห็นแชทกับตา", "gaslight", "แฟน"),
    ("My boss said my salary is 40000 but the contract says only 32000", "number", "boss"),
    ("The recruiter promised guaranteed income and said don't tell your family", "too_good", "recruiter"),
]


@pytest.mark.parametrize("text,kind,who", CASES)
def test_finds_what_does_not_line_up_and_who(text, kind, who):
    found = check(text)
    hit = next((f for f in found if f["kind"] == kind), None)
    assert hit, (text, found)
    assert hit["who"].lower() == who.lower()


@pytest.mark.parametrize("text", [
    "วันนี้ไปตลาดซื้อผักมา",
    "ลงทุนกองทุนรวม มีความเสี่ยงตามตลาด",
    "เพื่อนบอกว่าเงินเดือน 30,000 แต่สลิป 30,000",            # ตัวเลขตรงกัน
    "ในละครพระเอกการันตีกำไร ห้ามบอกใคร",                     # เรื่องในละคร
    "แม่บอกว่าจะไปตลาด แต่ไปเจอเพื่อนที่ตลาดเดียวกัน",
])
def test_normal_stories_are_left_alone(text):
    assert check(text) == []


def test_reply_never_says_someone_is_lying():
    block = reply_block(check("นายหน้าการันตีกำไร 10% ต่อเดือน ต้องโอนวันนี้"))
    assert "ไม่ได้แปลว่าใครโกหก" in block and "1207" in block
    assert "โกหกแน่" not in block and "เป็นคนโกหก" not in block
    assert "ห้ามสรุปว่าใครโกหก" in llm_hint(check("แฟนหาว่าฉันคิดไปเอง"))


def test_shows_up_in_chat_but_not_in_emergencies():
    from core.kernel_voice import compose
    out = compose("สามีบอกว่าไปประชุมที่เชียงใหม่ทั้งอาทิตย์ แต่เพื่อนเห็นเขาที่สยาม ควรทำยังไง", footer=False)
    assert "ยังไม่ตรงกัน" in out and out.rstrip().endswith("LYLA ◈")
    urgent = compose("แฟนหาว่าฉันคิดไปเอง แล้วตบหน้าจนเลือดออก", footer=False)
    assert "ยังไม่ตรงกัน" not in urgent                           # เรื่องด่วน: ขั้นตอนความปลอดภัยต้องเด่น


def test_driftzero_points_out_a_partner_whose_numbers_do_not_match():
    from ENGINE.driftzero import audit, lyla_voice
    r = lyla_voice(audit("หุ้นส่วนบอกว่ายอดขายเดือนละ 500,000 แต่บัญชีจริงแค่ 200,000 และไม่ยอมให้ดูบัญชี จะลงเงินเพิ่ม 1 ล้าน"))
    assert {f["kind"] for f in r["story"]} >= {"number", "no_proof"}
    assert "หุ้นส่วน" in r["lyla"]["th"] and "ไม่ได้แปลว่าใครโกหก" in r["lyla"]["th"]
