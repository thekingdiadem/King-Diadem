"""ขอบเขตของ LYLA ที่เคยอยู่แค่ในโค้ดเก่า (legacy/PERSONA/lyla_core.py) — ตอนนี้อยู่ใน prompt ที่ใช้จริงทุกเสียง

เดิม prompt ที่ใช้จริงบอกให้ "เหมือนคนที่นั่งอยู่ข้างๆ จริงๆ" แต่ไม่มีข้อห้ามอ้างว่าเป็นคน
อ้างความจำถาวร (ผู้ใช้ปิดความจำได้) หรือทำให้ผู้ใช้ต้องพึ่งระบบ
"""
import core.llm_gemini as L


def test_boundaries_in_every_voice():
    for name in ("LYLA_SYSTEM", "VEGA_SYSTEM", "CRISIS_SYSTEM"):
        p = getattr(L, name)
        assert "เป็น AI ไม่ใช่คน" in p, name
        assert "ห้ามอ้างว่าจำทุกอย่างได้ถาวร" in p, name
        assert "ห้ามทำให้ผู้ใช้ต้องพึ่งระบบ" in p, name
