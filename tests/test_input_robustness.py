"""ความแข็งแกร่งของ /run และหน้าสาธารณะ ต่อ "ของแปลกๆ" ที่ส่งเข้ามา (เสริม test_robustness.py ที่ตรวจตัวจับ)
พี่คิง: "ลองทดสอบความแข็งแกร่ง ถ้ามันพังเราก็จะได้ซ่อมก่อน" · กติกาเดียว: ห้ามมี 500 ไม่ว่าจะส่งอะไรเข้ามา
คนที่พิมพ์ผิดๆ ถูกๆ ตอนลำบากต้องไม่เจอจอขาว · วัดได้ รันซ้ำได้ ใครแก้แล้วทำพังเทสต์นี้จะร้องทันที"""
import pytest

WEIRD = [
    {"input": ""}, {}, {"input": None}, {"input": 123}, {"input": ["a", "b"]},
    {"input": {"x": 1}}, {"input": "ก" * 200000}, {"input": "hi\x00there"},
    {"input": "👨‍👩‍👧‍👦" * 3000}, {"input": "\r\n\t\x1b[31m" * 100},
    {"input": '{"$ne": null}'}, {"input": "   "}, {"input": "\n" * 10000}, {"input": "‮" * 500},
]


@pytest.mark.parametrize("payload", WEIRD, ids=lambda p: str(p)[:24])
def test_run_never_500s_on_weird_json(client, payload):
    r = client.post("/run", json=payload, headers={"cf-connecting-ip": "203.0.113.7"})
    assert r.status_code < 500, r.text[:200]


RAW = [
    b'{"input": "\\ud800 lone surrogate"}',          # JSON ถูก แต่ decode เป็น surrogate เดี่ยว
    b'{"input": "\\ud834\\udd1e \\ud800 mixed"}',
    b'{"input": ',                                    # JSON ขาดครึ่ง
    b'<<<not json>>>', b'', b'{"input": 1e9999}',     # เลขล้น
    b'{"input":"x","a":' + b'[' * 1500 + b']' * 1500 + b'}',   # ซ้อนลึก
]


@pytest.mark.parametrize("body", RAW, ids=lambda b: b[:20])
def test_run_never_500s_on_raw_body(client, body):
    r = client.post("/run", content=body, headers={"content-type": "application/json", "cf-connecting-ip": "203.0.113.8"})
    assert r.status_code < 500, r.text[:200]


def test_public_pages_do_not_crash_on_bad_params(client):
    for path in ["/api/quakes?lat=abc&lon=xyz", "/api/hazards", "/r/no-such-token"]:
        assert client.get(path).status_code < 500, path


def test_many_distinct_users_at_once_all_served(client):
    import concurrent.futures as cf
    def hit(i):
        return client.post("/run", json={"input": f"ช่วยคิดเรื่องงาน {i}"},
                           headers={"cf-connecting-ip": f"198.51.{i % 256}.{i // 256 + 1}"}).status_code
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        codes = list(ex.map(hit, range(48)))
    assert all(c < 500 for c in codes), codes


ODD_BODIES = [b"[1,2]", b'"text"', b"42", b"null", b"true"]


@pytest.mark.parametrize("path", ["/api/practice", "/api/driftzero"])
@pytest.mark.parametrize("body", ODD_BODIES, ids=lambda b: b.decode())
def test_json_that_is_not_an_object_is_refused_politely(client, path, body):
    # JSON ที่ถูกไวยากรณ์แต่ไม่ใช่ object เคยทำให้ (body or {}).get(...) พัง → 500
    r = client.post(path, content=body, headers={"content-type": "application/json", "cf-connecting-ip": "203.0.113.60"})
    assert r.status_code == 400, (path, body, r.status_code, r.text[:120])


def test_every_post_route_survives_odd_bodies(client, app_module):
    """กวาดทุกเส้นทาง POST — เส้นทางใหม่ที่ลืมตรวจชนิดของ body จะถูกจับที่นี่ (503 = ระบบย่อยปิดอยู่ ไม่ใช่พัง)"""
    from fastapi.testclient import TestClient
    c = TestClient(app_module.app, raise_server_exceptions=False)
    paths = sorted({r.path for r in app_module.app.routes if "POST" in getattr(r, "methods", set())
                    and "{" not in r.path and "webhook" not in r.path})
    assert len(paths) > 20
    broken = []
    for i, p in enumerate(paths):
        for b in ODD_BODIES + [b'{"input": ["a"], "prior": {"asks": "x", "text": 5}}']:
            r = c.post(p, content=b, headers={"content-type": "application/json", "cf-connecting-ip": f"203.0.114.{i}"})
            if r.status_code >= 500 and r.status_code != 503:
                broken.append((p, b.decode()[:30], r.status_code))
    assert not broken, broken
