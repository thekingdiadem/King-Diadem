"""หน้าจอจริง: "ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง" → ตอบสั้นๆ "นี่" เคยกลับเป็น GENERAL Risk 0"""
import pytest


@pytest.mark.parametrize("first", ["ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง", "อยากฆ่าพ่อ", "เจอปืนในบ้าน ไม่รู้ของใคร",
                                   "ยายโดนหลานด่าทุกวัน"])
@pytest.mark.parametrize("reply", ["นี่", "ไม่รู้"])
def test_short_reply_keeps_new_urgent_topics(client, first, reply):
    from tests.conftest import FAKE_LLM
    d = client.post("/run", json={"input": reply, "history": [{"role": "user", "content": first},
                                                               {"role": "assistant", "content": "ตอนนี้ยังได้ยินอยู่ไหมคะ"}]}).json()
    assert d["risk_score"] >= 30 and "เรื่องด่วน" in FAKE_LLM["prompts"][-1]


def test_short_reply_after_theft_keeps_context(client):
    """ถูกขโมยไม่ใช่เรื่องเสี่ยงต่อชีวิต (ไม่ดันความเสี่ยง) แต่คำตอบสั้นถัดไปต้องยังคุยเรื่องเดิม"""
    from tests.conftest import FAKE_LLM
    client.post("/run", json={"input": "ไม่รู้", "history": [{"role": "user", "content": "โดนวิ่งราว มือถือหาย"}]})
    assert "การถูกขโมย" in FAKE_LLM["prompts"][-1]
