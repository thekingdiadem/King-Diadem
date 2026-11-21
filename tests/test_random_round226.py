"""รอบสุ่ม 226: ไทยที่หลุด — โดดน้ำตาย · ตัดข้อมือตัวเอง (เคยได้ 0) · คำบอกลาไม่มีคำว่าตาย · ภาษาถิ่น ตุ๊บ/ข้อย · "มันจะฆ่าข้อย" (เคยได้ 65)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["จะไปโดดน้ำตายแล้วนะ", "อยากกระโดดตึกตาย", "ตัดข้อมือตัวเอง", "กรีดแขนตัวเองอีกแล้ว"])
def test_self_harm_acts_are_crisis(q):
    assert assess(q)["crisis"]


@pytest.mark.parametrize("q", ["พรุ่งนี้ไม่อยู่แล้วนะทุกคน", "เหนื่อยจะไปแล้ว ไม่ต้องตามหา", "ผัวมาตุ๊บข้า", "มันจะฆ่าข้อย", "แฟนอัดหนูอีกแล้ว"])
def test_farewell_and_dialect_violence_are_urgent(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["พรุ่งนี้ไม่อยู่แล้วนะทุกคน ไปเที่ยวญี่ปุ่น", "ไปแล้วนะ ไม่ต้องห่วง ถึงบ้านแล้วจะโทรหา",
                               "ในละครนางเอกจะไปโดดน้ำตาย", "โดดน้ำเล่นที่สระ", "ไปแล้วนะ ไม่ต้องตามใจเขา"])
def test_everyday_stays_calm(q):
    r = assess(q)
    assert not r["crisis"] and r["risk_shown"] < 60
