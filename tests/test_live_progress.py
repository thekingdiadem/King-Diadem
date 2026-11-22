"""สถานะเบื้องหลังจริงระหว่างรอ (core/progress · /api/progress/<rid>) — เจ้าของโปรเจกต์อยากได้แบบ "Percolating…"
ต้องเป็นขั้นที่ระบบทำจริง ไม่เก็บข้อความของผู้ใช้ และเนื้อแชทไม่มีศัพท์ระบบ"""
import re

from core import progress
from tests._front import front_page


def test_real_stages_are_recorded_in_order(client):
    rid = "abcd1234efgh"
    r = client.post("/run", json={"input": "จะกู้เงิน 3 แสนเปิดร้านกาแฟกับเพื่อน ดีไหม", "rid": rid})
    assert r.status_code == 200
    j = client.get(f"/api/progress/{rid}").json()
    stages = [s["stage"] for s in j["stages"]]
    assert stages[0] == "receive" and "risk" in stages and j["done"] is True
    assert stages.index("risk") > stages.index("receive")
    assert all(s in progress.STAGES for s in stages)


def test_progress_never_contains_the_message(client):
    rid = "zzzz9999yyyy"
    client.post("/run", json={"input": "ความลับมาก 0812345678", "rid": rid})
    body = client.get(f"/api/progress/{rid}").text
    assert "ความลับ" not in body and "0812345678" not in body


def test_bad_or_unknown_rid_is_harmless(client):
    assert client.get("/api/progress/nope").json() == {"stages": [], "done": False}
    assert client.get("/api/progress/" + "a" * 40).json() == {"stages": [], "done": False}
    r = client.post("/run", json={"input": "สวัสดี", "rid": "../../etc"})
    assert r.status_code == 200                                   # rid เพี้ยน = ไม่ติดตาม คำตอบยังมาปกติ


def test_memory_is_bounded():
    for i in range(progress.MAX_REQUESTS + 50):
        progress.begin(f"x{i:011d}")
        progress.end()
    assert len(progress._runs) <= progress.MAX_REQUESTS + 1


def test_front_shows_plain_words_and_module_names_only_while_waiting():
    page = front_page()
    assert "rid:rid" in page and "Live.watch(rid, th)" in page and "stopLive();" in page
    for stage in progress.STAGES:
        assert re.search(rf"\b{stage}: \['", page), stage                # ทุกขั้นมีคำง่ายๆ
    assert "LYLA · DriftZero" not in re.sub(r"/\*[\s\S]*?\*/", "", page.split("var Live")[0][-20000:])
