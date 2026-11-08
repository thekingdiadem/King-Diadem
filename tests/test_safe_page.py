"""หน้าฉุกเฉินแตะเดียว /safe — "ฉันไม่ปลอดภัย · หาที่ปลอดภัยใกล้ฉัน"

พี่คิง: "ทางหนีทีไล่ เผื่อใครหนีคนร้าย" — คำตอบเดิมบอกว่า "ไปร้านสะดวกซื้อหรือสถานีตำรวจ" แต่คนที่กำลังกลัวไม่รู้ว่าอยู่ตรงไหน
· โทร 191/1669/1300 แตะเดียว · ส่งตำแหน่งให้คนที่ไว้ใจ · ที่ที่มีคนใกล้ตัว (Google Maps ใช้ตำแหน่งในเครื่อง)
· ตำแหน่งไม่ถูกส่งเข้าเซิร์ฟเวอร์ · หน้าเบา ไม่โหลดฟอนต์/ภาพ/ไลบรารี
"""
import re
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
SAFE = (ROOT / "static" / "safe.html").read_text(encoding="utf-8")


def _client():
    import app
    return TestClient(app.app)


def test_safe_page_is_served_and_location_is_allowed_for_our_pages_only():
    r = _client().get("/safe")
    assert r.status_code == 200 and "ไม่ปลอดภัยตอนนี้" in r.text
    pp = r.headers.get("permissions-policy", "")
    assert "geolocation=(self)" in pp and "camera=()" in pp      # เดิม geolocation=() ทำให้ปุ่มตำแหน่งของ /sky ใช้ไม่ได้ด้วย


def test_one_tap_calls_and_share_location():
    for n in ("191", "1669", "1300"):
        assert f'href="tel:{n}"' in SAFE
    assert 'id="share"' in SAFE and "navigator.share" in SAFE and "sms:?&body=" in SAFE
    assert "navigator.clipboard.writeText(msg).then(" in SAFE      # บอกว่าคัดลอกแล้วเมื่อคัดลอกได้จริงเท่านั้น


def test_location_never_goes_to_our_server():
    assert "fetch(" not in SAFE and "XMLHttpRequest" not in SAFE and "sendBeacon" not in SAFE
    assert "/universe#safe=" in SAFE                                # ส่งต่อแผนที่ของเราผ่าน # (ไม่ถึงเซิร์ฟเวอร์)
    assert "https://www.google.com/maps/" in SAFE and "key=" not in SAFE


def test_page_is_light_and_csp_safe():
    assert "fonts.googleapis.com" not in SAFE and "<img" not in SAFE and 'src="http' not in SAFE
    assert not re.search(r"<[^>]+\son[a-z]+=", SAFE)


def test_both_languages_have_real_place_names():
    for name in ("Police station", "Convenience store", "Petrol station", "Hospital"):
        assert f'data-name-en="{name}"' in SAFE


def test_chat_offers_the_safe_page_first_when_followed():
    from core.engine_bridge import nearby
    from core.kernel_voice import assess
    t = "มีคนเดินตามมา กลัวมาก จะหนีไปไหนดี"
    links = nearby(t, assess(t).get("disaster"))
    assert links[0]["url"] == "/safe" and [l["label"] for l in links][1:] == ["สถานีตำรวจ", "ร้านสะดวกซื้อ (มีคน ไฟสว่าง)", "ปั๊มน้ำมัน"]
    t = "someone is following me at night"
    links = nearby(t, assess(t).get("disaster"))
    assert links[0]["url"] == "/safe?lang=en" and links[1]["label"] == "Police station"
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "/^\\/safe(?:\\?lang=en)?$/.test(l.url)" in js            # การ์ดในแชตรับลิงก์ภายในเฉพาะ /safe


def test_safe_map_arrival_reads_hash_only():
    earth = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
    assert "function safeArrive()" in earth and "location.hash" in earth and "safeArrive();" in earth
