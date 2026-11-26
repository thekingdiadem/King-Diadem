"""การ์ดวิเคราะห์ภาพต้องเตือนก่อนอัปโหลดว่าภาพถูกส่งให้ AI ทั้งภาพ (ครบ 7 ภาษา)"""
import re
from pathlib import Path

from tests._front import front_page

ROOT = Path(__file__).resolve().parent.parent
WARN = "⚠ ภาพจะถูกส่งให้ AI ทั้งภาพ · อย่าถ่ายเลขบัญชี บัตรประชาชน บัตรเครดิต หรือรหัสผ่านติดมา"


def test_warning_sits_in_image_card_before_run_button():
    page = front_page()
    card = page[page.index('id="card-img"'):page.index('id="card-pay"')]
    assert 'id="img-warn"' in card and WARN in card
    assert card.index('id="img-warn"') < card.index('id="img-run"')


def test_warning_translated_in_all_languages():
    main = (ROOT / "static/i18n.js").read_text(encoding="utf-8")
    m = re.search(re.escape("'" + WARN + "'") + r":\s*\['([^']+)',\s*'([^']+)'\]", main)
    assert m and "AI" in m.group(1) and m.group(2)
    for lang in ("es", "ko", "vi", "zh"):
        pack = (ROOT / f"static/i18n/{lang}.js").read_text(encoding="utf-8")
        assert re.search(re.escape('"' + WARN + '"') + r':\s*"[^"]+"', pack), lang
