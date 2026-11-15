"""เทสต์สุ่มรอบ 12: สำลัก · เด็กกินสารเคมี · เจ็บหน้าอก+เหงื่อแตก · ไฟไหม้ — เดิมได้ Risk 0 ใน ja zh ko es vi
และคนเวียดนามเคยได้คำตอบด่วนเป็นภาษาสเปน"""
import pytest
from core.kernel_voice import assess, compose

R = ["家が燃えている、逃げられない", "赤ちゃんがおもちゃを喉に詰まらせた", "子供が洗剤を飲んだ", "宝宝被玩具卡住喉咙", "孩子喝了洗涤剂",
     "爸爸胸口痛还出冷汗", "아기가 장난감이 목에 걸렸어", "아이가 세제를 마셨어", "아빠가 가슴이 아프고 식은땀을 흘려",
     "mi bebé se atragantó con un juguete", "nhà tôi đang cháy, không ra được", "em bé bị hóc đồ chơi", "con tôi uống nước tẩy"]


@pytest.mark.parametrize("q", R)
def test_emergency_is_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q,start", [("em bé bị hóc đồ chơi", "Đây là tình huống khẩn cấp"),
                                     ("con tôi uống nước tẩy", "Đây là tình huống khẩn cấp"),
                                     ("nhà tôi đang cháy, không ra được", "Mạng sống của bạn")])
def test_vietnamese_emergency_answered_in_vietnamese(q, start):
    out = compose(q, footer=False)
    assert out.startswith(start)
    if "cháy" in q:
        assert "199" in out and "114" in out


@pytest.mark.parametrize("q", ["洗剤を買いに行った", "喉に詰まらせないように小さく切った", "我喝了水", "목에 걸린 가시 빼는 법", "me atraganté de risa"])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["胸が痛いほど感動した", "Tôi đau ngực vì cười nhiều quá"])
def test_chest_idioms_and_laughing_stay_calm(q):
    # สำนวน "ซึ้งจนเจ็บหัวใจ" / เจ็บหน้าอกเพราะหัวเราะ — เคยได้ 85
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["胸が痛い", "đau ngực dữ dội", "bố tôi đau ngực và vã mồ hôi"])
def test_real_chest_pain_still_heard(q):
    assert assess(q)["risk_shown"] >= 65
