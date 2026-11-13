"""ด่านสุดท้ายของคำตอบจาก AI — ข้อความมีความเสี่ยง คำตอบต้องมีเบอร์ช่วยเหลือ (core/kernel_voice.ensure_safety_line)

ทดสอบด้วย AI ปลอมที่ตอบผิดแบบเลวร้ายที่สุด (แผนสามขั้นทั่วไป ไม่มีเบอร์): เดิม "อยากตาย" "ผัวตีฉัน"
และชุดประโยคตามอารมณ์ทั้งหมด 195 ข้อ ถึงผู้ใช้โดยไม่มีเบอร์เลยสักข้อ
หน้าเว็บโชว์กล่องสายด่วนเฉพาะเมื่อคำตอบมี 1323/1669 — AI ลืมครั้งเดียว คนที่ต้องการที่สุดก็ไม่เห็นเบอร์
"""
import re
import uuid

import pytest

from tests.conftest import FAKE_LLM
from tests.test_mood_safety_intl import ANGER_TH_EN, HOT, LIGHT, TH_EN_HOT, TH_EN_LIGHT, ANGER_LIGHT
from tests.test_mood_safety_net import DANGER_NOW, HEAVY, HIDDEN_CRISIS
from tests.test_mood_safety_net import LIGHT as TH_EN_EVERYDAY

BAD_TH = "ลองแบ่งเป็นสามขั้น 1) จดสิ่งที่เกิดขึ้น 2) แยกสิ่งที่คุมได้ 3) เลือกก้าวเล็ก\n— LYLA ◈"
BAD_X = "Let's plan: 1) write it down 2) split what you control 3) one small step\n— LYLA ◈"
NUM = re.compile(r"1323|1669|191|1300|110|112|911|988|findahelpline")

HOT_ALL = ["อยากตาย", "ผัวตีฉัน", "i want to die"] + DANGER_NOW + HIDDEN_CRISIS + HEAVY + ANGER_TH_EN + TH_EN_HOT + \
          [x for xs in HOT.values() for x in xs]
LIGHT_ALL = TH_EN_EVERYDAY + TH_EN_LIGHT + ANGER_LIGHT + [x for xs in LIGHT.values() for x in xs]


def _run(client, text):
    FAKE_LLM.update(text=BAD_TH if re.search(r"[฀-๿]", text) else BAD_X)
    ip = "10.77.%d.%d" % tuple(uuid.uuid4().bytes[:2])
    return client.post("/run", json={"input": text, "history": []}, headers={"cf-connecting-ip": ip}).json()


@pytest.mark.parametrize("text", HOT_ALL)
def test_risky_message_always_reaches_the_user_with_a_number(client, text):
    r = _run(client, text)
    assert r.get("answer_source") == "llm"
    out = r["ai_response"]
    assert NUM.search(out), out
    assert out.startswith(BAD_TH[:10]) or out.startswith(BAD_X[:10])     # ไม่ลบคำตอบของ AI แค่เติม
    assert out.rstrip().endswith("— LYLA ◈")                            # บรรทัดเบอร์อยู่ก่อนลายเซ็น


@pytest.mark.parametrize("text", LIGHT_ALL)
def test_everyday_message_is_left_alone(client, text):
    r = _run(client, text)
    assert r["ai_response"] in (BAD_TH, BAD_X), r["ai_response"]


def test_reply_that_already_has_a_number_is_not_touched():
    from core.kernel_voice import ensure_safety_line
    good = "อยู่ตรงนี้นะคะ โทร 1323 ได้ตลอด 24 ชม.\n— LYLA ◈"
    assert ensure_safety_line("อยากตาย", good) == good


@pytest.mark.parametrize("text,kind", [("อยากตาย", "crisis"), ("ผัวตีฉัน", "danger"), ("ดิ่งมากเลยวันนี้", "soft"),
                                       ("i'm so angry i could kill him", "danger"), ("วันนี้อากาศดีจัง", None)])
def test_the_number_fits_the_kind_of_trouble(text, kind):
    from core.kernel_voice import assess, safety_kind
    assert safety_kind(assess(text)) == kind


def test_other_languages_get_numbers_in_their_own_words():
    from core.kernel_voice import ensure_safety_line
    out = ensure_safety_line("涙が止まらない", BAD_X)
    assert "タイにいる場合" in out and "1323" in out
