"""หน้า Universe: ฉากหน้าต่างยานมองโลกตอนกลางคืน · ตัวจำลองที่ถามสมองจริง · ตัวเลขโชว์จากการรันจริง"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")


def test_preview_answers_in_users_language_without_ai(client):
    r = client.post("/api/kernel/preview", json={"input": "mẹ tôi không thở được"},
                    headers={"cf-connecting-ip": "10.77.0.1"})
    d = r.json()
    assert r.status_code == 200 and d["risk"] >= 85 and d["lang"] == "vi" and d["choices"] == 3
    assert "Đây là tình huống khẩn cấp" in d["reply"] and "no AI" not in d["reply"]


def test_preview_does_not_spend_quota_or_log(client, monkeypatch):
    import app
    called = []
    monkeypatch.setattr(app, "_charge", lambda *a, **k: called.append(1) or (None, False))
    r = client.post("/api/kernel/preview", json={"input": "อยากเปลี่ยนงาน"}, headers={"cf-connecting-ip": "10.77.0.2"})
    assert r.status_code == 200 and not called


@pytest.mark.parametrize("body,code", [({"input": ""}, 400), ({"input": "x" * 200000}, 413)])
def test_preview_rejects_empty_and_huge(client, body, code):
    assert client.post("/api/kernel/preview", json=body, headers={"cf-connecting-ip": "10.77.0.3"}).status_code == code


def test_preview_is_rate_limited(client):
    h = {"cf-connecting-ip": "10.77.0.9"}
    codes = [client.post("/api/kernel/preview", json={"input": "hi"}, headers=h).status_code for _ in range(25)]
    assert 429 in codes


def test_showcase_numbers_are_real():
    d = json.loads((ROOT / "static" / "showcase.json").read_text(encoding="utf-8"))
    from scripts.build_showcase import languages
    assert [l["code"] for l in d["languages"]] == languages()
    assert d["slips_total"] == 0 and d["messages_total"] == sum(s["messages"] for s in d["suites"]) > 50000


def test_page_has_cockpit_scene_and_safe_rendering():
    assert 'id="cockpit-earth"' in PAGE and "/static/cockpit_earth.js" in PAGE
    js = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
    assert "earth/lights.jpg" in js and "prefers-reduced-motion" in js
    # คำตอบของระบบใส่ด้วย textContent เท่านั้น — กัน XSS จากข้อความที่ผู้ใช้พิมพ์สะท้อนกลับ
    live = PAGE[PAGE.index("function runSimulation(){"):PAGE.index("function tryText")]
    assert "innerHTML=d.reply" not in live.replace(" ", "") and "textContent=d.reply" in live.replace(" ", "")
