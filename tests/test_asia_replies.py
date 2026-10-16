"""เรื่องด่วนในภาษาเอเชียต้องได้คำตอบเป็นภาษานั้น พร้อมเบอร์ในไทย — เดิมได้ภาษาอังกฤษหรือ Risk 0"""
import pytest

from core.asia_replies import REPLY, asia_lang
from core.kernel_voice import compose

CASES = [("my", "အမေ အသက်မရှူနိုင်ဘူး", "1669"), ("km", "ប្តីវាយខ្ញុំ", "191"), ("lo", "ຂ້ອຍຢາກຕາຍ", "1323"),
         ("vi", "mẹ tôi không thở được", "1669"), ("id", "suamiku memukulku", "191"), ("ms", "saya nak mati", "1323"),
         ("tl", "hindi makahinga ang nanay ko", "1669"), ("hi", "पति मुझे मारता है", "191"), ("ne", "मलाई मर्न मन लाग्छ", "1323"),
         ("bn", "আমি মরে যেতে চাই", "1323"), ("ur", "میں مرنا چاہتا ہوں", "1323"), ("ta", "அம்மா மூச்சு விடவில்லை", "1669"),
         ("si", "මට මැරෙන්න ඕනේ", "1323"), ("fa", "شوهرم منو می‌زنه", "191"), ("ar", "أمي لا تتنفس", "1669"),
         ("tr", "kocam beni dövüyor", "191")]


@pytest.mark.parametrize("lang,text,number", CASES)
def test_reply_in_own_language(lang, text, number):
    out = compose(text)
    assert out.split("\n")[0] in {r[0] for r in REPLY[lang].values()}, (lang, out[:80])
    assert number in out


@pytest.mark.parametrize("t,lang", [("suamiku memukulku", "id"), ("hindi makahinga ang nanay ko", "tl"), ("imdat", "tr"),
                                    ("زوجي يضربني", "ar"), ("میں مرنا چاہتا ہوں", "ur")])
def test_asia_lang_detection(t, lang):
    assert asia_lang(t) == lang


def test_every_language_has_all_four_kinds():
    for lang, kinds in REPLY.items():
        assert set(kinds) == {"crisis", "medical", "violence", "help"}, lang
        for opener, steps, ask in kinds.values():
            assert opener and ask and len(steps) == 3
