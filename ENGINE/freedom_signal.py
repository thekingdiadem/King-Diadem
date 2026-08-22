# ENGINE/freedom_signal.py
"""
KING DIADEM — Freedom / Wisdom Signal
======================================
สมการหลัก (พี่คิง, 2026-07-04):

    Wisdom = Outcome Usefully / Spent Energy

ของเดิมมีแค่ตัวนับคำถาม (_question_count) ซึ่งวัดได้แค่ "ถามไปกี่ครั้ง"
ไม่ได้วัด "ถามแล้วได้อะไรจริง เทียบกับเสียไปเท่าไร" — โมดูลนี้แก้ตรงนั้น
โดยยังคง backward-compatible กับของเดิม 100% (record_question / freedom_index
เรียกได้เหมือนเดิมทุกที่ที่เคย import ไปใช้)

Deterministic: ไม่มี random, ไม่มี time-based decay ที่ไม่ระบุ seed —
input เดียวกัน -> output เดียวกันเสมอ ตาม logic kernel ของ King Diadem
"""

_question_count = 0

# ---- Wisdom ledger: บันทึกทุก "ผลลัพธ์ที่ใช้ได้จริง" กับ "พลังงานที่เสียไป" ----
_outcome_total = 0.0   # ผลลัพธ์ที่ใช้งานได้จริงสะสม (หน่วยพี่คิงกำหนดเอง เช่น บาท, งานที่เสร็จ, ปัญหาที่แก้)
_energy_total = 0.0    # พลังงานที่เสียไปสะสม (เวลา/นาที, แรง, เงินต้นทุน — พี่คิงเลือกหน่วยเดียวแล้วใช้สม่ำเสมอ)
_ledger = []           # ประวัติทุกรายการ เพื่อ audit ย้อนหลังได้ (deterministic replay)


def record_question():
    """ของเดิม: นับจำนวนคำถาม/รอบที่ถามระบบ ยังใช้ได้เหมือนเดิม"""
    global _question_count
    _question_count += 1


def freedom_index() -> int:
    """ของเดิม: จำนวนคำถามสะสม"""
    return _question_count


def record_outcome(value: float, label: str = "") -> None:
    """
    บันทึกผลลัพธ์ที่ใช้ได้จริง 1 รายการ
    value ต้อง >= 0 (ผลลัพธ์ติดลบไม่ควรมี — ถ้ามีความเสียหายให้บันทึกเป็น energy แทน)
    """
    global _outcome_total
    if value < 0:
        raise ValueError("record_outcome: value ต้องไม่ติดลบ (ความเสียหายให้ใช้ record_energy)")
    _outcome_total += value
    _ledger.append({"type": "outcome", "value": value, "label": label})


def record_energy(cost: float, label: str = "") -> None:
    """
    บันทึกพลังงาน/ต้นทุนที่เสียไป 1 รายการ (เวลา, เงิน, แรง, ความเสียหาย)
    cost ต้อง > 0
    """
    global _energy_total
    if cost <= 0:
        raise ValueError("record_energy: cost ต้องมากกว่า 0")
    _energy_total += cost
    _ledger.append({"type": "energy", "value": cost, "label": label})


def wisdom_index() -> float:
    """
    Wisdom = Outcome Usefully / Spent Energy

    ถ้ายังไม่เคยเสียพลังงานเลย (energy_total == 0) คืนค่า 0.0
    เพื่อกันหาร 0 — ไม่ใช่ inf เพราะ "ยังไม่เกิดเหตุการณ์" ไม่ใช่ "ประสิทธิภาพไม่จำกัด"
    """
    if _energy_total == 0:
        return 0.0
    return _outcome_total / _energy_total


def snapshot() -> dict:
    """สรุปสถานะทั้งหมด ณ ตอนนี้ — ใช้โชว์บนหน้า dashboard หรือ log ได้ตรงๆ"""
    return {
        "question_count": _question_count,
        "outcome_total": _outcome_total,
        "energy_total": _energy_total,
        "wisdom_index": wisdom_index(),
        "entries": len(_ledger),
    }


def reset() -> None:
    """ล้างค่าทั้งหมด (ใช้ตอนเริ่มรอบวัดใหม่ เช่น เริ่มกะทำงานใหม่)"""
    global _question_count, _outcome_total, _energy_total, _ledger
    _question_count = 0
    _outcome_total = 0.0
    _energy_total = 0.0
    _ledger = []


if __name__ == "__main__":
    # ตัวอย่าง: กะทำงานส่งของวันนี้ — บันทึกงานที่ส่งสำเร็จ (outcome) กับเวลาที่เสียไป (energy)
    record_energy(43, label="เวลาขับรถเฉลี่ยต่องาน (นาที) x1")
    record_outcome(35, label="ค่าส่งงานที่ 1 (บาท)")
    record_question()
    print(snapshot())
