"""เว็บ GitHub Pages (docs/index.html) — ลื่นบนมือถือ และกดได้ด้วยคีย์บอร์ด
เดิมวาดดาว 1,800 ดวงใหม่ทุกเฟรม + กระจกฝ้าบนพื้นหลังที่ขยับ (เครื่องทำงาน ~34% ตลอดเวลา · หลังแก้ ~6%)
และเมนูใช้ onclick="scrollTo(...)" ไม่มีลิงก์จริง (Tab ไม่ถึง) ทั้งยังทับ window.scrollTo ของเบราว์เซอร์"""
import re
from pathlib import Path

HTML = (Path(__file__).resolve().parent.parent / "docs" / "index.html").read_text(encoding="utf-8")


def test_menu_uses_real_links_to_existing_sections():
    assert "onclick=" not in HTML and "function scrollTo" not in HTML
    for target in re.findall(r'class="nav-link" href="#([\w-]+)"', HTML):
        assert f'id="{target}"' in HTML, target


def test_star_field_is_painted_once_and_pauses_when_hidden():
    assert "paintStill" in HTML and "visibilitychange" in HTML and "prefers-reduced-motion" in HTML
    assert "ctx.arc(" not in HTML                      # ไม่วาดวงกลมทีละดวงทุกเฟรมอีก


def test_mobile_blur_rule_targets_only_glass_panels():
    assert "*{-webkit-backdrop-filter" not in HTML     # เคยใส่เบลอให้ทุกชิ้นในหน้า ทำให้ช้ากว่าเดิม
