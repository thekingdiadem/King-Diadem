"""อารมณ์ของปัญญา (ธัมมจักกัปปวัตตนสูตร) — หน้าแชทสงบ ลึก มีอำนาจ · โหมดภาพยนตร์สำหรับอัดคลิป

เจ้าของโปรเจกต์: "อยากให้หน้าแชท สงบ ลึกลับ มีอำนาจ อลังการ เหมือนบทสวดธัมมจักกัปปวัตตนสูตร"
และเลือกสองท่อน: ธรรมจักรที่ไม่มีใครหมุนกลับได้ · ญาณทัสสนะในอริยสัจ ๔ ที่บริสุทธิ์
"""
from pathlib import Path

SRC = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def _fn(start):
    body = SRC[SRC.index(start):]
    return body[:body.index("\n  }\n")]


def test_dhamma_wheel_has_eight_spokes_and_rests_when_calm():
    w = _fn("function drawWheel(")
    assert "i < 8" in w
    assert "if(!REDUCED) WHEEL.a +=" in w and "REDUCED ? .85" in w      # ลดการเคลื่อนไหว = นิ่ง ไม่หายใจ
    assert "6.4" in w                                                     # จังหวะหายใจแบบสวด
    assert "drawWheel(cx, cy, r, tsec, dt, DAWN.show);" in SRC


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
