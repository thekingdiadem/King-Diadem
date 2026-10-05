"""ความจำข้ามแชทของ LYLA — เฉพาะผู้ที่เข้าสู่ระบบ · เรื่องเปราะบางไม่เก็บข้อความ · ผู้ใช้ดู/ปิด/ล้างเองได้"""
from DATABASE.db import auto_extract_memory, build_memory_context, list_memory
from tests.conftest import FAKE_LLM


def _contents(email):
    return " ".join(m["content"] for m in list_memory(email))


def test_goal_is_remembered_and_reaches_next_chat(user):
    user.post("/run", json={"input": "เป้าหมายปีนี้คืออยากเปิดร้านกาแฟเล็กๆ"})
    assert "ร้านกาแฟ" in _contents(user.email)
    user.post("/run", json={"input": "วันนี้เหนื่อยนิดหน่อย"})          # แชทใหม่ ไม่มี history
    assert "ร้านกาแฟ" in FAKE_LLM["prompts"][-1] and "[MEMORY" in FAKE_LLM["prompts"][-1]


def test_sensitive_story_is_not_stored_as_text(user):
    user.post("/run", json={"input": "เบื่อชีวิต พ่อตีหัวทุกวัน"})
    mem = _contents(user.email)
    assert "พ่อตีหัว" not in mem and "เบื่อชีวิต" not in mem
    assert "เคยเล่าเรื่องที่หนักมาก" in mem


def test_turning_memory_off_stops_saving_and_reading(user):
    user.post("/api/memory", json={"action": "off"})
    user.post("/run", json={"input": "เป้าหมายคืออยากเรียนต่อปริญญาโท"})
    assert "ปริญญาโท" not in _contents(user.email)
    assert build_memory_context(user.email) == ""
    assert user.get("/api/memory").json()["enabled"] is False


def test_clear_memory(user):
    user.post("/run", json={"input": "เป้าหมายคืออยากเก็บเงินซื้อบ้าน"})
    assert user.get("/api/memory").json()["items"]
    assert user.post("/api/memory", json={"action": "clear"}).json()["ok"]
    assert user.get("/api/memory").json()["items"] == []
    assert "ซื้อบ้าน" not in build_memory_context(user.email)            # บทสนทนาเก่าก็ไม่ถูกดึงมาอีก


def test_memory_api_needs_login(client):
    assert client.get("/api/memory").status_code == 401
    assert client.post("/api/memory", json={"action": "clear"}).status_code == 401


def test_cannot_read_someone_elses_memory(user, client):
    """อีเมลที่ใช้ดึงความจำมาจาก session เท่านั้น — ส่ง user_email ใน body มาไม่มีผล"""
    victim = user.email
    auto_extract_memory(victim, "เป้าหมายคืออยากย้ายไปอยู่เชียงใหม่", "", "general")
    client.cookies.clear()
    client.post("/run", json={"input": "สวัสดี", "user_email": victim})
    assert "เชียงใหม่" not in FAKE_LLM["prompts"][-1]


def test_anonymous_has_no_memory():
    auto_extract_memory("anonymous", "เป้าหมายคืออยากรวย", "", "general")
    assert build_memory_context("anonymous") == ""


def test_memory_tags_never_reach_the_user():
    from core.llm_gemini import scrub_internal
    assert scrub_internal("สวัสดีค่ะ\n[MEMORY — สิ่งที่รู้เกี่ยวกับผู้ใช้]") == "สวัสดีค่ะ"


def test_topics_are_saved_in_thai(user):
    user.post("/run", json={"input": "อยากเปิดร้านกาแฟ ทุน 200000"})
    assert "ธุรกิจ" in _contents(user.email) and "business" not in _contents(user.email)


def test_mobile_menu_is_not_closed_by_every_click():
    """<body data-view> เคยทำให้ทุกคลิกปิดเมนู — ปุ่ม ☰ บนมือถือเปิดไม่ได้"""
    import pathlib
    page = pathlib.Path(__file__).resolve().parent.parent.joinpath("static", "index.html").read_text(encoding="utf-8")
    assert "e.target.closest('button[data-view], a[data-view]')" in page
    assert "e.target.closest('[data-view]')" not in page
