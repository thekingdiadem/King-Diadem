"""VEGA Human DriftZero Kernel (14 Gates) — ตามเอกสารของเจ้าของโปรเจกต์

ก่อนหน้านี้ 14 kernel มีแค่ในเอกสาร (KERNEL/*.md) ไม่มีโค้ดตรวจจริง — ตอนนี้ตรวจจากข้อความแบบดีเทอร์มินิสติก
แล้ว VEGA ถามคำถามของประตูที่ติด (มี AI: แนบเป็นบริบท · ไม่มี AI: แทรกในคำตอบ) และแสดงในรายละเอียดคำตอบ
"""
import pytest

from core.vega_kernels import KERNELS, evaluate, llm_hint, offline_lines


def test_all_fourteen_kernels_exist_with_rule_and_question():
    assert [k[0] for k in KERNELS] == [f"K{i}" for i in range(1, 15)]
    for kid, name, enemy, rule, ask, _ in KERNELS:
        assert name and enemy and rule and ask.strip(), kid


@pytest.mark.parametrize("text,gate", [
    ("ช่างมันเถอะ เดี๋ยวก็ดีเอง ไม่กล้าเปิดดูยอดหนี้", "K1"),
    ("จะเอาเงินเก็บทั้งหมดไปลงคริปโต ผลตอบแทนสูง", "K2"),
    ("ไม่รู้จะเริ่มตรงไหน ซับซ้อนมาก", "K3"),
    ("ตกงานอยู่ แต่อยากลงทุนเปิดร้านเพิ่ม", "K4"),
    ("กำลังจะเซ็นสัญญาค้ำประกันให้เพื่อน", "K5"),
    ("โดนด่าทุกวัน ชินแล้ว เป็นแบบนี้มาตลอด", "K6"),
    ("โมโหมาก จะส่งข้อความด่าคืนนี้เลย", "K7"),
    ("เครียดมาก ร้องไห้ทั้งคืน", "K8"),
    ("กำไรร้านจะเก็บไว้คนเดียว ไม่แบ่งใคร", "K9"),
    ("คิดจะเอาเงินบริษัทไปใช้ส่วนตัวก่อน", "K10"),
    ("อยู่เฉยไม่ได้ ต้องทำอะไรสักอย่าง", "K11"),
    ("มั่นใจ 100 ว่าหุ้นตัวนี้ขึ้น ไม่มีทางผิด", "K12"),
    ("โดนหลอกโอนไปแล้ว เขาให้โอนเพิ่มอีก", "K13"),
    ("ต้องเอาชนะให้ได้ อยากแก้แค้น", "K14"),
])
def test_each_gate_fires_on_its_enemy(text, gate):
    assert gate in [g["id"] for g in evaluate(text, limit=14)]


@pytest.mark.parametrize("text", ["วันนี้อากาศดี", "สวัสดีค่ะ", "ขอสูตรแกงเขียวหวาน", "เงินเดือน 30,000 วางแผนเก็บเงินยังไงดี"])
def test_calm_messages_trigger_nothing(text):
    assert evaluate(text) == []


def test_priority_and_limit():
    g = evaluate("โดนหลอกโอนไปแล้ว โมโหมาก อยากแก้แค้นให้มันรู้ เอาเงินเก็บทั้งหมดไปทวงคืน")
    assert len(g) <= 3 and g[0]["id"] == "K13"            # ความเสียหายที่กำลังเคลื่อนมาก่อน


def test_deterministic():
    t = "จะลาออกคืนนี้เลย โกรธหัวหน้ามาก"
    assert evaluate(t) == evaluate(t)


def test_hint_and_offline_text():
    g = evaluate("กำลังจะเซ็นสัญญาค้ำประกันให้เพื่อน")
    assert "[VEGA 14 GATES" in llm_hint(g) and "K5" in llm_hint(g)
    assert "K5 ·" in offline_lines(g) and llm_hint([]) == "" and offline_lines([]) == ""


def test_run_with_vega_returns_gates_and_asks_offline(client, app_module, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": "กำลังจะเซ็นสัญญาค้ำประกันให้เพื่อน ทำดีไหม", "persona_ui": "VEGA", "voice_mode": "vega"}).json()
    assert [g["id"] for g in d.get("vega_gates", [])][:1] == ["K5"]
    if d.get("answer_source") == "kernel":
        assert "ถ้าทางนี้ไม่เวิร์ก" in d["ai_response"]
        assert d["ai_response"].rstrip().splitlines()[-1].startswith("— VEGA") or "— VEGA" in d["ai_response"]


def test_lyla_and_crisis_do_not_get_gates(client):
    d = client.post("/run", json={"input": "กำลังจะเซ็นสัญญาค้ำประกันให้เพื่อน", "persona_ui": "LYLA", "voice_mode": "lyla"}).json()
    assert "vega_gates" not in d
    d = client.post("/run", json={"input": "อยากตาย โมโหมาก จะลาออกคืนนี้เลย", "persona_ui": "VEGA", "voice_mode": "vega"}).json()
    assert "vega_gates" not in d


def test_vega_prompt_and_ui_know_the_gates():
    from pathlib import Path
    import core.llm_gemini as L
    assert "K13 Stop-the-Line" in L.VEGA_SYSTEM and "Human SOP" in L.VEGA_SYSTEM
    html = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")
    assert "row('VEGA gates'" in html


# ── รอบไล่หาบั๊ก: ภาษา · เรื่องวิกฤตตอนเลือกเส้นทาง VEGA · คำอังกฤษที่ซ้อนกัน ──────────

def test_english_offline_reply_gets_english_gate_questions(client, monkeypatch):
    """เดิมผู้ใช้ภาษาอังกฤษได้คำตอบอังกฤษ แล้วตามด้วย "ก่อนตัดสินใจ ลองตอบตัวเองก่อนครับ" ภาษาไทย"""
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": "I'm about to co-sign a loan for my friend, should I?",
                                  "persona_ui": "VEGA", "voice_mode": "vega"}).json()
    assert [g["id"] for g in d.get("vega_gates", [])][:1] == ["K5"]
    assert "step back out" in d["vega_gates"][0]["ask"]
    if d.get("answer_source") == "kernel":
        assert "Before you decide" in d["ai_response"]
        assert "ก่อนตัดสินใจ" not in d["ai_response"] and "ถ้าทางนี้ไม่เวิร์ก" not in d["ai_response"]


@pytest.mark.parametrize("text", ["อยากตาย จะลาออกคืนนี้เลย", "I want to die. I'll quit my job tonight",
                                  "I took 30 pills, should I quit my job", "พ่อตีหัวผม จะลาออกคืนนี้เลย"])
def test_crisis_on_vega_route_gets_no_gate_questions(client, monkeypatch, text):
    """ผู้ใช้ที่เลือกเส้นทาง VEGA ไว้ (route ไม่ถูกยกระดับ) เคยได้สายด่วน 1323 แล้วตามด้วย
    "รอ 24 ชั่วโมงก่อนตัดสินใจได้ไหม" — เรื่องวิกฤตต้องให้ทางช่วยก่อน ไม่ใช่ถามให้คิด"""
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": text, "route": "vega", "persona_ui": "VEGA", "voice_mode": "vega"}).json()
    assert "vega_gates" not in d
    assert "ลองตอบตัวเองก่อน" not in d["ai_response"] and "Before you decide" not in d["ai_response"]


def test_crisis_gates_not_in_llm_prompt(client):
    from tests.conftest import FAKE_LLM
    client.post("/run", json={"input": "อยากตาย จะลาออกคืนนี้เลย", "route": "vega", "persona_ui": "VEGA", "voice_mode": "vega"})
    assert not any("VEGA 14 GATES" in p for p in FAKE_LLM["prompts"])


@pytest.mark.parametrize("text", ["small investment idea for my shop", "box2 for sale", "how to install the app"])
def test_english_words_that_only_contain_all_in_or_x2_do_not_fire(text):
    assert evaluate(text) == []


@pytest.mark.parametrize("text", ["จะall inเลย", "going all-in on crypto", "ได้กำไร x3 แน่นอน"])
def test_real_all_in_still_fires_k2(text):
    assert "K2" in [g["id"] for g in evaluate(text)]


def test_offline_lines_english():
    g = evaluate("I'm about to co-sign a loan", lang="en")
    out = offline_lines(g, lang="en")
    assert out.startswith("Before you decide") and "K5 ·" in out and "ครับ" not in out
