"""แผนที่โมเดลเขียนเป็นภาษาอังกฤษธรรมดาก่อนคำตอบ — เคยหลุดถึงผู้ใช้ทั้งก้อน (หน้าจอจริง "Decision=Revenge/Entropy")"""
import pytest

from core.llm_gemini import strip_reasoning

LEAK = '''**My immediate response should:**
1. Acknowledge the user's input directly.
2. Gently inquire about the user's intent or meaning behind this "equation" without being judgmental.
3. Reaffirm LYLA's core principles, especially regarding harm reduction and choice.

The internal state indicates [PAUSE], [Risk: LOW], and [ยังไม่ผ่าน: วิริยะ–สมาธิ — รอ 24 ชม. ได้ไหม]. This suggests the user might be moving too fast. I need to address the concept of "Revenge" directly but gently.

The user's language is English, so I must respond in English.

Strategizing complete. I will now generate the response based on the plan.That's a very thought-provoking statement you've put forward: "Decision = Revenge/Entropy."

May I ask what you mean by framing a decision in terms of "Revenge" and "Entropy"?'''


def test_plain_english_plan_is_removed():
    out = strip_reasoning(LEAK)
    assert out.startswith("That's a very thought-provoking")
    for bad in ("My immediate response", "internal state", "user's language", "Strategizing", "ยังไม่ผ่าน"):
        assert bad not in out


def test_plan_without_closing_sentence_is_removed():
    t = "My response should:\n1. Be kind.\n2. Ask a question.\n\nThe user's language is English.\n\nHi! What's on your mind today?"
    assert strip_reasoning(t) == "Hi! What's on your mind today?"


@pytest.mark.parametrize("ok", ["I need you to know you're not alone. Call 1323.", "Let me help you with that. First, breathe.",
                                "สวัสดีค่ะ ยินดีช่วยนะคะ", "The user agreement says you can cancel anytime."])
def test_normal_replies_are_untouched(ok):
    assert strip_reasoning(ok) == ok


# ── รอบหาจุดรั่ว: หมายเหตุกลางประโยค · ห่อความคิด · ไม่ตัดคำตอบดีทิ้ง ────────────────────
from core.llm_gemini import scrub_internal, strip_notes

_S = lambda x: scrub_internal(strip_notes(strip_reasoning(x)))
_ANS = "ฟังดูเหนื่อยมากเลยนะคะ ลองพักสักครู่ก่อนค่ะ"


@pytest.mark.parametrize("leak", [
    f"ฉันเห็นว่า [Risk: LOW] ตอนนี้ {_ANS}", f"Based on [PAUSE], {_ANS}", f"[RELATIONSHIP] ฟังก่อน ไม่ตัดสิน\n{_ANS}",
    f"<thinking>[Risk: LOW] user is tired</thinking>\n{_ANS}", f"```thought\n[PAUSE]\n```\n{_ANS}",
    f"Draft: abc\n\nFinal answer: {_ANS}", '{"analysis": "[Risk: LOW]", "reply": "%s"}' % _ANS,
    f"Thought process: user is sad.\n\n{_ANS}", f"{_ANS} [โพธิปักขิยธรรม: PAUSE · ยังไม่ผ่าน: วิริยะ–สมาธิ]",
])
def test_internal_notes_never_reach_the_user(leak):
    out = _S(leak)
    for bad in ("Risk: LOW", "PAUSE", "RELATIONSHIP", "<thinking", "```", "Draft", "analysis", "Thought process", "ยังไม่ผ่าน"):
        assert bad not in out, (leak, out)


@pytest.mark.parametrize("good", [
    "I hear you.\n\nWe need to keep you safe right now. Please call 1669 or 1323.",
    "Let me think about this with you.\n\nYou have two options: rest today, or talk to your boss.",
    "Okay, let me explain the difference between the two plans.",
    "Plan: 1) save 3 months expenses 2) apply to 2 jobs", "เบอร์ที่โทรได้ [1323, 1669]\nดูแลตัวเองนะคะ",
    "1. Do you have food today: Yes\n2. Safe place: No\n3. Someone to call: Yes\nOK let's start with a safe place.",
])
def test_good_replies_are_kept_whole(good):
    assert _S(good) == good


def test_run_json_hides_engine_internals(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": "เหนื่อยมาก", "context": {"energy": 10, "money": 5, "sleep": 2}}).json()
    blob = str(d)
    assert "context_for_lyla" not in blob and "SURVIVOR ENGINE" not in blob and "collapse_chain" not in d
