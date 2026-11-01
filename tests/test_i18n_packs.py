"""หน้าเว็บ 6 ภาษา: ไทย อังกฤษ ญี่ปุ่น + จีน เกาหลี สเปน (static/i18n/<lang>.js โหลดเฉพาะตอนเลือก)
เจ้าของโปรเจกต์: หน้าเว็บขึ้นว่า "54 ภาษา" แต่เมนูมีแค่ 3 ภาษา — เพิ่มให้ตรงกับ 6 ภาษาที่ระบบตอบได้เต็มตอนไม่มี AI"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = (ROOT / "static" / "i18n.js").read_text(encoding="utf-8")
KEYS = re.findall(r"'([^']*[ก-๙][^']*)':\s*\[", I18N)


def _pack(lang):
    src = (ROOT / "static" / "i18n" / f"{lang}.js").read_text(encoding="utf-8")
    return json.loads(src[src.index("= {") + 2: src.rindex("}") + 1])


@pytest.mark.parametrize("lang", ["zh", "ko", "es"])
def test_pack_covers_every_page_text(lang):
    p = _pack(lang)
    missing = [k for k in KEYS if k not in p]
    assert not missing, missing[:10]
    th = re.compile(r"[\u0E01-\u0E3A\u0E40-\u0E5B]")                      # ไทย (ยกเว้น ฿ สัญลักษณ์เงินบาท)
    assert not [k for k, v in p.items() if th.search(v)]                      # ไม่มีไทยหลงในคำแปล


@pytest.mark.parametrize("lang", ["zh", "ko", "es"])
def test_placeholders_and_markup_survive(lang):
    en = dict(re.findall(r"'([^']*[ก-๙][^']*)':\s*\['([^']*)'", I18N))
    ph = lambda s: sorted(re.findall(r"\{\w+\}|<[^>]+>", s))
    bad = [k for k, v in _pack(lang).items() if k in en and ph(v) != ph(en[k])]
    assert not bad, bad[:5]


def test_runtime_lazy_loads_packs_and_picker_lists_six():
    assert "var LANGS = ['th', 'en', 'ja', 'zh', 'ko', 'es']" in I18N
    assert "'i18n/' + lang + '.js'" in I18N and "(PACK[lang] && PACK[lang][th]) || D[th][0]" in I18N   # ขาดคำแปล → อังกฤษ
    page = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    for v, name in (("zh", "中文"), ("ko", "한국어"), ("es", "Español")):
        assert f'<option value="{v}">{name}</option>' in page
