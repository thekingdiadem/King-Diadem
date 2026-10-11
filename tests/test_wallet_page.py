"""หน้า Wallet: เข้าชุดกับทั้งเว็บ (กรอบแก้วขอบแสงอุ่น/เย็น · ฟ้าดาวไม่มีศูนย์กลาง) แต่ระบบจ่ายเงินเดิมต้องอยู่ครบ"""
import re
from pathlib import Path

HTML = (Path(__file__).resolve().parent.parent / "static" / "wallet.html").read_text(encoding="utf-8")


def test_payment_flow_is_untouched():
    """ID และ endpoint ที่ JS ใช้ต้องอยู่ครบ — ปรับหน้าตาแล้วการเติมเงินต้องทำงานเหมือนเดิม"""
    for i in ("balance-display", "balance-sub", "wallet-account", "amount-label", "wallet-amount",
              "topup-btn", "portal-btn", "status-box", "history-list"):
        assert f'id="{i}"' in HTML, i
    for ep in ("'/wallet/balance'", "'/wallet/topup'", "'/billing-portal'"):
        assert ep in HTML
    assert "PromptPay" in HTML and "จัดการสมาชิก · ยกเลิก · ใบเสร็จ" in HTML
    assert "location.href = d.url;" in HTML


def test_thai_uses_looped_font():
    """ฟอนต์ไทยแบบไม่มีหัวทำให้ "ระบบ" อ่านเป็น "ระUU" — หน้านี้ต้องใช้แบบมีหัวเหมือนหน้าอื่น"""
    assert "Noto+Sans+Thai+Looped" in HTML
    assert "family=Noto+Sans+Thai:" not in HTML
    assert "--f-body: 'Noto Sans Thai Looped'" in HTML


def test_disabled_topup_stays_dim_after_reveal():
    """แอนิเมชันตอนเปิดหน้าเคยค้าง opacity:1 ทับปุ่ม disabled (ยังไม่ล็อกอิน) จนดูกดได้
    ต้องใช้ fill แบบ backwards ให้คืนค่าสไตล์เดิมเมื่อเล่นจบ"""
    assert ".card > * { animation:kd-rack .9s var(--ease) backwards;" in HTML
    assert ".btn-topup:disabled { opacity:0.42;" in HTML
    assert not re.search(r"\.card > \*[^}]*\bboth\b", HTML)


def test_sky_has_no_center_and_respects_motion():
    """ฟ้าดาวใช้ไฟล์กลาง cinema_sky.js ร่วมกับหน้าเข้าสู่ระบบ/สมัคร (รายละเอียดเทสต์อยู่ใน test_portal_pages)"""
    assert '<canvas id="sky"' in HTML
    assert '<script src="/static/cinema_sky.js" defer></script>' in HTML
    assert "@media (prefers-reduced-motion:reduce)" in HTML


def test_quick_amounts_are_buttons_and_show_selection():
    """ปุ่มจำนวนเงินกดด้วยคีย์บอร์ดได้ และไฮไลต์ตามจำนวนที่กรอก"""
    assert HTML.count('<button type="button" class="quick-btn"') == 4
    assert "b.classList.toggle('on', Number(b.dataset.v) === n)" in HTML
