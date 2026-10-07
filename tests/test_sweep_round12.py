"""รอบหาบั๊ก 12: น้ำขึ้น (อังกฤษ) · ทำร้ายผู้สูงอายุ · มีคนตาม · ค่าจ้างค้าง (อังกฤษ) · โดนแฮก"""
from core.kernel_voice import assess


def test_english_rising_water_is_flood():
    for t in ("water is rising", "the river is overflowing"):
        assert assess(t)["disaster"], t


def test_elder_abuse_reversed_word_order():
    for t in ("ป้าโดนลูกตี", "ยายโดนหลานด่าทุกวัน", "my grandma is being hit by her son"):
        assert "elder_abuse" in assess(t)["topics"], t
    assert "elder_abuse" not in assess("ตามสบาย")["topics"]


def test_someone_following_me_home_thai():
    assert assess("มีคนตามผมกลับบ้าน")["risk"] >= 70
    assert assess("ตามผมมาหน่อย")["risk"] < 60


def test_english_unpaid_wages():
    assert "labor" in assess("my boss hasnt paid me for 3 months")["topics"]


def test_hacked_account_is_scam_lost():
    for t in ("my phone was hacked", "บัญชีโดนแฮก"):
        assert assess(t)["scam"] == ["lost"], t
