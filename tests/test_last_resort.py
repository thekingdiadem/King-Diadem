"""ชั้นสุดท้ายเมื่อทุกอย่างพัง (core/last_resort.py) — บทเรียนจาก Microsoft ล่มทั่วโลก 12–13 พ.ย. 2569

เหตุของการล่มครั้งนั้น: การตั้งค่าที่เปลี่ยนหลังอัปเดต · ไม่มีอะไรจับได้ก่อนผู้ใช้เจอ · กู้แล้วล่มซ้ำ
ทดลองเหตุเดียวกันกับระบบเรา: ตัวประเมินและสมการพังหลังอัปเดต + AI ล่มพร้อมกัน → "อยากตาย" ได้ error 500 ไม่มีเบอร์
"""
import re
from pathlib import Path

import pytest

import app as A
from core.last_resort import LINES, canary, lang, reply
from tests.conftest import FAKE_LLM

NUM = re.compile(r"1669|191|1323|119|112|911|115")


@pytest.fixture
def broken(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("bad config after update")
    monkeypatch.setattr(A, "kernel_assess", boom)
    monkeypatch.setattr(A, "kernel_compose", boom)
    FAKE_LLM.update(mode="fail")


@pytest.mark.parametrize("text,lg", [("อยากตาย", "th"), ("i want to die", "en"), ("死にたい", "ja"), ("我想死", "zh"),
                                     ("죽고 싶어", "ko"), ("quiero morir", "es"), ("tôi muốn chết", "vi")])
def test_when_everything_breaks_the_user_still_gets_emergency_numbers(client, broken, text, lg):
    r = client.post("/run", json={"input": text, "history": []})
    assert r.status_code == 200
    d = r.json()
    assert d["answer_source"] == "last_resort" and d["ai_response"] == LINES[lg]
    assert NUM.search(d["ai_response"])


def test_last_resort_imports_nothing_from_the_system():
    src = Path(__file__).resolve().parent.parent.joinpath("core", "last_resort.py").read_text(encoding="utf-8")
    top = [ln for ln in src.splitlines() if ln.startswith(("import ", "from "))]
    assert top == ["import re"]                         # ไม่พึ่งโมดูลที่อาจพังพร้อมกัน


def test_every_language_has_numbers_and_detection_is_simple():
    assert all(NUM.search(t) for t in LINES.values())
    assert lang("") == "th" and lang("hello") == "en" and reply("??") == LINES["th"]


def test_canary_checks_crisis_replies_in_seven_languages():
    c = canary()
    assert c == {"ok": True, "failed": []}


def test_canary_is_visible_at_health(client):
    assert client.get("/health").json()["crisis_canary"]["ok"] is True


def test_canary_notices_when_the_kernel_stops_giving_numbers(monkeypatch):
    import core.kernel_voice as KV
    monkeypatch.setattr(KV, "compose", lambda t, *a, **k: "ok")
    assert canary()["ok"] is False


def test_front_end_error_message_carries_the_hotlines():
    js = Path(__file__).resolve().parent.parent.joinpath("static", "app.js").read_text(encoding="utf-8")
    assert "ถ้าเป็นเรื่องด่วน โทรได้เลยไม่ต้องรอ: 1669" in js
