"""เวลาตอบของแชท: ต้องวัดได้ (p50/p95/p99) และคนที่รอนานต้องไม่ถูกทิ้งให้เงียบ
ที่มา: ความเห็นใน LinkedIn — เวลาตอบของ LLM ที่แกว่งมากทำลายความนิ่งที่ระบบช่วยคนในวิกฤตต้องมี · เดิมไม่ได้วัดเลย"""
from fastapi.testclient import TestClient

from core import latency
from tests._front import front_page


def test_percentiles_nearest_rank():
    latency.reset()
    assert latency.summary() == {"n": 0}
    for ms in range(1, 101):
        latency.record(ms * 100)                   # 100 … 10,000 ms
    s = latency.summary()
    assert (s["n"], s["p50"], s["p95"], s["p99"], s["max"]) == (100, 5000, 9500, 9900, 10000)
    assert s["over_10s"] == 0
    latency.record(45_000)
    assert latency.summary()["over_10s"] == 1


def test_only_the_last_500_are_kept_and_nothing_but_numbers():
    latency.reset()
    for i in range(700):
        latency.record(i)
    assert latency.summary()["n"] == 500 and latency.summary()["max"] == 699


def test_run_is_timed_and_health_reports_it():
    import app as appmod
    latency.reset()
    c = TestClient(appmod.app)
    r = c.post("/run", json={"input": "สวัสดี"})
    assert "app;dur=" in r.headers.get("server-timing", "")
    h = c.get("/health").json()["reply_ms"]
    assert h["n"] >= 1 and h["p99"] >= h["p50"] >= 0
    before = h["n"]
    c.get("/health"); c.post("/api/driftzero", json={"input": "x"})
    assert c.get("/health").json()["reply_ms"]["n"] == before            # จับเวลาเฉพาะ /run


def test_waiting_user_is_told_we_are_still_here_then_given_numbers():
    page = front_page()
    assert "[6000, 'ยังอยู่ตรงนี้นะคะ" in page and "[20000, 'ใช้เวลานานกว่าปกติ" in page
    assert "1669" in page and "if(!th.parentNode) return;" in page         # ได้คำตอบแล้วไม่โผล่ตามมา
