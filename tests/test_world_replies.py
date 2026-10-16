"""ยุโรป อเมริกา แอฟริกา + เรื่องทั่วไปในภาษาเอเชีย — เดิมได้คำตอบภาษาอังกฤษ (หรือ Risk 0)"""
import pytest

from core.kernel_voice import compose
from core.world_replies import GENERAL_ASIA, WORLD_REPLY, reply_for, world_lang

URGENT = [("fr", "ma mère ne respire plus"), ("de", "mein mann schlägt mich"), ("pt", "minha mãe não respira"),
          ("it", "voglio morire"), ("uk", "я хочу померти"), ("pl", "mąż mnie bije"), ("nl", "help mij"),
          ("sw", "mama hapumui"), ("am", "ባሌ ይመታኛል"), ("ha", "ina so in mutu"), ("yo", "ọkọ mi ń lù mí"),
          ("zu", "umama akaphefumuli"), ("af", "my man slaan my"), ("so", "i caawi")]


@pytest.mark.parametrize("lang,text", URGENT)
def test_urgent_reply_in_own_language(lang, text):
    first = compose(text).split("\n")[0]
    assert first in {r[0] for r in WORLD_REPLY[lang].values()}, (lang, first)


@pytest.mark.parametrize("lang,text", [("fr", "je suis très fatigué avec mon travail aujourd'hui"), ("vi", "hôm nay tôi rất mệt vì công việc"),
                                       ("my", "ဒီနေ့ အလုပ်မှာ အရမ်းပင်ပန်းတယ်"), ("sw", "mimi nina shida na kazi yangu leo")])
def test_general_reply_in_own_language(lang, text):
    assert compose(text).split("\n")[0] == reply_for(lang, "general")[0]


@pytest.mark.parametrize("t", ["I am very tired with my job today", "help me with my homework", "my mom is not ok"])
def test_english_is_not_misdetected(t):
    assert world_lang(t) is None


def test_yoruba_is_not_vietnamese():
    assert world_lang("mo fẹ́ kú") == "yo"
    assert world_lang("hôm nay tôi rất mệt") == "vi"


def test_australia_number_in_english_emergency():
    assert "000 in Australia" in compose("my dad collapsed and is not breathing")


def test_every_reply_is_complete():
    for lang, kinds in WORLD_REPLY.items():
        assert set(kinds) == {"crisis", "medical", "violence", "help", "general"}, lang
    for opener, steps, ask in list(GENERAL_ASIA.values()) + [r for k in WORLD_REPLY.values() for r in k.values()]:
        assert opener and ask and len(steps) == 3
