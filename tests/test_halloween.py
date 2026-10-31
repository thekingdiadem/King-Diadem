"""ธีมฮาโลวีน (เจ้าของโปรเจกต์ชวนเข้าธีมวันฮาโลวีน 31 ต.ค.)

แอปนี้มีคนเข้ามาคุยตอนเจอเรื่องหนัก — ธีมต้องน่ารัก ไม่หลอน เปิดเองเท่านั้น
ไม่ขยับเมื่อตั้งลดการเคลื่อนไหว และซ่อนทั้งหมดตอนกำลังคุยเรื่องด่วน/วิกฤต"""
from pathlib import Path
from tests._front import front_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = front_page()


def test_opt_in_toggle_and_remembered():
    assert 'id="halloween-btn" aria-pressed="false"' in HTML
    assert "localStorage.getItem('kd-halloween') === '1'" in HTML and "lsSet('kd-halloween', hw ? '1' : '0')" in HTML
    assert "html.kd-halloween:not(.kd-hush) #halloween{display:block}" in HTML
    # ช่วงเทศกาลแค่ชวน (วันละครั้ง) ไม่เปิดให้เอง
    nudge = HTML[HTML.index("var d = new Date(), md ="):HTML.index("})();", HTML.index("var d = new Date(), md =")) ]
    assert "if(hw || md < 1024 || md > 1101) return;" in nudge and "kd-halloween" not in nudge.replace("kd-hw-nudge-", "")


def test_hidden_during_urgent_conversations():
    assert "document.documentElement.classList.toggle('kd-hush'," in HTML
    assert "la.tr.mode === 'crisis' || (la.tr.risk || 0) >= 75 || /1323|1669/.test(la.t)" in HTML


def test_bats_stay_still_when_motion_is_reduced_and_never_block_taps():
    assert "#halloween{display:none;position:fixed;inset:0;z-index:1;pointer-events:none" in HTML
    assert "html.kd-calm #halloween i" in HTML and "@media (prefers-reduced-motion:reduce){#halloween i{animation:none" in HTML
    assert 'id="halloween" aria-hidden="true"' in HTML                       # โปรแกรมอ่านหน้าจอไม่อ่านค้างคาว
