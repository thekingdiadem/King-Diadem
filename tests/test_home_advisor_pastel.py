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
    assert "_t('⏳ เหลือเวลาตัดสินใจราว {n} วัน', {n: n})" in PAGE     # แปลได้ 3 ภาษา (static/i18n.js)
    assert "'🌿 ยังมีเวลา ไม่ต้องรีบตัดสินใจ'" in PAGE and "'⏳ ควรเริ่มวันนี้'" in PAGE
    assert "if(!tw || !tw.status) return '';" in PAGE                    # ไม่มีข้อมูลจริงก็ไม่แสดง ไม่เดา
    assert "cls = n <= 7 ? 'bad' : n <= 30 ? 'warn' : 'ok';" in PAGE       # เกณฑ์เดียวกับ core/choice_dynamics.py


def test_pastel_layer():
    assert "--mint:#bff0e0; --rose:#ffc8dd; --lav:#d9ccff;" in PAGE
    assert "#view-chat::before{" not in PAGE            # หมอกพาสเทลบนอวกาศดูเลอะ (เจ้าของโปรเจกต์) — เอาออก ใช้โหมดสีแทน
    assert "#send{background:var(--pastel);" in PAGE
    assert ".tw-card.warn{" in PAGE and ".tw-card.bad{" in PAGE


def test_real_sky_from_hipparcos_catalog():
    """ดาวบนหน้าแรกเป็นดาวจริงแบบ Stellarium: ตำแหน่ง ความสว่าง สีจริง (เดิมเป็นจุดสุ่ม + ดาวลูกไก่วาดเอง)"""
    import json
    sky = json.loads((ROOT / "static" / "earth" / "sky_taurus.json").read_text(encoding="utf-8"))
    assert "Hipparcos" in sky["source"] and "BSD-3-Clause" in sky["source"]
    stars = sky["stars"]
    assert len(stars) > 4000 and all(len(r) == 4 for r in stars)
    m45 = [r for r in stars if abs(r[0] - 56.75) < 1.2 and abs(r[1] - 24.12) < 1 and r[2] < 4.5]
    assert len(m45) >= 6                                                    # ดาวลูกไก่ 6 ดวงที่ตาเปล่าเห็น
    alde = [r for r in stars if abs(r[0] - 68.98) < .05 and abs(r[1] - 16.51) < .05]
    assert alde and alde[0][2] < 1 and alde[0][3] > 1.4                      # ดาวโรหิณีสว่างและสีส้ม (B−V ~1.5)
    assert "fetch('/static/earth/sky_taurus.json')" in PAGE and "function bvRGB(b)" in PAGE
    assert "ctx.globalCompositeOperation = 'destination-out'" in PAGE      # โลก/ดาวเคราะห์บังดาว
    assert "['ดาวลูกไก่', 56.75, 24.12" in PAGE and "['ดาวไถ', 84.05, -1.2" in PAGE
    assert "if(paper && !inM45) return;" in PAGE                            # พื้นสว่างเหลือแค่ดาวลูกไก่
    assert "drawPleiades" not in PAGE and "*(.55+.45*sin(t*.8+hc*40.))*0.;" in PAGE   # จุดสี่เหลี่ยมแบบพิกเซลปิดแล้ว
    readme = (ROOT / "static" / "earth" / "README.md").read_text(encoding="utf-8")
    assert "Olaf Frohn" in readme and "Hipparcos" in readme
