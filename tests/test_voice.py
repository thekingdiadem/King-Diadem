"""พูดแทนพิมพ์ + อ่านคำตอบออกเสียง — คนที่เครียด ร้องไห้ หรือเจอภัย อาจพิมพ์ไม่ไหว ต้องพูดกับระบบได้เลย
ต้องซื่อตรงเรื่องเสียง: บอกผู้ใช้ว่าเบราว์เซอร์อาจส่งเสียงไปแปลงที่เซิร์ฟเวอร์ของผู้ผลิต และเปิดไมค์ให้เฉพาะเว็บเราเอง"""
from fastapi.testclient import TestClient

from tests._front import front_page

PAGE = front_page()


def test_microphone_is_allowed_for_our_own_pages_only():
    import app as appmod
    pp = TestClient(appmod.app).get("/").headers["permissions-policy"]
    assert "microphone=(self)" in pp and "camera=()" in pp


def test_mic_button_is_hidden_until_the_browser_supports_it_and_has_no_inline_handler():
    assert '<button type="button" id="mic" class="hide" aria-label="พูดแทนพิมพ์" aria-pressed="false"' in PAGE
    assert "if(SR){ mic.classList.remove('hide');" in PAGE
    assert "window.SpeechRecognition || window.webkitSpeechRecognition" in PAGE


def test_user_is_told_where_their_voice_goes_before_first_use():
    assert "lsGet('kd-mic-told') !== '1'" in PAGE and "บางเบราว์เซอร์ส่งเสียงไปที่เซิร์ฟเวอร์ของผู้ผลิต" in PAGE


def test_each_voice_is_distinct_and_council_is_read_part_by_part():
    i = PAGE.index("var VOICE = {")
    block = PAGE[i:PAGE.index("};", i)]
    import re
    pairs = re.findall(r"(LYLA|VEGA|PATICCA|TITAN|COSMOS|CIVIL): \[([\d.]+), ([\d.]+), (\d)\]", block)
    assert len(pairs) == 6 and len({(p, r) for _, p, r, _ in pairs}) == 6 and len({k for *_, k in pairs}) == 6
    assert "if(p !== 'COUNCIL') return [{ who:" in PAGE and "/^(LYLA|VEGA|PATICCA|TITAN|COSMOS|CIVIL)\\s*" in PAGE


def test_speaking_gets_a_spoken_reply_and_can_be_hung_up():
    assert "if(speakOn || call) speak(e.detail.t, e.detail.p);" in PAGE
    assert "if(listening || call){ stop(); return; }" in PAGE
    assert "function stop(){ call = false; listening = false; if(synth) synth.cancel();" in PAGE
    assert "window.dispatchEvent(new CustomEvent('KD:reply'" in PAGE
