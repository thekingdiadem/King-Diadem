"""เว็บจริง 21 พ.ย.: "my potassium is 6.4 and eGFR 25"
1) ความเสี่ยงเคยเป็น 0 → ไม่เข้าทางด่วน → AI ตอบเอง ป้ายความเสี่ยงขึ้น "ยังรับมือได้"
2) แผนของ AI หลุดถึงผู้ใช้: "My primary directive is… Plan: 2. … 7. Maintain a supportive and urgent tone.Thank you for sharing…"
"""
from core.kernel_voice import assess, compose, safety_kind
from core.llm_gemini import strip_reasoning

LEAK = """My primary directive is to prioritize safety and reduce harm.
I cannot diagnose or provide medical advice, but I must highlight the seriousness of these numbers and the need for professional help.
I also need to provide emergency contact information for Thailand, as most users are in Thailand, followed by general emergency advice for other regions.

Plan:
2. Clearly state that these numbers are a medical emergency.
3. Strongly advise them to go to the emergency room or seek immediate medical attention.
4. Provide emergency contact numbers for Thailand.
5. Provide general advice for other countries.
6. Reiterate that I am an AI and cannot provide medical advice, reinforcing the need for professional help.
7. Maintain a supportive and urgent tone.Thank you for sharing these numbers with me. I understand you're telling me about your potassium level (6.4) and eGFR (25).

These numbers are very important, and they indicate a serious medical situation that needs immediate attention.

In Thailand, you can call 1669 for medical emergencies."""


def test_critical_lab_is_urgent_and_takes_the_fast_path():
    a = assess("my potassium is 6.4 and eGFR 25")
    assert a["risk_shown"] >= 85 and safety_kind(a) == "danger"
    r = compose("my potassium is 6.4 and eGFR 25", footer=False)
    assert "go to hospital today" in r


def test_normal_kidney_numbers_stay_a_care_plan():
    q = "eGFR 38 creatinine 1.9 age 62 male, BP 150/95, HbA1c 7.8"
    assert assess(q)["risk_shown"] < 60
    assert "stage G3b" in compose(q, footer=False)


def test_ai_plan_does_not_reach_the_user():
    out = strip_reasoning(LEAK)
    assert "primary directive" not in out and "Plan:" not in out and "Maintain a supportive" not in out
    assert "I also need to provide" not in out
    assert out.startswith("Thank you for sharing these numbers") and "1669" in out
