"""รอบหาบั๊ก 3: เรื่องที่ยังได้ "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน" หรือคำตอบภาษาอังกฤษทั่วไป"""
import pytest

from core.kernel_voice import assess, compose
from tests.conftest import FAKE_LLM


def _top(text):
    return (assess(text)["topics"] or [None])[0]


@pytest.mark.parametrize("text", ["กรีดแขนตัวเองบ่อย", "เอามีดกรีดขาตัวเอง", "I keep cutting myself"])
def test_self_injury_gets_hotline(text):
    assert assess(text)["crisis"]
    r = compose(text)
    assert "1323" in r or "findahelpline" in r


@pytest.mark.parametrize("text,topic,word", [
    ("ล้วงคอหลังกินทุกมื้อ", "eating", "เกลือแร่"),
    ("ไม่กินข้าวเพราะกลัวอ้วน", "eating", "1323"),
    ("ได้ยินเสียงคนพูดในหัว", "psychosis", "จิตแพทย์"),
    ("แม่เป็นอัลไซเมอร์ ดูแลไม่ไหว", "caregiver", "ภาวะพึ่งพิง"),
    ("เหนื่อยกับการดูแลพ่อที่ป่วยติดเตียง", "caregiver", "1300"),
    ("ไม่มีสิทธิ์รักษา", "health_rights", "1330"),
    ("ค่ารักษาแพงมาก", "health_rights", "สังคมสงเคราะห์"),
    ("ไม่มีบัตรประชาชน", "health_rights", "สำนักงานเขต"),
    ("ป่วยเป็นมะเร็ง ไม่รู้จะเริ่มยังไง", "diagnosis", "จดคำถาม"),
    ("ติดเชื้อ HIV", "diagnosis", "ยาต้านไวรัส"),
    ("ผลตรวจเลือดผิดปกติ กลัวมาก", "diagnosis", "พบบ่อย"),
    ("ถูกตำรวจจับ", "legal", "พบและปรึกษาทนาย"),
    ("ได้หมายศาล", "legal", "อย่าเพิกเฉยหมายศาล"),
    ("โดนฟ้อง", "legal", "กองทุนยุติธรรม"),
    ("พ่อแก่แล้วล้มในห้องน้ำ", "first_aid", "อย่ารีบดึงให้ลุก"),
    ("เล่นเว็บพนันออนไลน์หมดตัว", "addiction", "1323"),
    ("ยืมเงินแม่ไปเล่นบาคาร่า", "addiction", "1323"),
    ("ลูกติดมือถือ", "addiction", "สังเกต"),
    ("นายจ้างยึดพาสปอร์ต", "labor", "บังคับใช้แรงงาน"),
    ("ทำงานบ้านเขาไม่ได้หยุดเลย", "labor", "สัปดาห์ละ 1 วัน"),
    ("โดนเลิกจ้างเพราะท้อง", "labor", "ลาคลอด"),
])
def test_round3_topics(text, topic, word):
    assert _top(text) == topic
    r = compose(text)
    assert word in r and "ขอเรียงเรื่องนี้" not in r


def test_fall_reply_has_no_burn_advice():
    assert "ไฟลวก" not in compose("พ่อแก่แล้วล้มในห้องน้ำ")


@pytest.mark.parametrize("text", ["ซื้อของออนไลน์ไม่ได้ของ", "โอนเงินซื้อของแล้วร้านปิดเพจ"])
def test_online_shopping_fraud_is_scam_lost(text):
    a = assess(text)
    assert a["scam"] == ["lost"] and "1441" in compose(text)


@pytest.mark.parametrize("text", ["แฟนต่างชาติขอเงินค่าตั๋วเครื่องบิน", "มีคนในเฟสขอยืมเงินบอกว่าเป็นเพื่อน"])
def test_romance_and_friend_impersonation(text):
    a = assess(text)
    assert "romance" in a["scam"] and a["text_risk"] >= 75
    r = compose(text)
    assert "วิดีโอคอล" in r and "วางสาย" not in r


def test_financial_control_by_partner():
    assert assess("ผัวไม่ให้เงินใช้")["relationship"]


@pytest.mark.parametrize("text,word", [("คุณคือใคร", "เป็น AI ไม่ใช่คน"), ("คุณเป็นคนหรือ AI", "เป็น AI ไม่ใช่คน"),
                                       ("who are you", "an AI, not a person")])
def test_who_are_you(text, word):
    assert word in compose(text)


def test_vega_introduces_itself_as_vega():
    assert "ผมคือ VEGA" in compose("คุณคือใคร", voice_mode="vega")


@pytest.mark.parametrize("text,word", [("hi", "Hi!"), ("help", "Are you safe"), ("I'm pregnant and scared", "1663"),
                                       ("I lost my job", "Social Security"), ("my dad drinks every night", "1413")])
def test_english_replies(text, word):
    r = compose(text)
    assert word in r and "Let's lay this out" not in r


@pytest.mark.parametrize("text", ["อยากรู้ว่าตัวเองเป็นซึมเศร้าไหม", "รู้สึกว่างเปล่า", "ไม่อยากคุยกับใคร", "ฝันร้ายบ่อย"])
def test_low_mood_goes_to_stress_not_diagnosis(text):
    assert _top(text) == "stress"


# ── ไม่จับผิด ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("text", ["กลัวอ้วนเลยออกกำลังกาย", "อาหารเป็นพิษทำให้อาเจียน", "มีเสียงคนคุยกันข้างห้อง",
                                  "เลี้ยงลูกคนเดียวเหนื่อยมาก", "ถูกจับได้ว่าโกหก", "โดนจับผิดทุกเรื่อง",
                                  "ตำรวจจับตัวคนร้ายได้แล้ว"])
def test_round3_no_false_alarm(text):
    a = assess(text)
    assert not set(a["topics"]) & {"eating", "psychosis", "caregiver", "legal"} and not a["crisis"]


def test_run_passes_round3_hotlines(client):
    client.post("/run", json={"input": "ได้ยินเสียงคนพูดในหัว"})
    assert "จิตแพทย์" in FAKE_LLM["prompts"][-1]
