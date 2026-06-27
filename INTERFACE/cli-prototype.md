# CLI PROTOTYPE
**KING DIADEM — Command Line Interface**
Author: Nithikorn Bunsrang | Bound to: `king_diadem_core.py` v2.0

---

## Purpose

Interface บรรทัดคำสั่งสำหรับทดสอบ engine โดยตรง
ไม่ต้องรอ UI — ใช้ mobile หรือ terminal ก็ได้

---

## Run

```bash
python -m ENGINE.cli --input "สถานการณ์ของฉัน" --route survival
```

หรือ interactive mode:

```bash
python -m ENGINE.cli --interactive
```

---

## Interactive Flow

```
KING DIADEM CLI v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

คุณอยู่ที่ไหน? (ประเทศ/พื้นที่)
> ไทย กรุงเทพ

กำลังทำอะไรอยู่?
> หางานอยู่ ตกงานมา 2 เดือน

ทรัพยากรที่มี (food 0-100 / money 0-100)
> food: 40 / money: 20

ความเร่งด่วน (low/medium/high)
> high

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[BODHIPAKKHIYA] ตรวจโครงสร้าง...
[YONISO] เลือกวิธีคิด: อริยสัจ 4
[PATTICCA] ต้นเหตุ: resource depletion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

เส้นทางที่ระบบพบ:

A) ลดรายจ่ายจำเป็นให้เหลือ 3 อย่างใน 30 วัน
B) ติดต่อคนรู้จัก 1 คนที่ไม่ใช่ครอบครัว บอกตรงๆ
C) หางานชั่วคราว (Shopee Food / Grab) เพื่อ cashflow ระยะสั้น

Choice preserved: 3 / Canon aligned: ✓
```

---

## Engine Calls (ลำดับจริง)

```python
from king_diadem_core import quick_assess, king_diadem_decision

# 1. quick assess
result = quick_assess(user_input, pattern)

# 2. full decision ถ้าต้องการ
decision = king_diadem_decision(
    location=location,
    lat=lat, lng=lng,
    food=food, money=money, risk=risk,
    context=user_input
)
```

---

## Output Flags

| flag | ความหมาย |
|------|----------|
| `peace: true` | โครงสร้างสงบ พร้อม output |
| `should_pause: true` | มี bias หรือ UAP — ควรทบทวนก่อน |
| `SYSTEM_PAUSE` | Choice = 0 — ระบบหยุด รอทางออก |
| `drift_alert: true` | entropy สูง — เฝ้าระวัง |

---

## Validation Rules

path ที่ valid ต้องผ่าน `north_principle()`:

- `harm_life: false`
- `break_ethics: false`
- `reality_violation: false`

และผ่าน `cosmic_latte_canon.evaluate_task()`:

- `choice_preserved: true`
- `exit_available: true`
- `canon_aligned: true`

---

## Axiom Lock

> ถ้าอธิบายไม่ได้ภายใน 2 นาที = ระบบนั้นใช้ไม่ได้
> — FATE™ Axiom 5
