"""รอบแก้ของค้าง: ติดเพลง · ภัยภาษาอังกฤษในบ้าน · W เริ่มต้น · ครู/เพื่อนด่า"""
import pathlib
from core.kernel_voice import assess


def test_addicted_to_song_is_not_addiction():
    for t in ("I'm addicted to this song", "addicted to coffee", "I'm addicted to you"):
        assert "addiction" not in assess(t)["topics"], t
    for t in ("I am addicted to gambling", "addicted to pills", "I'm addicted to drugs"):
        assert "addiction" in assess(t)["topics"], t


def test_english_hazard_in_my_house_is_near():
    assert assess("There is a flood in my house")["risk"] > assess("if there is a flood")["risk"]
    assert assess("My house is on fire")["risk"] >= 60
    assert assess("I watched the news about a flood now")["risk"] < 60


def test_verbal_abuse_outside_family_is_detected():
    for t in ("ครูบอกว่าผมโง่ทุกวัน", "เพื่อนด่าทุกวัน", "หัวหน้าตะคอกใส่ทุกวัน"):
        assert "bullying" in assess(t)["topics"], t
    assert "bullying" not in assess("ครูสอนดีมาก")["topics"]


def test_sigma_panel_does_not_show_default_w_as_100():
    page = (pathlib.Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")
    assert "ใช้ 100 ชั่วคราว" in page
