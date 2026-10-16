"""คำตอบภาษาอังกฤษเฉพาะเรื่อง — เดิมนิ้วขาด/น้ำร้อนลวก/สารเข้าตาได้ "Animal bites: wash…"
และเลือดไม่หยุด/แพ้รุนแรง/ไข้คอแข็งได้แค่ "Write down when it started" (หลายเรื่องเคยได้ Risk 0)"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text,needle", [
    ("my son won't stop bleeding", "Press a clean cloth"),
    ("my son was stabbed", "Don't pull out a knife"),
    ("my son cut off a finger", "put the bag on ice"),
    ("my dad got burned with boiling water", "20 minutes"),
    ("my mom got chemicals in the eye", "15–20 minutes"),
    ("my son got electrocuted", "Cut the power"),
    ("my son hit his head and is vomiting", "emergency room"),
    ("my son was stung by a bee and his face is swelling", "EpiPen"),
    ("my son has a high fever and a stiff neck", "meningitis"),
    ("my dad is very drunk and won't wake up", "onto their side"),
    ("my mom swallowed a coin", "X-ray"),
    ("my son fell in the pool", "Throw something that floats"),
    ("my son ate rat poison", "poison control"),
])
def test_english_first_step(text, needle):
    assert assess(text)["text_risk"] >= 60
    assert needle in compose(text)


@pytest.mark.parametrize("text", ["I burned my toast lol", "my son is drowning in homework", "my dad hit his head on the cabinet lol he's fine"])
def test_english_idioms_stay_calm(text):
    assert assess(text)["text_risk"] < 60


@pytest.mark.parametrize("text", ["I wrote my goodbye letters", "I'm going to jump off the bridge tonight", "I've been stockpiling my pills",
                                  "tonight is my last night", "I just want the pain to stop forever", "I wish I could sleep and never wake up"])
def test_english_warning_signs_are_a_crisis(text):
    a = assess(text)
    assert a["crisis"] and "988" in compose(text)


@pytest.mark.parametrize("text", ["end it all with a bang at the party", "I can't go on with this project", "tonight is my last night in Bangkok"])
def test_english_everyday_phrases_are_not(text):
    assert not assess(text)["crisis"] and assess(text)["text_risk"] < 60
