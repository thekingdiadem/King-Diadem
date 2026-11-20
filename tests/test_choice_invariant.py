"""O ≥ 1 — ไม่มีคำตอบเรื่องด่วนไหนที่ปล่อยให้คนไม่เหลือทางไปเลย (core/choice.py)

"บางครั้งเราไม่ได้ต้องการคำตอบที่สมบูรณ์แบบ เราแค่ต้องการรู้ว่ายังมีทางเลือกอยู่ในคำตอบนั้นหรือเปล่า"
ทุกเรื่องด่วน (Risk ≥ 60) ทุกภาษา ต้องได้คำตอบที่มีขั้นตอนที่ทำได้ + ช่องทางขอความช่วยเหลืออย่างน้อยหนึ่งทาง
ถ้าล้ม: ข้อความที่ได้ O = 0 จะแสดงอยู่ในรายงาน — เติมขั้นตอนหรือสายด่วนให้หัวข้อนั้น อย่าลดเกณฑ์
"""
import itertools
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import sweep_all as S  # noqa: E402
from core.choice import choices_left  # noqa: E402
from core.kernel_voice import assess, compose  # noqa: E402


def _cases():
    rnd = random.Random(7)
    th = sorted({f.format(w=w, e=e).strip() for w, e, f in itertools.product(S.URGENT_WHO, S.URGENT_EVENTS, S.URGENT_FRAME)})
    en = sorted({f.format(w=w, e=e) for w, e, f in itertools.product(S.EN_URG_WHO, S.EN_URG_EVENTS, S.EN_URG_FRAME)})
    intl = [t for xs in S.INTL_URGENT.values() for t in xs]
    return rnd.sample(th, 250) + [t for t, _ in rnd.sample(S._violence_cases(), 150)] + rnd.sample(en, 150) + intl


def test_every_urgent_reply_leaves_at_least_one_way_out():
    zero = []
    for t in _cases():
        if assess(t)["risk_shown"] < 60:
            continue
        if choices_left(compose(t)) < 1:
            zero.append(t)
    assert not zero, f"O = 0 ใน {len(zero)} ข้อความ เช่น {zero[:5]}"


@pytest.mark.parametrize("reply,expect", [
    ("", 0),
    ("ใจเย็นๆ นะ", 0),                                  # ปลอบอย่างเดียว ไม่มีทางไป
    ("ขอบคุณที่บอกนะ\n\n1) โทร 1323 ได้ตลอด 24 ชม.\n2) ไปอยู่ใกล้ใครสักคน", 2),
    ("Stay calm.\n\n1) Call 911 now.", 1),
])
def test_choices_left_counts_ways_out(reply, expect):
    assert choices_left(reply) == expect


def test_live_reply_adds_a_last_way_out_when_a_topic_forgets(monkeypatch):
    """ถ้าวันหน้ามีหัวข้อใหม่ที่ลืมใส่ทางไป LYLA ต้องเติมทางสุดท้ายให้เองตอนตอบ"""
    import core.kernel_voice as K
    monkeypatch.setattr(K, "_compose_before_choice", lambda text, *a, **k: "ใจเย็นๆ นะ\n\nเดี๋ยวก็ดีขึ้น")
    r = K.compose("แม่หมดสติ ไม่หายใจ")
    assert choices_left(r) >= 1 and "1669" in r
