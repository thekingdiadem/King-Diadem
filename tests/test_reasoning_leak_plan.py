"""ความคิดของโมเดลหลุดถึงผู้ใช้ (หน้าจอจริง พ.ย. 2569): "My primary directive is…" + "Plan:" แล้วคำตอบจริงต่อท้ายข้อ 7 ไม่เว้นวรรค"""
from core.llm_gemini import strip_reasoning

LEAK = """My primary directive is to prioritize safety and reduce harm.
I cannot diagnose or provide medical advice, but I must highlight the seriousness of these numbers and the need for professional help.
I also need to provide emergency contact information for Thailand, as most users are in Thailand, followed by general emergency advice for other regions.

Plan:
2. Clearly state that these numbers are a medical emergency.
3. Strongly advise them to go to the emergency room or seek immediate medical attention.
4. Provide emergency contact numbers for Thailand.
7. Maintain a supportive and urgent tone.Thank you for sharing these numbers with me. I understand you're telling me about your potassium level (6.4).

**It is crucial that you seek immediate medical help right now.**

In Thailand, you can call these numbers for urgent help:
* 1669 for medical emergencies (ambulance)"""


def test_plan_and_directive_are_removed_answer_kept():
    out = strip_reasoning(LEAK)
    assert out.startswith("Thank you for sharing")
    assert "primary directive" not in out and "Plan:" not in out and "Maintain a supportive" not in out
    assert "1669" in out and "crucial" in out


def test_normal_answer_with_a_plan_word_is_untouched():
    txt = "Here's a simple plan you can try this week.\n\n1. Walk 10 minutes after dinner.\n2. Cut instant noodles to twice a week."
    assert strip_reasoning(txt) == txt


def test_critical_potassium_is_not_shown_as_manageable():
    from core.kernel_voice import assess
    assert assess("my potassium is 6.4 and eGFR 25")["risk_shown"] >= 75
    assert assess("โพแทสเซียม 6.4")["risk_shown"] >= 75
    assert assess("โพแทสเซียม 4.2")["risk_shown"] < 60


def test_users_plan_with_glued_sentence_is_kept():
    txt = "Plan:\n1. Walk 10 minutes after dinner.\n2. Cut salt.Then check your pressure weekly."
    assert strip_reasoning(txt) == txt
