"""ทางด่วนของเรื่องวิกฤตและภัยตอนนี้ — ไม่รอ AI (app.py · fast_path)

CTO ที่ทำระบบแบบเดียวกันเตือนใต้โพสต์ LinkedIn ว่าเวลาตอบของ LLM ที่แกว่ง (p99) ทำลายความนิ่งที่คนในวิกฤตต้องการ
วัดแล้ว: เดิม "อยากตาย" "ผัวตีฉัน" รอ AI เหมือนข้อความทั่วไป นานสุด 45 วินาที
สมการของระบบตอบเรื่องเดียวกันได้ใน 1–25 มิลลิวินาที พร้อมเบอร์ที่ตรวจสอบได้ และได้คำตอบเดิมทุกครั้ง
"""
import time
import uuid

import pytest

import core.llm_gemini as L
from tests.conftest import FAKE_LLM

URGENT = ["อยากตาย", "ผัวตีฉัน", "i want to die", "เขาอยู่หน้าบ้าน ฉันกลัว", "彼が家の前にいる、怖い", "我想死", "죽고 싶어",
          "quiero morir", "tôi muốn chết", "กินยาไป 30 เม็ด", "jk but sometimes i wish i wouldn't wake up"]
EVERYDAY = ["วันนี้อากาศดี", "ช่วยวางแผนเที่ยวเชียงใหม่", "how do I ask for a raise", "อยากเปิดร้านกาแฟ"]


@pytest.fixture
def fast(monkeypatch):
    monkeypatch.setenv("KD_FAST_PATH", "1")
    monkeypatch.delenv("KD_AI", raising=False)


@pytest.fixture
def slow_ai(monkeypatch):
    orig = L.GeminiLLM._call

    def slow(self, *a, **k):
        time.sleep(2)
        return orig(self, *a, **k)
    monkeypatch.setattr(L.GeminiLLM, "_call", slow)


def _run(client, text, hist=None):
    ip = "10.33.%d.%d" % tuple(uuid.uuid4().bytes[:2])
    t = time.perf_counter()
    r = client.post("/run", json={"input": text, "history": hist or []}, headers={"cf-connecting-ip": ip}).json()
    return r, time.perf_counter() - t


@pytest.mark.parametrize("text", URGENT)
def test_crisis_and_danger_do_not_wait_for_the_ai(client, fast, slow_ai, text):
    r, sec = _run(client, text)
    assert r["fast_path"] is True and r["answer_source"] == "kernel"
    assert FAKE_LLM["calls"] == 0
    assert sec < 1.5, sec                                  # AI ช้า 2 วินาที — ต้องไม่รอ
    assert any(n in r["ai_response"] for n in ("1323", "1669", "191", "110", "119", "112", "911", "109", "findahelpline"))


@pytest.mark.parametrize("text", EVERYDAY)
def test_everyday_messages_still_get_the_ai(client, fast, text):
    r, _ = _run(client, text)
    assert not r.get("fast_path") and r["answer_source"] == "llm"


@pytest.mark.parametrize("first,reply", [("ดิ่งมากเลยวันนี้ ไม่อยากทำอะไร", "ก็มีบ้าง"),
                                         ("มีคนโทรมาอ้างเป็นตำรวจ บอกให้ถอนเงินไปซื้อทอง แล้วจะส่งเจ้าหน้าที่มารับที่บ้าน", "เขามาถึงหน้าบ้านแล้ว")])
def test_short_reply_that_turns_serious_takes_the_fast_path(client, fast, first, reply):
    r, _ = _run(client, reply, [{"role": "user", "content": first}, {"role": "assistant", "content": "..."}])
    assert r["fast_path"] is True


def test_same_crisis_message_gets_the_same_answer_every_time(client, fast):
    a, _ = _run(client, "อยากตาย")
    b, _ = _run(client, "อยากตาย")
    assert a["ai_response"] == b["ai_response"]


def test_fast_path_can_be_switched_off(client, monkeypatch):
    monkeypatch.setenv("KD_FAST_PATH", "0")
    r, _ = _run(client, "อยากตาย")
    assert not r.get("fast_path") and FAKE_LLM["calls"] == 1
