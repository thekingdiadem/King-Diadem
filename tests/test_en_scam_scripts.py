"""บทพูดมิจฉาชีพภาษาอังกฤษที่เคยได้ Risk 0 ทั้งชุด — ต้องขึ้นเตือน ส่วนเรื่องธรรมดาต้องสงบ"""
import pytest

from core.kernel_voice import assess

SCAM = ["someone called and said he's from the IRS and I must pay in gift cards", "a man asked for the code they sent to my phone",
        "said he's my grandson in jail and needs bail money", "asked me to install AnyDesk to fix my computer",
        "wants me to invest in crypto, guaranteed 20% a week", "told me to move my savings to a safe account",
        "said a warrant is out for my arrest unless I pay now", "my online girlfriend asked me to send money for a plane ticket"]
CALM = ["I bought a gift card for my mom", "can I pay with gift card at target", "I installed teamviewer for work",
        "the police said I should pay the parking fine", "my bank sent a verification code to my phone when I logged in"]


@pytest.mark.parametrize("t", SCAM)
def test_en_scam_script_is_flagged(t):
    a = assess(t)
    assert a["text_risk"] >= 60 and a.get("scam"), (t, a["text_risk"], a.get("scam"))


@pytest.mark.parametrize("t", CALM)
def test_en_ordinary_money_talk_stays_calm(t):
    assert assess(t)["text_risk"] < 60, t
