"""เตรียมเปิดตัว (เว็บ + แอป Android แบบ TWA)
เดิมไม่มีหน้าคืนเงินและหน้าติดต่อแยก (Stripe/Play Store ต้องมี) · ไม่มีปุ่มติดตั้งแอป คนไม่รู้ว่าติดตั้งได้
· manifest ไม่มีภาพตัวอย่าง (หน้าต่างติดตั้งบน Android เลยเป็นแบบเรียบ) · ยังผูกแอป TWA กับโดเมนไม่ได้"""
import json
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("path,title", [("/refund", "การยกเลิกและคืนเงิน"), ("/support", "ช่วยเหลือและติดต่อ")])
def test_refund_and_support_pages_show_contact(client, app_module, path, title):
    r = client.get(path)
    assert r.status_code == 200 and title in r.text
    assert f"mailto:{app_module.SUPPORT_EMAIL}" in r.text and app_module.OPERATOR_NAME in r.text
    assert "{{" not in r.text


def test_refund_page_matches_the_terms():
    """หน้าคืนเงินต้องไม่สัญญาเกินข้อกำหนด ข้อ 5"""
    t = (ROOT / "static" / "refund.html").read_text(encoding="utf-8")
    for must in ("คืนเครดิตให้ทันที", "ยกเลิกแพ็กเกจได้ทุกเมื่อ", "ไม่คืนเป็นเงิน", "Stripe", "/wallet"):
        assert must in t, must
    assert "ห้ามส่งรหัสผ่าน" in t


def test_support_page_has_hotlines_and_never_asks_for_secrets():
    t = (ROOT / "static" / "support.html").read_text(encoding="utf-8")
    for n in ("1669", "191", "1323", "1441"):
        assert f'href="tel:{n}"' in t
    assert "ไม่ขอ" in t and "never ask" in t


def test_pages_link_to_each_other_and_from_the_app():
    from tests._front import front_page
    assert 'href="/support"' in front_page()
    w = (ROOT / "static" / "wallet.html").read_text(encoding="utf-8")
    assert 'href="/refund"' in w
    for f in ("terms", "privacy", "refund", "support"):
        s = (ROOT / "static" / f"{f}.html").read_text(encoding="utf-8")
        assert 'href="/refund"' in s and 'href="/support"' in s, f


def test_install_button_waits_for_the_browser_and_hides_when_installed():
    from tests._front import front_page
    page = front_page()
    assert 'id="pwa-install"' in page and "onclick" not in page.split('id="pwa-install"')[0][-80:]
    assert "beforeinstallprompt" in page and "(display-mode: standalone)" in page and "appinstalled" in page


def test_manifest_has_real_screenshots():
    m = json.loads((ROOT / "static" / "manifest.json").read_text(encoding="utf-8"))
    forms = {s["form_factor"] for s in m["screenshots"]}
    assert forms == {"narrow", "wide"}
    for s in m["screenshots"]:
        f = ROOT / s["src"].lstrip("/")
        w, h = Image.open(f).size
        assert f"{w}x{h}" == s["sizes"] and f.stat().st_size < 400_000


def test_assetlinks_empty_until_configured(client, monkeypatch):
    monkeypatch.delenv("TWA_PACKAGE", raising=False)
    monkeypatch.delenv("TWA_SHA256", raising=False)
    assert client.get("/.well-known/assetlinks.json").json() == []


def test_assetlinks_from_render_env(client, monkeypatch):
    monkeypatch.setenv("TWA_PACKAGE", "com.kingdiadem.app")
    monkeypatch.setenv("TWA_SHA256", "aa:bb , CC:DD")
    d = client.get("/.well-known/assetlinks.json").json()
    assert d[0]["target"] == {"namespace": "android_app", "package_name": "com.kingdiadem.app",
                              "sha256_cert_fingerprints": ["AA:BB", "CC:DD"]}
    assert d[0]["relation"] == ["delegate_permission/common.handle_all_urls"]
