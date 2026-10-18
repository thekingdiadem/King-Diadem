"""คนต่างชาติในไทยต้องได้เบอร์ในไทย — เดิมคำตอบ en/zh/ja/ko/es ให้แค่ 911 · 110 · 119 (โทรจากไทยไม่ติด)
และเรื่องด่วนของแรงงานข้ามชาติ (จมน้ำ กินยาเยอะ นายจ้างยึดพาสปอร์ต) ใน 10 ภาษาเคยหลุด"""
import pytest

from core.kernel_voice import assess, compose
from core.llm_gemini import _lang_directive


@pytest.mark.parametrize("t", ["I want to die", "我想死", "死にたい", "죽고 싶어", "quiero morir",
                               "我妈妈不能呼吸了", "mi madre no respira", "老公打我", "엄마가 숨을 안 쉬어"])
def test_foreign_language_replies_include_thai_numbers(t):
    out = compose(t)
    assert "1669" in out and "1323" in out and "1155" in out, (t, out[:200])


@pytest.mark.parametrize("lang", ["en", "zh", "ja", "ko", "es"])
def test_ai_prompt_puts_thai_numbers_first(lang):
    d = _lang_directive(f"[ภาษาผู้ใช้: {lang}] x")
    assert all(n in d for n in ("1669", "191", "1323", "1155"))


@pytest.mark.parametrize("t", [
    "မနေချင်တော့ဘူး", "ပတ်စ်ပို့ သိမ်းထားတယ် ထွက်ခွင့်မပေးဘူး", "သားလေး ရေနစ်သွားတယ်", "ဆေးအများကြီး သောက်လိုက်ပြီ",
    "ចៅហ្វាយយកលិខិតឆ្លងដែនខ្ញុំ", "កូនលង់ទឹក", "ລູກຈົມນ້ຳ", "老板扣了我的护照不让我走", "살기 싫어",
    "chủ giữ hộ chiếu của tôi không cho đi", "tôi uống nhiều thuốc ngủ", "majikan menahan paspor saya",
])
def test_migrant_worker_emergencies_are_caught(t):
    a = assess(t)
    assert a["crisis"] or a["text_risk"] >= 50 or a.get("intl_urgent"), t


def test_khmer_drowning_uses_khmer_letters():
    """อักษร "ล" พม่า (U+101C) กับเขมร (U+179B) หน้าตาเหมือนกัน — เคยพิมพ์ผิดตัวจนจับไม่ได้"""
    from core.lang_signals import WORLD_URGENT
    assert "លង់ទឹក" in WORLD_URGENT["medical"]
    assert "လង់" not in WORLD_URGENT["medical"]


@pytest.mark.parametrize("t", ["今天累死了", "笑死我了", "お腹すいて死にそう", "배고파 죽겠다", "mệt chết đi được"])
def test_everyday_idioms_stay_calm(t):
    a = assess(t)
    assert not a["crisis"] and a["text_risk"] < 50 and not a.get("intl_urgent"), t
