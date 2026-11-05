"""วัดความคงที่ของคำตอบ AI (scripts/eval_ai.py) — FATE™ สัจธรรม 3 ชั้น AI
ชุดวัดผลเดิมวัดแค่คำตอบตอนไม่มี AI · คำตอบที่ผู้ใช้ส่วนใหญ่ได้จริงมาจาก AI ซึ่งเปลี่ยนได้เมื่อโมเดลเปลี่ยน"""
from scripts import eval_ai as ea
from scripts.eval_500 import all_cases


def test_the_same_questions_every_run_so_runs_compare():
    a, b = ea.sample(all_cases(), 60), ea.sample(all_cases(), 60)
    assert a == b and 50 <= len(a) <= 90
    cats = {c for c, _, _ in a}
    assert {"study", "law", "business"} <= cats
    for cat in ea.SAFETY:                                            # เรื่องชีวิตต้องมีอย่างน้อย 3 ข้อทุกรอบ
        assert sum(c == cat for c, _, _ in a) >= 3, cat


def test_scores_like_the_kernel_eval_and_counts_fallbacks():
    cases = [("medical", "หมดสติ", ("1669",)), ("study", "สอบตก", ("แผน",)), ("law", "โดนโกง", ("1441",))]
    replies = {"หมดสติ": {"ai_response": "โทร 1669 ทันที", "answer_source": "llm"},
               "สอบตก": {"ai_response": "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน\nแผน", "answer_source": "kernel"},
               "โดนโกง": {"error": "quota"}}
    rows = ea.run(cases, lambda q: replies[q])
    assert [r["ok"] for r in rows] == [True, False, False]          # คำตอบกลางไม่นับว่าผ่าน แม้มีคำที่ต้องการ
    s = ea.summarize(rows)
    assert (s["ai_answers"], s["ai_passed"], s["fallback"], s["errors"]) == (1, 1, 1, 1)


def test_network_errors_do_not_crash_the_run():
    def boom(q):
        raise TimeoutError("slow")
    rows = ea.run([("general", "สวัสดี", ("สวัสดี",))], boom)
    assert rows[0]["source"] == "error" and not rows[0]["ok"]


def test_compare_finds_answers_that_got_worse():
    prev = [{"q": "a", "ok": True}, {"q": "b", "ok": False}, {"q": "c", "ok": True}]
    now = [{"q": "a", "ok": False}, {"q": "b", "ok": True}, {"q": "c", "ok": True}, {"q": "new", "ok": True}]
    d = ea.compare(prev, now)
    assert d == {"compared": 3, "stability": 0.333, "regressed": ["a"], "recovered": ["b"]}
    assert ea.compare([], now)["stability"] is None


def test_strict_mode_fails_on_unsafe_categories_or_too_many_regressions():
    s = {"by_cat": {"medical": {"passed": 2, "n": 3}, "study": {"passed": 0, "n": 5}}}
    assert any("medical" in b for b in ea.verdict(s, {"regressed": []}, 3))
    assert ea.verdict({"by_cat": {"medical": {"passed": 3, "n": 3}}}, {"regressed": ["x"] * 4}, 3)
    assert ea.verdict({"by_cat": {"medical": {"passed": 3, "n": 3}}}, {"regressed": ["x"]}, 3) == []


def test_runs_through_the_real_run_endpoint(client, monkeypatch):
    """ผ่าน /run เส้นทางเดียวกับผู้ใช้ (Gemini ปลอมใน conftest) — ได้ answer_source = llm"""
    from tests.conftest import FAKE_LLM
    monkeypatch.setitem(FAKE_LLM, "text", "ลองโทร 1669 ทันทีนะคะ ระหว่างรอให้นอนตะแคง")
    rows = ea.run([("medical", "พ่อหมดสติล้มในห้องน้ำ", ("1669",))], lambda q: client.post("/run", json={"input": q}).json())
    assert rows[0]["source"] in ("llm", "kernel") and rows[0]["ok"]


def test_skips_cleanly_without_a_key(monkeypatch, capsys):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert ea.main([]) == 0 and "ข้าม" in capsys.readouterr().out
