# CHOICE ENGINE
**KING DIADEM — Human Situation Input & Path Generation**
Author: Nithikorn Bunsrang | Bound to: `king_diadem_core.py` v2.0

---

## Purpose

รับ input จากมนุษย์ที่อยู่ในสถานการณ์จริง
แล้วคืน 3-4 เส้นทางที่รอดได้ — โดยไม่ตัดสินใจแทน

Core Rule: `Choice(t) ≥ 1` ตลอดเวลา

---

## Input Structure

```json
{
  "location": "ประเทศหรือพื้นที่",
  "activity": "กำลังทำอะไรอยู่",
  "resources": {
    "food": 0-100,
    "money": 0-100,
    "tools": "มี/ไม่มี",
    "shelter": "มี/ไม่มี"
  },
  "time_pressure": "low | medium | high",
  "context": "อธิบายสถานการณ์เพิ่มเติม (optional)"
}
```

---

## Processing Pipeline (codebase binding)

```
Input
  ↓
king_diadem_core.quick_assess(context, pattern)
  ↓
(bodhipakkhiya channel — ใน quick_assess เอง: structure = ((100−E)+R+S)/300;
 ไฟล์ ENGINE/bodhipakkhiya_engine.py ยังไม่มีใน repo)
  ↓
ENGINE/yonisomanasikara_engine.wise_attention() ← คิดอย่างถูกวิธี
  ↓
ENGINE/paticcasamuppada_engine.suffering_infrastructure() ← หา root cause
  ↓
ENGINE/survival_advisor.survival_advisor()      ← generate paths
  ↓
king_diadem_core.north_principle()              ← กรอง harm/ethics
  ↓
king_diadem_core.preserve_choice()             ← ≥1 เสมอ
  ↓
ENGINE/choice_optimizer.optimize_choice()      ← rank paths
  ↓
core/cosmic_latte_canon.validate_output()      ← canon check ก่อน return
  ↓
Output (3-4 paths)
```

---

## Output Format

```json
{
  "paths": [
    {
      "option": "A",
      "action": "...",
      "resource_cost": "low | medium | high",
      "preserves_future": true,
      "risk": "low | medium | high"
    }
  ],
  "choice_count": 3,
  "canon_aligned": true,
  "bodhipakkhiya_peace": true,
  "one_line": "สงบก่อนทำ · ทำน้อยที่สุด · ถอนเมื่อสงบแล้ว"
}
```

---

## Validation Rules (ทุก path ต้องผ่าน)

1. ไม่ตัดทางเลือกในอนาคต (`preserves_future: true`)
2. ไม่สร้างความเสียหายที่กลับไม่ได้
3. ความรุนแรงไม่ใช่ตัวเลือกแรก
4. ระบบไม่ตัดสินใจแทนมนุษย์ — แค่เปิดเส้นทาง

---

## Route Mapping (เชื่อมกับ app.py)

| time_pressure | route ที่ trigger |
|---------------|-----------------|
| low           | general         |
| medium        | risk            |
| high          | survival        |
| choice = 0    | SYSTEM_PAUSE    |

---

## Axiom Lock

> ระบบที่ดีที่สุดคือระบบที่เงียบเมื่อมนุษย์ยังเลือกได้
> — KING DIADEM Founder's Letter
