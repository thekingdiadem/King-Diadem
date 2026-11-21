"""SEO หลายภาษา — ให้คนทั่วโลกค้นเจอ (core/seo_langs.py)
เดิมหน้าแรกมีชื่อเรื่อง/คำอธิบายแค่ภาษาไทย ภาษาอื่นแปลด้วย JS หลังโหลด เครื่องมือค้นหาเลยเห็นแค่หน้าไทย"""
import re
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import app as A
    return TestClient(A.app)


@pytest.mark.parametrize("lg,word", [("en", "way forward"), ("ja", "道"), ("zh", "出路"), ("ko", "길"),
                                     ("es", "camino"), ("vi", "lối đi")])
def test_each_language_has_its_own_title_and_description(client, lg, word):
    h = client.get(f"/?lang={lg}").text
    assert f'<html lang="{lg}">' in h
    title = re.search(r"<title>([^<]*)</title>", h).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)
    assert word in title + desc
    assert re.search(rf'<link rel="canonical" href="[^"]*/\?lang={lg}">', h)


def test_every_page_lists_all_languages_for_search_engines(client):
    h = client.get("/").text
    assert '<html lang="th">' in h
    for lg in ("th", "en", "ja", "zh", "ko", "es", "vi", "x-default"):
        assert f'hreflang="{lg}"' in h, lg
    assert h.count('<meta property="og:locale:alternate"') == 6


def test_unknown_lang_falls_back_to_thai_and_is_not_injected(client):
    h = client.get('/?lang="><script>alert(1)</script>').text
    assert '<html lang="th">' in h and "alert(1)" not in h


def test_sitemap_lists_every_language_with_hreflang(client):
    x = client.get("/sitemap.xml").text
    assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in x
    for lg in ("en", "ja", "zh", "ko", "es", "vi"):
        assert f"/?lang={lg}</loc>" in x
    assert x.count('hreflang="x-default"') == 7


def test_frontend_opens_in_the_language_from_the_link():
    from pathlib import Path
    js = (Path(__file__).resolve().parent.parent / "static" / "i18n.js").read_text(encoding="utf-8")
    assert "URLSearchParams(location.search).get('lang')" in js


def test_descriptions_speak_about_the_system_and_teachings():
    """เจ้าของโปรเจกต์: ไม่ใส่เรื่องส่วนตัว เน้นระบบ คำสอน และสิ่งที่ทำให้ต่าง โดยไม่เปรียบเทียบกับใคร"""
    from core.seo_langs import META
    for lg, (title, desc, _) in META.items():
        assert "O ≥ 1" in desc and "DriftZero" in desc and "LYLA" in desc, lg
    for word in ("better than", "unlike", "ดีกว่า", "ต่างจาก", "แทนที่จะ"):
        assert all(word not in d for _, d, _ in META.values()), word


def test_site_verification_accepts_a_pasted_whole_meta_tag():
    """เคยวางแท็กทั้งบรรทัดลงใน Render → รหัสกลายเป็น "metanamegoogle-site-verificationcontent…" ยืนยันไม่ผ่าน"""
    import app as A
    code = "nz4_fWcDMapEmRRf89wQz8H9TxbL9eeumkIBJJrEgkE"
    assert A._site_code(f'<meta name="google-site-verification" content="{code}" />') == code
    assert A._site_code(code) == code
    assert A._site_code("") == ""
