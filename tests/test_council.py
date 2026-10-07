"""สภา 6 เสียง (AI/council_engine) — LYLA · VEGA · PATICCA · TITAN · COSMOS · CIVIL + มติร่วม"""
import pathlib

import pytest

from core.kernel_voice import compose, compose_council
from tests.conftest import FAKE_LLM

MEMBERS = ("LYLA ◈", "VEGA ◆", "PATICCA ☸", "TITAN ▲", "COSMOS ✦", "CIVIL ⬡", "มติสภา")


def test_kernel_council_has_all_voices_and_human_decides():
    r = compose_council("ลังเลว่าจะลาออกไปเปิดร้านกาแฟ หรือทำงานเดิมแล้วขายวันหยุด")
    assert all(m in r for m in MEMBERS) and "คุณเป็นคนตัดสินใจเสมอ" in r
    assert "ทำงานเดิมแล้วขายวันหยุด" in r                          # VEGA เรียงทางเลือกจริง


def test_council_slows_down_risky_offers():
    r = compose_council("มีคนชวนลงทุนการันตี 30% ต่อเดือน อยากรวยเร็ว")
    assert "สัญญาณของการหลอก" in r and "ชะลอ" in r and "ความอยากได้" in r


@pytest.mark.parametrize("text", ["อยากตาย", "กินยาเกินขนาดไป"])
def test_crisis_beats_council(text):
    r = compose(text, voice_mode="council")
    assert "PATICCA" not in r and ("1323" in r or "1669" in r)


def test_run_council_from_button(client):
    d = client.post("/run", json={"input": "ควรย้ายงานไหม", "voice_mode": "council"}).json()
    assert d["persona"] == "COUNCIL" and d["voice_mode"] == "council"
    assert "สภา 6 เสียง" in FAKE_LLM["systems"][-1] and "PATICCA" in FAKE_LLM["systems"][-1]


def test_run_council_from_text(client):
    d = client.post("/run", json={"input": "ขอความเห็นสภาเรื่องย้ายงาน"}).json()
    assert d["persona"] == "COUNCIL"


def test_run_council_crisis_goes_to_crisis(client):
    d = client.post("/run", json={"input": "อยากตาย", "voice_mode": "council"}).json()
    assert d["persona"] != "COUNCIL" and "เจ็บปวดมาก" in FAKE_LLM["systems"][-1]


def test_council_without_ai_uses_kernel(client):
    FAKE_LLM["mode"] = "fail"
    d = client.post("/run", json={"input": "ควรย้ายงานไหม", "voice_mode": "council"}).json()
    assert "TITAN ▲" in d["ai_response"] and "มติสภา" in d["ai_response"]


def test_page_has_council_button():
    page = pathlib.Path(__file__).resolve().parent.parent.joinpath("static", "index.html").read_text(encoding="utf-8")
    assert 'data-p="council"' in page and "function councilFmt" in page and "COUNCIL:['สภา 6 เสียง'" in page


@pytest.mark.parametrize("text", ["กินยาเกินขนาดไป", "น้ำท่วมบ้าน ตอนนี้น้ำถึงเอว", "แฟนตบหน้า"])
def test_run_urgent_skips_council(client, text):
    d = client.post("/run", json={"input": text, "voice_mode": "council"}).json()
    assert d["persona"] == "LYLA" and "สภา 6 เสียง" not in FAKE_LLM["systems"][-1]
