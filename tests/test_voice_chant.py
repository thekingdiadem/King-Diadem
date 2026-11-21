"""อ่านออกเสียงแบบทำนองสรภัญญะ (กาพย์ยานี ๑๑) — แบ่งวรรค 5/6 พยางค์ เอื้อนสั้นท้ายบาท เรื่องด่วนอ่านเรียบ"""
import json, subprocess

APP = open("static/app.js", encoding="utf-8").read()


def _run(js):
    i, j = APP.index("function sylls"), APP.index("function chantable")
    code = "global.window=global;" + APP[i:j] + js
    return subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout


def test_lines_alternate_front_and_back_like_yani_11():
    out = json.loads(_run("console.log(JSON.stringify(chantLines('ผลเลือดของคุณบอกว่าไตทำงานลดลงแต่ยังชะลอได้')))"))
    assert out[0]["back"] is False and out[1]["back"] is True
    assert "".join(x["t"] for x in out) == "ผลเลือดของคุณบอกว่าไตทำงานลดลงแต่ยังชะลอได้"


def test_short_leftover_word_is_not_its_own_line():
    out = json.loads(_run("console.log(JSON.stringify(chantLines('ผลเลือดของคุณบอกว่าไตทำงานลดลงแต่ยังชะลอได้ถ้าคุมความดันและลดเค็ม')))"))
    assert out[-1]["t"] != "เค็ม"


def test_urgent_and_crisis_are_read_plainly():
    assert "x.who !== 'CRISIS'" in APP and "1669|1323|191" in APP
    assert "rate * .78" in APP              # เอื้อนสั้นท้ายบาท
    assert "contextmenu" in APP and "kd-chant" in APP


def test_drawn_out_ending_is_a_whole_word_not_half_a_syllable():
    out = json.loads(_run("console.log(JSON.stringify(chantLines('ถ้าคุมความดันและลดเค็มได้')))"))
    assert all(x["t"].endswith(x["last"]) for x in out)
    assert "w.length - 3" not in APP
