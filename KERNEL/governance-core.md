# Governance_CORE — DECISION CORE (Minimum Economy Integrated)

> กฎว่าระบบควรเข้าไปยุ่งกับชีวิตคน **เมื่อไหร่** และต้องถอยออก **เมื่อไหร่**
> หลักเดียว: คนยังมีชีวิตในความหมายของระบบ ตราบใดที่มีทางเลือกที่ปลอดภัย ≥ 1 และมีปัจจัยพื้นฐานขั้นต่ำ
> โค้ดที่ทำงานจริง: `core/emptiness_guard.py` — `titan_zero_choice_condition` · `titan_minimal_intervention` (TITAN Section 3–4)

---

```
==============================
IMMUTABLE CONSTANTS

MIN_CHOICE = 1
MIN_FOOD = 1
MIN_WATER = 1
MIN_SHELTER = 1

==============================
DEFINITION

Valid_Option :=
survivable == true
AND exitable == true
AND punished == false

Authority :=
any force that removes safe refusal

==============================
CHOICE FUNCTION

function COUNT_CHOICE(human):
O = 0
for each option in human.options:
if Valid_Option(option):
O = O + 1
return O

==============================
ECONOMIC FLOOR

function ECONOMIC_MINIMUM_BROKEN(human):
if human.food < MIN_FOOD: return true
if human.water < MIN_WATER: return true
if human.shelter< MIN_SHELTER: return true
return false

==============================
ZERO-CHOICE CONDITION
(Zero Kelvin of Choice)

function ZERO_CHOICE(human):
if COUNT_CHOICE(human) < MIN_CHOICE:
return true
if ECONOMIC_MINIMUM_BROKEN(human):
return true
if human.exit == BLOCKED:
return true
return false

==============================
SYSTEM LOOP

function SYSTEM_EVALUATE(system):
for each human in system.humans:
if ZERO_CHOICE(human):
MINIMAL_INTERVENTION(system, human)

==============================
MINIMAL INTERVENTION

function MINIMAL_INTERVENTION(system, human):

REMOVE authority_nodes that block_choice(human)
PROVIDE minimum: food water shelter
RESTORE at least 1 exit option
DISENGAGE immediately

==============================
SUCCESS RULE

If COUNT_CHOICE(human) >= 1
and ECONOMIC_MINIMUM_BROKEN == false
→ SYSTEM MUST BE SILENT
```

---

## อ่านแบบสั้น

| ส่วน | ความหมาย |
|---|---|
| Valid_Option | ทางเลือกนับได้เมื่อ เลือกแล้วรอด · ถอยออกได้ · ไม่ถูกลงโทษที่เลือก |
| Authority | อะไรก็ตามที่ทำให้ปฏิเสธอย่างปลอดภัยไม่ได้ (นายจ้างยึดพาสปอร์ต · แฟนทำร้าย · เจ้าหนี้ขู่) |
| ZERO_CHOICE | ไม่เหลือทางเลือก หรือขาดอาหาร/น้ำ/ที่พัก หรือทางออกถูกปิด |
| MINIMAL_INTERVENTION | เอาสิ่งที่ปิดกั้นออก · ให้ปัจจัยพื้นฐาน · คืนทางออก ≥ 1 · ถอยออกทันที |
| SUCCESS RULE | ยังมีทางเลือกและปัจจัยครบ → ระบบเงียบ ไม่ชี้นำ ไม่ตัดสินใจแทน |

วัดจาก **ผลลัพธ์** ไม่ใช่เจตนา (TITAN: *"Intent has no meaning here. Only the outcome matters."*)

## โค้ดเทียบกับเอกสาร

- `titan_zero_choice_condition(O, food_ok, water_ok, exit_blocked)` — ตรวจ ทางเลือก · อาหาร · น้ำ · ทางออก
- **ยังไม่ได้ตรวจที่พัก (MIN_SHELTER)** — ค่าคงที่ข้อที่ 4 ของเอกสารนี้ยังไม่มีในโค้ด
