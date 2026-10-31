"""หน้า Universe: ฉากหน้าต่างยานมองโลกตอนกลางคืน · ตัวจำลองที่ถามสมองจริง · ตัวเลขโชว์จากการรันจริง"""
import json
from pathlib import Path

import pytest
from tests._front import front_page  # noqa: E402

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
    assert "'lights.jpg'" in js and "lights_4k.jpg" in js and "prefers-reduced-motion" in js
    assert "bunny" not in PAGE and "sathud" not in PAGE                 # เจ้าของขอโลกสวยแบบของจริง ไม่เติมอะไรทับภาพ
    # คำตอบของระบบใส่ด้วย textContent เท่านั้น — กัน XSS จากข้อความที่ผู้ใช้พิมพ์สะท้อนกลับ
    live = PAGE[PAGE.index("function runSimulation(){"):PAGE.index("function tryText")]
    assert "innerHTML=d.reply" not in live.replace(" ", "") and "textContent=d.reply" in live.replace(" ", "")


def test_capitals_cover_every_country_with_real_coordinates():
    d = json.loads((ROOT / "static" / "earth" / "capitals.json").read_text(encoding="utf-8"))
    caps = {c[0]: c for c in d["capitals"]}
    assert len(d["capitals"]) >= 240
    bkk = caps["Bangkok"]
    assert abs(bkk[2] - 13.75) < .05 and abs(bkk[3] - 100.5) < .05
    assert "Nay Pyi Taw" in caps and "Washington, D.C." in caps and "Phnom Penh" in caps


def test_city_tiers_load_lazily_and_stay_light():
    js = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
    for f in ("capitals.json", "cities_t2.json", "cities_t3.json", "cities_t4.json", "cities_t5.json"):
        assert f in js and (ROOT / "static" / "earth" / f).exists()
    total = sum((ROOT / "static" / "earth" / f"cities_t{i}.json").stat().st_size for i in range(2, 6))
    assert total < 1_600_000                                           # ราว 49,000 เมือง — โหลดเฉพาะตอนซูมถึงชั้นนั้น
    assert "if (show <= 0) return;" in js                              # มองทั้งโลกไม่วาดชื่อเมืองเลย


def test_4k_textures_exist_and_are_optional():
    js = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
    assert "MAX_TEXTURE_SIZE" in js and "saveData" in js
    for f in ("lights_4k.jpg", "day_4k.jpg", "clouds_4k.jpg", "water.png"):
        assert (ROOT / "static" / "earth" / f).exists()


def test_calm_mode_stops_scroll_spin_and_is_remembered():
    sky = (ROOT / "static" / "universe_sky.js").read_text(encoding="utf-8")
    assert "kd-calm" in sky and "(calm ? 0 : sc * Math.PI * 2 * .92)" in sky   # ฟ้าไม่หมุนตามการเลื่อนจอ
    assert "localStorage.getItem('kd-calm')" in PAGE and 'id="ec-calm"' in PAGE
    assert "html.kd-calm *" in PAGE


def test_language_list_is_folded_away():
    assert '<details class="lang-more">' in PAGE


def test_suggestion_buttons_bind_to_real_class():
    """index.html เคยผูกปุ่มคำแนะนำกับ #sugg ซึ่งไม่มีในหน้า (ใช้ class .sugg) — ปุ่มที่เพิ่มทีหลังจะกดไม่ติด"""
    idx = front_page()
    assert "$$('#sugg button')" not in idx and "$$('.sugg button')" in idx


def test_phone_does_not_download_4k_until_zoom():
    """มือถือเคยโหลดภาพ 4K ทั้งสามภาพ (~2.6 MB) ทันทีที่เปิดหน้า แม้ไม่ได้ซูม"""
    js = open("static/cockpit_earth.js", encoding="utf-8").read()
    assert "light && S.tL < 2" in js and "maybe4k();" in js           # tL ≥ 2 = ซูมลงใกล้กว่าวงโคจร 2 เท่า
    assert js.count("load(0, 'lights_4k.jpg')") == 1      # โหลดได้ที่เดียว ผ่าน maybe4k
