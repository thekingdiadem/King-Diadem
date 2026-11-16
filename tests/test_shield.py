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


def test_time_is_one_every_closed_door_takes_the_same_time():
    """เวลาเป็นเอกภาพ: ทางที่ไม่มีจริง · method ผิด · ไม่มีสิทธิ์ — ต่างก็รอเท่ากัน จับเวลาแยกไม่ออก"""
    waits = {}
    for name, call in (("missing", lambda c: c.get("/wp-admin")), ("method", lambda c: c.delete("/hello")),
                       ("auth", lambda c: c.post("/login"))):
        slept = []
        call(_app([0.0], slept))
        waits[name] = sum(slept)
    assert set(waits.values()) == {S.EVEN_S}


def test_success_and_crisis_chat_are_never_padded():
    slept = []
    c = _app([0.0], slept)
    assert c.get("/hello").status_code == 200 and c.post("/run").status_code == 200
    assert not slept


def _app_ip(clock, slept, ip_box):
    a = FastAPI()

    @a.get("/hello")
    def hello():
        return {"ok": 1}

    async def fake_sleep(s):
        slept.append(s)
    a.add_middleware(S.ShieldMiddleware, shape_from=lambda: a, clock=lambda: clock[0], sleep=fake_sleep,
                     ip_of=lambda scope: ip_box[0])
    return TestClient(a)


SCANNER = {"user-agent": "sqlmap/1.7", "accept": "*/*"}


def test_changing_ip_does_not_hide_the_same_gait():
    """เครื่องสแกนเปลี่ยน IP ทุกคำขอ — แต่ท่าเดินเหมือนเดิม โล่ก็ยังจำได้"""
    clock, slept, ip = [0.0], [], ["10.0.0.0"]
    c = _app_ip(clock, slept, ip)
    for i in range(14):
        ip[0] = f"10.0.{i}.{i}"
        c.get(f"/probe{i}", headers=SCANNER)
    tarpit = [s for s in slept if s != S.EVEN_S]
    assert tarpit and max(tarpit) >= 1.0


def test_a_real_person_sharing_the_gait_is_not_slowed_on_real_pages():
    """คนจริงที่บังเอิญท่าเดินเหมือนเครื่องสแกน แต่มาจาก IP ของตัวเอง เข้าหน้าที่มีจริงได้ทันที"""
    clock, slept, ip = [0.0], [], ["10.0.0.0"]
    c = _app_ip(clock, slept, ip)
    for i in range(14):
        ip[0] = f"10.1.{i}.{i}"
        c.get(f"/probe{i}", headers=SCANNER)
    slept.clear()
    ip[0] = "203.0.113.7"
    assert c.get("/hello", headers=SCANNER).status_code == 200
    assert not slept


def test_gait_forgets_too():
    clock, slept, ip = [0.0], [], ["x"]
    c = _app_ip(clock, slept, ip)
    for i in range(14):
        ip[0] = f"10.2.{i}.{i}"
        c.get(f"/probe{i}", headers=SCANNER)
    clock[0] += 3 * 3600
    slept.clear()
    ip[0] = "10.9.9.9"
    c.get("/probe-again", headers=SCANNER)
    assert slept == [S.EVEN_S]                                     # แค่เวลาเอกภาพ ไม่มีหน่วงค้างจากเมื่อสามชั่วโมงก่อน
