"""ขอให้ "ท่องปรัชญาปารมิตา" ต้องได้ตัวบทจริง ไม่ใช่คำอธิบาย และเสียงสันสกฤตต้องถูก
เจ้าของโปรเจกต์เจอ AI ตอบอธิบายแทนการท่อง ใช้คำว่า "ความว่างเปล่า" และถอดเสียงผิด เช่น "โบดิซัวฮา\""""
import pytest

from core.kernel_voice import compose, heart_sutra_recital


@pytest.mark.parametrize("q", ["ท่องปรัชญาปารมิตาให้ฟังหน่อย", "สวดหฤทัยสูตรให้ฟังที", "ขอบทหัวใจสูตร", "recite the heart sutra"])
def test_recite_request_gets_the_text(q):
    out = compose(q)
    assert "คัมภีราม" in out and "โพธิ สวาหา" in out


def test_sanskrit_sounds_are_correct():
    t = heart_sutra_recital()
    for good in ("คัมภีราม", "อตรัสโต", "คะเต คะเต ปาระคะเต ปาระสังคะเต โพธิ สวาหา"):
        assert good in t
    for bad in ("กรรมบิรัม", "ทรัสโส", "โบดิซัวฮา", "ความว่างเปล่า"):
        assert bad not in t


def test_asking_what_it_means_is_not_a_recital():
    assert "อารยาวะโลกิเตศวะโร" not in compose("ปรัชญาปารมิตาคืออะไร")


def test_ai_is_told_emptiness_not_nothingness():
    from core import llm_gemini
    src = open(llm_gemini.__file__, encoding="utf-8").read()
    assert "ห้ามใช้ \"ความว่างเปล่า\"" in src
    assert "ให้ตัวบทจริงทีละวรรค" in src


def test_four_truths_hidden_when_no_suffering_seen():
    from tests._front import front_page
    assert "A.dukkha === 'ยังไม่ชัด') return ''" in front_page()
