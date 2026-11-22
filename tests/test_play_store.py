"""พร้อมส่ง Google Play (docs/PLAY_STORE.md) — ไฟล์ตั้งค่าแอปต้องตรงกับเว็บเสมอ และสิ่งที่ Play บังคับต้องมีจริง"""
import json
import re

from tests._front import front_page

TWA = json.load(open("android/twa-manifest.json", encoding="utf-8"))
WEB = json.load(open("static/manifest.json", encoding="utf-8"))
PRIVACY = open("static/privacy.html", encoding="utf-8").read()
DOC = open("docs/PLAY_STORE.md", encoding="utf-8").read()


def test_app_config_matches_the_web_manifest():
    assert TWA["startUrl"] == "/?src=twa" and TWA["display"] == WEB["display"]   # src=twa = รู้ว่าเปิดจากแอป
    assert TWA["backgroundColor"].lower() == WEB["background_color"].lower()
    assert TWA["themeColor"].lower() == WEB["theme_color"].lower()
    assert TWA["webManifestUrl"].endswith("/static/manifest.json")
    for key in ("iconUrl", "maskableIconUrl"):
        path = re.sub(r"^https://[^/]+", "", TWA[key])
        assert any(i["src"] == path for i in WEB["icons"]), key
    assert TWA["host"] in TWA["fullScopeUrl"] and TWA["host"] in TWA["iconUrl"]


def test_signing_key_never_enters_git():
    ignore = open("android/.gitignore", encoding="utf-8").read()
    assert "*.keystore" in ignore and "*.jks" in ignore
    assert TWA["signingKey"]["path"].endswith(".keystore")


def test_asset_links_follow_render_settings(client, monkeypatch):
    monkeypatch.delenv("TWA_PACKAGE", raising=False)
    assert client.get("/.well-known/assetlinks.json").json() == []
    monkeypatch.setenv("TWA_PACKAGE", TWA["packageId"])
    monkeypatch.setenv("TWA_SHA256", "aa:bb, cc:dd")
    j = client.get("/.well-known/assetlinks.json").json()
    assert j[0]["target"]["package_name"] == TWA["packageId"]
    assert j[0]["target"]["sha256_cert_fingerprints"] == ["AA:BB", "CC:DD"]


def test_play_requirements_exist():
    page = front_page()
    assert "ลบบัญชีของฉัน" in page                                  # ลบบัญชีได้เองในแอป
    assert 'id="delete"' in PRIVACY and "ลบบัญชีได้เองทันที" in PRIVACY  # ลิงก์ลบบัญชีบนเว็บ
    assert "/privacy#delete" in DOC and "Data safety" in DOC


def test_privacy_policy_matches_what_the_flag_button_really_keeps():
    """ปุ่มธงเก็บประโยคที่ผู้ใช้พิมพ์ได้ (เมื่อติ๊กเอง) — นโยบายเดิมบอกว่าไม่เก็บ ซึ่ง Play ตรวจและอาจปฏิเสธแอป"""
    assert "ไม่เก็บข้อความที่คุณพิมพ์ถาม" not in PRIVACY
    assert "แนบประโยคที่ฉันพิมพ์ไปด้วย" in PRIVACY and "90 วัน" in PRIVACY      # คำเดียวกับช่องติ๊กที่ผู้ใช้เห็น
    assert "attach my message" in PRIVACY
    assert "แนบประโยคที่ฉันพิมพ์ไปด้วย" in front_page()


def test_no_buying_inside_the_play_app():
    """ทาง 1 (ใช้เงินน้อยสุด): ในแอปไม่แสดงการซื้อ — Play บังคับ Play Billing และห้ามพาไปจ่ายที่อื่น (anti-steering)"""
    page = front_page()
    assert 'id="card-pay" data-buy' in page and '<div class="dlg-f" data-buy>' in page
    assert "html.in-app [data-buy]{display:none!important}" in page
    assert "sessionStorage.setItem('kd-in-app', '1')" in page and "localStorage.setItem('kd-in-app'" not in page
    note = re.search(r'data-app-only>([^<]+)<', page).group(1)
    assert "20 ข้อความ" in note and "เว็บ" not in note and "Stripe" not in note   # ไม่ชี้ไปจ่ายที่อื่น
    wallet = open("static/wallet.html", encoding="utf-8").read()
    assert "sessionStorage.getItem('kd-in-app') === '1'" in wallet
