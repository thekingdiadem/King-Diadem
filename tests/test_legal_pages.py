"""นโยบายความเป็นส่วนตัว + ข้อกำหนดการใช้งาน — PDPA ต้องบอกว่าใครดูแลข้อมูลและติดต่อทางไหน · Play Store ต้องมีลิงก์นโยบาย
เดิมเว็บไม่มีสองหน้านี้เลย ผู้ใช้ไม่รู้ว่าข้อความถูกส่งให้ AI ภายนอก หรือจะขอลบข้อมูลได้ที่ไหน"""
import pytest


@pytest.mark.parametrize("path,title", [("/privacy", "นโยบายความเป็นส่วนตัว"), ("/terms", "ข้อกำหนดการใช้งาน")])
def test_pages_show_operator_and_contact(client, app_module, path, title):
    r = client.get(path)
    assert r.status_code == 200 and title in r.text
    assert app_module.OPERATOR_NAME in r.text and app_module.SUPPORT_EMAIL in r.text
    assert f'mailto:{app_module.SUPPORT_EMAIL}' in r.text
    assert "{{" not in r.text                                   # ไม่มีช่องว่างที่ลืมเติม


def test_contact_can_change_without_code(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "SUPPORT_EMAIL", "support@example.com")
    monkeypatch.setattr(app_module, "OPERATOR_NAME", "<b>x</b>")
    t = client.get("/privacy").text
    assert "support@example.com" in t and "<b>x</b>" not in t and "&lt;b&gt;x&lt;/b&gt;" in t


def test_privacy_names_what_actually_leaves_the_system(client):
    t = client.get("/privacy").text
    for must in ("Gemini", "Stripe", "Turso", "Render", "ไม่ขายข้อมูล", "30 วัน", "สคส.", "90 วัน"):
        assert must in t, must


def test_terms_put_the_human_in_charge_and_list_hotlines(client):
    t = client.get("/terms").text
    for must in ("คุณเป็นคนตัดสินใจเสมอ", "1669", "1323", "1441", "กฎหมายไทย"):
        assert must in t, must


def test_links_are_where_people_sign_up():
    from tests._front import front_page
    page = front_page()
    assert 'href="/privacy"' in page and 'href="/terms"' in page
    for f in ("static/register.html", "static/login.html"):
        s = open(f, encoding="utf-8").read()
        assert 'href="/terms"' in s and 'href="/privacy"' in s, f
