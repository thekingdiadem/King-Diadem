"""อารมณ์ของปัญญา (ธัมมจักกัปปวัตตนสูตร) — หน้าแชทสงบ ลึก มีอำนาจ · โหมดภาพยนตร์สำหรับอัดคลิป

เจ้าของโปรเจกต์: "อยากให้หน้าแชท สงบ ลึกลับ มีอำนาจ อลังการ เหมือนบทสวดธัมมจักกัปปวัตตนสูตร"
และเลือกสองท่อน: ธรรมจักรที่ไม่มีใครหมุนกลับได้ · ญาณทัสสนะในอริยสัจ ๔ ที่บริสุทธิ์
"""
from pathlib import Path
from tests._front import front_page  # noqa: E402

SRC = front_page()


def _fn(start):
    body = SRC[SRC.index(start):]
    return body[:body.index("\n  }\n")]


def test_dhamma_wheel_has_eight_spokes_and_rests_when_calm():
    assert "i < 8" in _fn("function wheelSprite(")
    w = _fn("function drawWheel(")
    assert "if(!REDUCED) WHEEL.a +=" in w and "REDUCED ? .85" in w      # ลดการเคลื่อนไหว = นิ่ง ไม่หายใจ
    assert "6.4" in w                                                     # จังหวะหายใจแบบสวด
    assert "drawWheel(cx, cy, r, tsec, dt, DAWN.show" in SRC


def test_grand_but_light_cached_sprites_not_rebuilt_each_frame():
    """อลังการขึ้นแต่ไม่แลค: วงล้อและแสงอาทิตย์วาดเก็บเป็นภาพครั้งเดียว ทุกเฟรมแค่ drawImage"""
    w = _fn("function drawWheel(")
    assert "createLinearGradient" not in w and "createRadialGradient" not in w and "drawImage(cv" in w
    assert "if(WHEEL.key === k) return WHEEL.cv;" in SRC
    sr = _fn("function drawSunrise(")
    assert "createRadialGradient" not in sr and "flareSprite()" in sr
    assert "if(FLARE) return FLARE;" in SRC
    assert "if(CINEMA.on && !REDUCED) drawSunrise(" in SRC                # ลดการเคลื่อนไหว = ไม่มีประกายวาบ


def test_both_chosen_passages_are_chanted_in_pali():
    for line in ("อะนุตตะรัง ธัมมะจักกัง ปะวัตติตัง", "ยะถาภูตัง ญาณะทัสสะนัง สุวิสุทธัง อะโหสิ",
                 "anuttaraṃ dhammacakkaṃ pavattitaṃ", "yathābhūtaṃ ñāṇadassanaṃ suvisuddhaṃ ahosi"):
        assert line in SRC


def test_cinema_mode_hides_ui_and_always_lets_you_out():
    assert 'id="cinema-btn"' in SRC and 'id="cinema"' in SRC
    assert "html.kd-cinema :is(#sidebar,#topbar,#composer,#tabbar" in SRC
    cine = SRC[SRC.index("var Cine = (function(){"):]
    cine = cine[:cine.index("})();")]
    assert "$('#cinema').addEventListener('click', exit);" in cine           # แตะจอเพื่อออก
    assert "e.key === 'Escape'" in cine and "fullscreenchange" in cine
    assert "Cosmos.cinema(false)" in cine


def test_new_answer_unfolds_line_by_line_but_not_when_calm():
    assert "@keyframes kd-chant" in SRC
    assert "m.ts === CHANT_TS && !REDUCED" in SRC
    assert "if(born) CHANT_TS = born.ts;" in SRC


def test_top_level_code_does_not_call_cosmos_private_helpers():
    """บั๊กจริง: renderMsgs (ระดับบนสุดของสคริปต์) เรียก clamp() ซึ่งมีแค่ข้างใน Cosmos
    ได้คำตอบใหม่ทีไรหน้าแชทวาดข้อความไม่สำเร็จ (ReferenceError) — ตรวจทุกฟังก์ชันระดับบนสุด"""
    import re
    js = (Path(__file__).resolve().parent.parent / "static" / "app.js").read_text(encoding="utf-8")
    private = [n for n in ("clamp", "ease", "hash", "kick") if not re.search(r"^(?:function " + n + r"\b|var " + n + r"\b)", js, re.M)]
    for m in re.finditer(r"^function (\w+)\([^)]*\)\{\n(.*?)^\}", js, re.M | re.S):
        for n in private:
            assert not re.search(r"(?<![\w.])" + n + r"\(", m.group(2)), f"{m.group(1)}() เรียก {n}() ที่ไม่มีในระดับบนสุด"
