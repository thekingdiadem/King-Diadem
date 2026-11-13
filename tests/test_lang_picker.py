"""ตัวเลือก 54 ภาษา (static/i18n.js) — ปุ่มเดียว · ค้นหาได้ทั้งชื่อภาษาเอง ชื่ออังกฤษ ชื่อไทย · พูดชื่อภาษาผ่านไมค์ได้
เดิมเป็นกล่องเลือก 7 ภาษาที่เจ้าของโปรเจกต์ว่ารก ขณะที่แชทตอบได้ 54 ภาษา"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "static" / "i18n.js").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


def _obj(name):
    body = re.search(r"var " + name + r" = (\{.*?\});", JS).group(1)
    if name == "NAMES":                                  # คีย์ไม่มีเครื่องหมายคำพูด (th: [...]) — อ่านเฉพาะรหัสภาษา
        return {k: None for k in re.findall(r"(?:\{|, )(\w+): \[", body)}
    return json.loads(body)


def test_picker_lists_every_language_the_chat_can_answer():
    import sys
    sys.path.insert(0, str(ROOT))
    from core.asia_replies import REPLY
    from core.world_replies import GENERAL_ASIA, WORLD_REPLY
    chat = set(WORLD_REPLY) | set(REPLY) | set(GENERAL_ASIA) | {"th", "en", "ja", "zh", "ko", "es", "vi"}
    names = _obj("NAMES")
    assert set(names) == chat and len(names) == 54


def test_every_language_has_a_thai_name_for_search_and_voice():
    assert set(_obj("TH_NAME")) == set(_obj("NAMES"))
    assert _obj("TH_NAME")["ja"] == "ญี่ปุ่น"


def test_one_small_button_instead_of_a_long_select():
    assert '<select id="lang-pick"' not in PAGE and '<button type="button" id="lang-pick"' in PAGE


def test_device_language_aliases_map_to_our_codes():
    alias = re.search(r"var ALIAS = (\{.*?\});", JS).group(1)
    for a in ("nb: 'no'", "fil: 'tl'", "hr: 'sh'", "iw: 'he'"):
        assert a in alias


def test_mic_only_when_the_browser_supports_it_and_tells_about_audio():
    assert "window.SpeechRecognition || window.webkitSpeechRecognition" in JS and "if (SR) {" in JS
    assert "ผู้ผลิตเบราว์เซอร์" in JS
