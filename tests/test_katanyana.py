"""กตญาณ (core/katanyana): จำก้าวที่ตั้งใจไว้หนึ่งอย่าง ถามครั้งเดียวในวันถัดไป รับรู้เมื่อทำแล้ว"""
from DATABASE.db import _mem_value, save_memory

STORY = "ค่าเช่าค้างมาสองเดือนแล้ว กลัวว่าเจ้าของบ้านจะไล่ออกพรุ่งนี้ อยากมีงานที่มั่นคง"


def _yesterday(email):
    step = _mem_value(email, "next_step")
    save_memory(email, "next_step", "2000-01-01|" + step.split("|", 1)[1], "general", importance=3)


def test_story_is_remembered_as_one_fact_only(user):
    user.post("/run", json={"input": STORY})
    step = _mem_value(user.email, "next_step")
    assert step and step.endswith("|ค่าเช่าค้างมาสองเดือนแล้ว")
    assert "กลัว" not in step                       # เก็บแค่สิ่งที่เกิดขึ้นแล้ว ไม่เก็บเรื่องทั้งหมด


def test_next_day_greeting_asks_once_without_retelling(user):
    user.post("/run", json={"input": STORY})
    _yesterday(user.email)
    first = user.post("/run", json={"input": "สวัสดี"}).json()["ai_response"]
    assert "ได้ลองไหม" in first and "ไม่ต้องเล่าก็ได้" in first
    assert "ค่าเช่า" not in first                    # ไม่ทวนเรื่องเดิม
    again = user.post("/run", json={"input": "สวัสดี"}).json()["ai_response"]
    assert "ได้ลองไหม" not in again                  # ไม่ถามซ้ำ


def test_saying_done_is_acknowledged_and_forgotten(user):
    user.post("/run", json={"input": STORY})
    _yesterday(user.email)
    user.post("/run", json={"input": "สวัสดี"})
    out = user.post("/run", json={"input": "ทำแล้ว ไปคุยกับเจ้าของบ้านมา"}).json()["ai_response"]
    assert "ก้าวนั้นทำเสร็จแล้วจริงๆ" in out
    assert not _mem_value(user.email, "next_step")


def test_same_day_or_new_story_is_not_interrupted(user):
    user.post("/run", json={"input": STORY})
    assert "ได้ลองไหม" not in user.post("/run", json={"input": "สวัสดี"}).json()["ai_response"]      # วันเดียวกัน
    _yesterday(user.email)
    out = user.post("/run", json={"input": "วันนี้โดนหัวหน้าด่าอีกแล้ว"}).json()["ai_response"]
    assert "ได้ลองไหม" not in out                    # เขากำลังเล่าเรื่องใหม่ ไม่แทรก


def test_sensitive_story_is_never_followed_up(user):
    user.post("/run", json={"input": "อยากตาย กลัวว่าจะไม่มีใครรัก ไม่อยากอยู่แล้ว เมื่อวานโดนไล่ออก"})
    assert not _mem_value(user.email, "next_step")


def test_memory_off_means_no_follow_up(user):
    user.post("/api/memory", json={"action": "off"})
    user.post("/run", json={"input": STORY})
    assert not _mem_value(user.email, "next_step")


def test_step_is_never_sent_to_the_ai_prompt(user):
    from DATABASE.db import build_memory_context
    user.post("/run", json={"input": STORY})
    assert "ค่าเช่าค้าง" not in build_memory_context(user.email)
