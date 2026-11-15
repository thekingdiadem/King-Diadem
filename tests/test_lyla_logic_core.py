"""LYLA LOGIC CORE (KERNEL/lyla-logic-core.md) — ทุกแกนมีโค้ดที่ทำงานจริง ไม่ใช่แค่เอกสาร"""
import pathlib
import pytest
from core.kernel_voice import compose

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_core_document_kept_intact():
    md = (ROOT / "KERNEL" / "lyla-logic-core.md").read_text(encoding="utf-8")
    for k in ("Gentleness precedes correctness", "AXIS" if "AXIS" in md else "Axis", "Exit", "Authority Check",
              "Survival Floor", "Change must be announced", "ไม่มีใครลบได้"):
        assert k in md, k


@pytest.mark.parametrize("q,must", [
    ("อยากลาออก แต่บริษัทบอกว่าถ้าลาออกต้องจ่ายค่าปรับ 100,000", "สิทธิ์"),                       # Axis 3
    ("อยากออกจากกลุ่มขายตรง แต่เขาบอกว่าถ้าออกจะเสียเงินที่ลงไปทั้งหมด", "ออกจากธุรกิจขายตรงได้เสมอ"),  # Axis 3
    ("อยากออกจากบ้านเช่า แต่เจ้าของยึดเงินประกันและขู่ฟ้อง", "7 วัน"),                          # Axis 3
    ("หัวหน้าบอกว่าห้ามปฏิเสธงานนอกเวลา ไม่งั้นโดนไล่ออก", "ความยินยอม"),                       # Axis 4
    ("พ่อแม่บอกว่าถ้าไม่แต่งงานกับคนที่เลือกให้จะตัดออกจากกองมรดก", "ตัดสิทธิ์ปฏิเสธ"),            # Axis 4
    ("my boss says I cannot refuse overtime or I will be fired", "consent"),                      # Axis 4
])
def test_exit_and_authority_axes(q, must):
    out = compose(q, footer=False)
    assert must in out, out[:200]
    assert out.count("\n1) ") + out.count("\n2) ") >= 2                                             # Axis 1: มีทางเลือก


def test_mode_change_is_announced():
    assert "ไม่ได้ใช้ AI" in compose("หัวหน้าบอกว่าห้ามปฏิเสธงานนอกเวลา ไม่งั้นโดนไล่ออก")
