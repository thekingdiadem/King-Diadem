"""docs/CPS.md (Choice Preservation System) ล็อกด้วย SHA-256 — แก้แม้ตัวอักษรเดียว เทสต์นี้จะล้ม
กฎ hash (เขียนไว้ที่หัวเอกสาร): UTF-8 · ขึ้นบรรทัดแบบ LF · ตัดบรรทัดที่ขึ้นต้นด้วย "SHA-256:" ออกก่อนคำนวณ
ตรวจเองได้:  grep -v '^SHA-256:' docs/CPS.md | sha256sum
ถ้าตั้งใจแก้เอกสาร: คำนวณ hash ใหม่แล้วใส่ในบรรทัด SHA-256: (และบอกเหตุผลใน commit)

หลักใน CPS ข้อ 0 (O ≥ 1) ถูกตรวจในโค้ดจริงที่ tests/test_choice_invariant.py
"""
import hashlib
import re
from pathlib import Path

DOC = Path(__file__).resolve().parent.parent / "docs" / "CPS.md"


def test_cps_text_matches_its_own_hash():
    raw = DOC.read_bytes()
    assert b"\r\n" not in raw, "ต้องขึ้นบรรทัดแบบ LF"
    text = raw.decode("utf-8")
    stated = re.search(r"^SHA-256: ([0-9a-f]{64})$", text, re.M)
    assert stated, "ไม่มีบรรทัด SHA-256:"
    body = "".join(line for line in text.splitlines(keepends=True) if not line.startswith("SHA-256:"))
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() == stated.group(1), "CPS.md ถูกแก้ แต่ hash ไม่ได้อัปเดต"


def test_cps_keeps_its_core_line():
    assert "    O ≥ 1\n" in DOC.read_text(encoding="utf-8")
