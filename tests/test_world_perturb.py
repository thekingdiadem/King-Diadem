"""เรื่องด่วนภาษาอื่น — บิดข้อความแบบที่คนตกใจพิมพ์จริง แล้วต้องยังจับได้ และคำตอบต้องพาไปโทรถูกที่

ทำไมต้องบิด: ข้อความในเทสต์เดิมเป็นประโยคตรงตำรา ส่วนคนจริงพิมพ์ "me toi khong tho duoc" (ไม่มีวรรณยุกต์
เพราะมือถือไม่มีคีย์บอร์ดเวียดนาม) — เคยได้ Risk 0 · ประโยคเดียวกลายเป็นหลายเคสโดยโค้ดไม่ยาวขึ้น
"""
import re
import unicodedata

import pytest

from core.kernel_voice import assess, compose
from tests.test_world_languages import CALM, CRISIS, URGENT


def _no_marks_latin(t):
    """ตัดเครื่องหมายเฉพาะอักษรละติน (แบบพิมพ์บนคีย์บอร์ดอังกฤษ) — อักษรพม่า เขมร ฮินดี ไม่มีใครพิมพ์ตัดสระทิ้ง"""
    t = t.replace("đ", "d").replace("ı", "i")
    out, latin = [], False
    for ch in unicodedata.normalize("NFD", t):
        if unicodedata.category(ch) == "Mn" and latin:
            continue
        if unicodedata.category(ch) != "Mn":
            latin = ch < "ɐ"
        out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


TWISTS = {
    "ตะโกน!!!": lambda t: t + "!!!",
    "ตัวใหญ่": str.upper,
    "เว้นวรรคเกิน": lambda t: "  " + re.sub(" ", "   ", t) + "  ",
    "อีโมจิ": lambda t: t + " 😭😭",
    "จุดๆ": lambda t: t + "...",
    "ขึ้นบรรทัดใหม่": lambda t: "\n" + t + "\n",
    "ไม่มีวรรณยุกต์": _no_marks_latin,
}


@pytest.mark.parametrize("twist", TWISTS)
@pytest.mark.parametrize("t", URGENT)
def test_urgent_survives_how_people_actually_type(t, twist):
    u = TWISTS[twist](t)
    assert assess(u)["text_risk"] >= 85, (twist, u)


@pytest.mark.parametrize("twist", TWISTS)
@pytest.mark.parametrize("t", CRISIS)
def test_crisis_survives_how_people_actually_type(t, twist):
    u = TWISTS[twist](t)
    assert assess(u)["crisis"], (twist, u)


@pytest.mark.parametrize("twist", ["ตะโกน!!!", "ตัวใหญ่", "ไม่มีวรรณยุกต์"])
@pytest.mark.parametrize("t", CALM)
def test_calm_stays_calm_when_twisted(t, twist):
    assert assess(TWISTS[twist](t))["text_risk"] < 50, t


# ── เนื้อหาคำตอบ: ไม่ใช่แค่มี "1)" แต่ต้องพาไปโทร และมีเบอร์ของประเทศผู้พิมพ์ด้วย ──────────────

# เบอร์ที่ต้องเห็นในคำตอบ (นอกจากเบอร์ไทย) — คนพม่า/ลาว/กัมพูชาในไทยใช้เบอร์ไทยได้ แต่คนที่อยู่บ้านเกิดต้องได้เบอร์ประเทศตัวเอง
HOME_NUMBER = {
    "mẹ tôi không thở được": "115", "အမေ အသက်မရှူနိုင်ဘူး": "192", "ប្តីវាយខ្ញុំ": "117", "ແມ່ຫາຍໃຈບໍ່ໄດ້": "1195",
    "زوجي يضربني": "112", "माँ साँस नहीं ले रही": "112", "мама не дышит": "112", "hindi makahinga ang nanay ko": "911",
    "kocam beni dövüyor": "112", "mia madre non respira": "112",
}


@pytest.mark.parametrize("t", URGENT)
def test_reply_tells_you_to_call_first_with_a_real_number(t):
    out = compose(t, footer=False)
    first = "\n".join(out.split("\n")[:5])
    assert re.search(r"(?<!\d)(?:1669|191|199|1300)(?!\d)", first), out[:300]   # ทางไทยอยู่ในบรรทัดต้นๆ
    assert re.search(rf"(?<!\d){HOME_NUMBER[t]}(?!\d)", out), (t, HOME_NUMBER[t])


def test_every_urgent_sample_has_a_home_number():
    assert set(HOME_NUMBER) == set(URGENT)
