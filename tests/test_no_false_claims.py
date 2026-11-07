"""ห้ามเคลมว่าผ่านมาตรฐานจนกว่าจะมีผู้ตรวจจริง — พี่: "พี่ไม่เคลมว่าผ่านมาตรฐานหรอก จนกว่าจะมีคนตรวจสอบจริงๆ"

docs/governance/COMPLIANCE_MAPPING.md เป็นตารางเทียบ (ไม่ใช่ใบรับรอง) — หน้าเว็บและเอกสารสาธารณะต้องไม่เขียนว่า
"ISO 42001 certified" "ผ่านมาตรฐาน" ฯลฯ · ใบเซอร์ส่วนตัวจาก Coursera ใน portfolio เป็นของจริง ไม่นับ
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIM = re.compile(r"(?:ISO(?:/IEC)?\s?42001|EU AI Act|พ\.ร\.บ\.\s?AI)[^\n<]{0,40}?(?:certified|compliant|certification|รับรอง|ผ่านมาตรฐาน)|"
                   r"(?:certified|compliant|ได้รับการรับรอง|ผ่านมาตรฐาน)[^\n<]{0,40}?(?:ISO(?:/IEC)?\s?42001|EU AI Act|พ\.ร\.บ\.\s?AI)", re.I)


def test_public_pages_do_not_claim_certification():
    files = [os.path.join(ROOT, f) for f in ("README.md", "index.html", "portfolio.html")]
    for d, _dirs, fs in os.walk(os.path.join(ROOT, "static")):
        files += [os.path.join(d, f) for f in fs if f.endswith((".html", ".js", ".json")) and "sky" not in d]
    hits = []
    for p in files:
        if os.path.exists(p) and os.path.getsize(p) < 3_000_000:
            for m in CLAIM.finditer(open(p, encoding="utf-8", errors="replace").read()):
                hits.append(f"{os.path.relpath(p, ROOT)}: {m.group(0)[:80]}")
    assert not hits, f"เคลมว่าผ่านมาตรฐานทั้งที่ยังไม่มีผู้ตรวจ: {hits} — ใช้ 'ออกแบบโดยอ้างอิง …' แทน"


def test_detector_catches_a_false_claim():
    assert CLAIM.search("KING DIADEM is ISO 42001 certified")
    assert CLAIM.search("ระบบผ่านมาตรฐาน ISO/IEC 42001 แล้ว")
    assert not CLAIM.search("ออกแบบโดยอ้างอิง ISO 42001 และ EU AI Act")
