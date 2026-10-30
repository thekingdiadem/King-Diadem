"""หน้าแรก: บอกว่าที่นี่ช่วยอะไร + ตัวอย่างคำถาม · ช่วงตัดสินใจเป็นวันใต้คำตอบ · โทนพาสเทล · ดาวลูกไก่"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
I18N = (ROOT / "static" / "i18n.js").read_text(encoding="utf-8")


def test_first_visit_explains_and_offers_examples():
    assert '<div class="starters" id="starters">' in PAGE
    assert "ฟรี ไม่ต้องสมัคร" in PAGE and "เล่าเรื่องที่ค้างใจได้เลย" in PAGE
    chips = re.findall(r'<button type="button" class="st-chip" data-q="([^"]+)">', PAGE)
    assert len(chips) == 4 and all(len(q) > 10 for q in chips)
    # แตะแล้วเติมลงช่องพิมพ์ให้แก้ต่อ ไม่ส่งเอง · ซ่อนเมื่อมีแชทหรือเริ่มพิมพ์
    assert "inp.dispatchEvent(new Event('input', { bubbles: true })); inp.focus();" in PAGE
    assert "show = !$('#empty').classList.contains('hide') && !(inp && inp.value.trim());" in PAGE
    assert "syncStarters();\n  paintEq();" in PAGE
    for th in ("ฟรี ไม่ต้องสมัคร", "ตัวอย่างคำถาม", "🌙 นอนไม่หลับมาหลายวัน"):
        assert f"'{th}': [" in I18N


def test_decision_window_shows_in_days_under_reply():
    assert "twCard(t) + helpCard(m.l)" in PAGE
    assert "'⏳ เหลือเวลาตัดสินใจราว ' + n + ' วัน'" in PAGE
    assert "'🌿 ยังมีเวลา ไม่ต้องรีบตัดสินใจ'" in PAGE and "'⏳ ควรเริ่มวันนี้'" in PAGE
    assert "if(!tw || !tw.status) return '';" in PAGE                    # ไม่มีข้อมูลจริงก็ไม่แสดง ไม่เดา
    assert "cls = n <= 7 ? 'bad' : n <= 30 ? 'warn' : 'ok';" in PAGE       # เกณฑ์เดียวกับ core/choice_dynamics.py


def test_pastel_layer():
    assert "--mint:#bff0e0; --rose:#ffc8dd; --lav:#d9ccff;" in PAGE
    assert "#view-chat::before{" in PAGE and "#view-chat>*{position:relative;z-index:1}" in PAGE
    assert "#send{background:var(--pastel);" in PAGE
    assert ".tw-card.warn{" in PAGE and ".tw-card.bad{" in PAGE


def test_pleiades_from_real_sky_positions():
    block = PAGE[PAGE.index("var PLEIADES = ["):PAGE.index("function drawPleiades")]
    stars = re.findall(r"\['(\w+)', (-?[\d.]+), (-?[\d.]+), ([\d.]+)\]", block)
    names = [s[0] for s in stars]
    assert names[0] == "Alcyone" and len(stars) == 9                         # 7 ธิดา + Atlas, Pleione
    for n in ("Atlas", "Electra", "Maia", "Merope", "Taygeta", "Pleione", "Celaeno", "Asterope"):
        assert n in names
    mags = {s[0]: float(s[3]) for s in stars}
    assert min(mags, key=mags.get) == "Alcyone"                              # ดวงที่สว่างที่สุดในกลุ่ม
    assert all(abs(float(s[1])) <= 40 and abs(float(s[2])) <= 30 for s in stars)   # กว้างราว 1 องศา
    assert "ctx.fillText('ดาวลูกไก่'," in PAGE and "if(drew) drawPleiades(" in PAGE
