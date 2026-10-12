"""ตัววัดโหลด (SECURITY/survival_mode): ย้ายกลับจาก legacy/ แบบอ่านอย่างเดียว
รุ่นเดิมปฏิเสธทุกคำขอ 30 วินาทีเมื่อ error ถี่ — รวมถึงข้อความของคนที่กำลังวิกฤต · รุ่นนี้วัดอย่างเดียว ไม่บล็อกใคร"""
import asyncio
import inspect

import pytest

import SECURITY.survival_mode as sm


@pytest.fixture(autouse=True)
def _fresh():
    sm.reset_for_tests()
    yield
    sm.reset_for_tests()


def test_health_shows_load_after_a_message(client):
    client.post("/run", json={"input": "วันนี้อากาศดี"})
    load = client.get("/health").json()["load"]
    assert load["mode"] == "observe_only"
    assert load["requests_60s"] == 1 and load["concurrent"] == 0 and load["concurrent_peak"] >= 1
    assert load["latency_p50_s"] is not None and load["errors_60s"] == 0


def test_only_heavy_routes_are_counted(client):
    client.get("/health"); client.get("/guide"); client.get("/static/cinema.css")
    assert client.get("/health").json()["load"]["requests_60s"] == 0


def test_never_blocks_even_when_errors_pile_up(client):
    """error 5xx ถี่ๆ ต้องไม่ทำให้คำขอถัดไปถูกปฏิเสธ (รุ่นเดิมเปิด circuit แล้วปฏิเสธ 30 วิ)"""
    for _ in range(15):
        sm.request_end(sm.request_start(), success=False)
    stats = sm.get_survival_stats()
    assert stats["errors_60s"] == 15 and stats["health"] == "degraded"
    r = client.post("/run", json={"input": "อยากตาย ไม่ไหวแล้ว"})
    assert r.status_code == 200 and r.json().get("ai_response")
    src = inspect.getsource(sm)
    assert "allowed" not in src and "retry_after" not in src and "circuit" not in src.split('"""', 2)[2]


def test_server_errors_are_counted_and_concurrency_never_sticks():
    async def boom(scope, receive, send):
        raise RuntimeError("x")

    async def five_hundred(scope, receive, send):
        await send({"type": "http.response.start", "status": 503, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    async def noop(msg):
        return None

    scope = {"type": "http", "path": "/run"}
    with pytest.raises(RuntimeError):
        asyncio.run(sm.LoadMonitorMiddleware(boom)(scope, None, noop))
    asyncio.run(sm.LoadMonitorMiddleware(five_hundred)(scope, None, noop))
    s = sm.get_survival_stats()
    assert s["errors_60s"] == 2 and s["concurrent"] == 0          # ล้มกลางทาง ตัวนับพร้อมกันก็ไม่ค้าง


def test_no_personal_data_is_kept():
    """ไม่เก็บ IP ข้อความ หรือตัวตน — มีแค่เวลาและสถานะ"""
    src = inspect.getsource(sm)
    for word in ("client", "headers[", "body", "email", "ip_"):
        assert word not in src.split("class LoadMonitorMiddleware")[0], word
