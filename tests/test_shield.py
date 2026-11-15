"""โล่แบนเงื่อนไข (SECURITY/shield.py)"""
import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from SECURITY import shield as S


def _app(clock, slept):
    a = FastAPI()

    @a.get("/hello")
    def hello():
        return {"ok": 1}

    @a.post("/run")
    def run():
        return {"reply": "1323"}

    @a.post("/login")
    def login():
        from fastapi import HTTPException
        raise HTTPException(401)

    async def fake_sleep(s):
        slept.append(s)
    a.add_middleware(S.ShieldMiddleware, shape_from=lambda: a, clock=lambda: clock[0], sleep=fake_sleep)
    return TestClient(a)


def test_a_million_patterns_get_one_identical_answer():
    c = _app([0.0], [])
    bodies = {(r.status_code, r.content) for r in (c.get(p) for p in
              ("/.env", "/wp-admin", "/../../etc/passwd", "/api/v1/admin?id=1' OR 1=1", "/%00", "/phpmyadmin/index.php"))}
    assert bodies == {(404, S._UNIFORM)}
    assert c.delete("/hello").status_code == 405                  # มีทางนี้จริงแต่ method ผิด ตอบตามมาตรฐาน (นับคะแนน)


def test_scanner_becomes_a_turtle_but_decays():
    clock, slept = [0.0], []
    c = _app(clock, slept)
    for i in range(12):
        c.get(f"/probe{i}")
    c.get("/hello")
    assert slept and slept[-1] >= 1.0                             # ช้าลงทวีคูณ
    clock[0] += 3 * 3600                                           # สามชั่วโมงต่อมา ไม่ถูกตราหน้าถาวร
    slept.clear()
    c.get("/hello")
    assert not slept


def test_repeated_auth_failures_count_as_a_condition():
    slept = []
    c = _app([0.0], slept)
    for _ in range(6):
        c.post("/login")
    c.get("/hello")
    assert slept


def test_crisis_chat_never_slowed():
    slept = []
    c = _app([0.0], slept)
    for i in range(40):
        c.get(f"/x{i}")
    slept.clear()
    r = c.post("/run")
    assert r.status_code == 200 and not slept


def test_normal_human_with_one_bad_link_is_not_slowed():
    slept = []
    c = _app([0.0], slept)
    c.get("/old-link", headers={"accept": "text/html"})
    for _ in range(5):
        c.get("/hello")
    assert not slept


def test_delay_is_capped():
    assert S.delay_for(1000) == S.MAX_DELAY_S and S.delay_for(0) == 0


def test_wired_into_real_app_as_outermost_layer():
    src = open("app.py", encoding="utf-8").read()
    assert src.index("app.add_middleware(_ShieldHook)") > src.index("app.add_middleware(BodyLimitMiddleware)")
    assert '"shield":' in src


def test_shield_404_is_byte_identical_to_app_404():
    a = FastAPI()

    @a.get("/item/{i}")
    def item(i: int):
        from fastapi import HTTPException
        raise HTTPException(404)
    r = TestClient(a).get("/item/1")
    assert r.content == S._UNIFORM and r.headers["content-type"] == "application/json"
