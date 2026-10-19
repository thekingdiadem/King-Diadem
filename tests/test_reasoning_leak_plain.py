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
