"""หน้าเว็บใช้ไอคอนลายเส้นของเราเอง (static/icons/kd.svg) ไม่ใช้อิโมจิ
เจ้าของโปรเจกต์: "พวกอิโมจิคนมองก็รู้ว่าทั้งหมดทำมาจาก AI" — งานนี้ต้องดูออกว่ามีคนตั้งใจทำทีละชิ้น
ถ้าเทสต์นี้ล้ม: เปลี่ยนอิโมจิเป็น <svg class="kd-i"><use href="/static/icons/kd.svg#ชื่อ"/></svg> (ใน app.js ใช้ kdIcon('ชื่อ'))
ไอคอนที่ยังไม่มี ให้วาดเพิ่มใน static/icons/kd.svg ด้วยลายเส้นเดียวกัน (ตาราง 24×24 เส้น 1.6 ปลายมน)"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMOJI = re.compile("(?:[\U0001F000-\U0001FAFF]|[☀-➿⬀-⯿⌀-⏿]️|[✅❌⏳⚡⛔❓☕])")
_MAP = re.compile(r'<script type="application/json" id="system-map">.*?</script>', re.S)   # แผนผังไฟล์ สร้างจาก repo (อ้างชื่อเทสต์ตามจริง)
PAGES = sorted(glob.glob(os.path.join(ROOT, "static", "*.html")) + glob.glob(os.path.join(ROOT, "static", "*.js"))
               + glob.glob(os.path.join(ROOT, "static", "*.css")) + glob.glob(os.path.join(ROOT, "static", "i18n", "*.js"))
               + [os.path.join(ROOT, "portfolio.html"), os.path.join(ROOT, "index.html"),
                  os.path.join(ROOT, "core", "survival_guide.py"), os.path.join(ROOT, "core", "survival_page.py"), os.path.join(ROOT, "core", "pregnancy_guide.py")])


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_no_emoji_in_pages():
    found = []
    for path in PAGES:
        for i, line in enumerate(_MAP.sub("", _read(path)).split("\n"), 1):
            for m in EMOJI.finditer(line):
                found.append(f"{os.path.relpath(path, ROOT)}:{i}: {m.group()}")
    assert not found, "ยังมีอิโมจิในหน้าเว็บ — เปลี่ยนเป็นไอคอนจาก static/icons/kd.svg:\n" + "\n".join(found[:40])


def test_every_icon_used_is_drawn():
    drawn = set(re.findall(r'<symbol id="([a-z]+)"', _read(os.path.join(ROOT, "static", "icons", "kd.svg"))))
    used = set()
    for path in PAGES:
        t = _read(path)
        used |= set(re.findall(r"kd\.svg#([a-z]+)", t)) | set(re.findall(r"kdIcon\('([a-z]+)'\)", t)) | set(re.findall(r'"icon": "([a-z]+)"', t))
    used |= set(re.findall(r"\['[^']+', '([a-z]+)'\]", re.search(r"var HZ_KIND = \{.*?\};", _read(os.path.join(ROOT, "static", "app.js"))).group()))
    assert used and not used - drawn, f"เรียกไอคอนที่ยังไม่ได้วาด: {sorted(used - drawn)}"


def test_icons_share_one_hand():
    """ทุกไอคอนวาดบนตารางเดียวกัน เส้นหนาเท่ากัน ปลายมน เส้นสีตามตัวอักษร ข้างในระบายสีพาสเทล — ดูเป็นมือเดียวกันทั้งเว็บ"""
    symbols = re.findall(r"<symbol [^>]+>", _read(os.path.join(ROOT, "static", "icons", "kd.svg")))
    assert len(symbols) >= 40
    for s in symbols:
        for need in ('viewBox="0 0 24 24"', 'stroke="currentColor"', 'stroke-width="1.6"', 'stroke-linecap="round"'):
            assert need in s, s


def test_icons_have_colour_but_stay_calm():
    """เจ้าของโปรเจกต์: "เพิ่มสีสันและทำให้มันดูไม่รก" — ไอคอนส่วนใหญ่มีสีระบาย และไม่มีตัวไหนเส้นยุ่งเกินไป"""
    svg = _read(os.path.join(ROOT, "static", "icons", "kd.svg"))
    symbols = re.findall(r"<symbol .*?</symbol>", svg)
    tinted = [s for s in symbols if re.search(r'(?:fill|stroke)="#[0-9a-f]{6}"', s)]
    assert len(tinted) >= len(symbols) - 6, len(tinted)
    for s in symbols:
        assert len(re.findall(r"[Mm]", re.sub(r'<g [^>]*>.*?</g>', "", s))) <= 12, s[:60]   # เส้นแยกไม่เกิน 12 ชิ้นต่อไอคอน
