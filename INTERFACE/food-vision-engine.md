# FOOD VISION ENGINE
**KING DIADEM — AI Food Balance System**
Author: Nithikorn Bunsrang | Bound to: `app.py` `/analyze-image` + `king_diadem_core.py`

---

## Purpose

ถ่ายภาพอาหาร → AI ประเมินแคลอรี่โดยประมาณ
→ เสนอทางสมดุล **โดยไม่ตัดทางเลือกอาหาร**

Core Rule: ระบบ **เพิ่ม choice** ไม่ใช่ **ลด choice**

---

## Principle

ไม่มีการประเมินแคลอรี่ที่แม่นยำ 100% —
portion, วัตถุดิบ, วิธีปรุง ต่างกันทุกครั้ง

ดังนั้นระบบใช้ **approximate estimation** ไม่ใช่ false precision

---

## Pipeline (codebase binding)

```
User Photo
  ↓
app.py /analyze-image
  ↓
core/llm_gemini.py (Gemini Vision)
  ↓
[Food recognition + portion estimation + calorie estimate]
  ↓
king_diadem_core.quick_assess(context, pattern)
  ↓ (ตรวจว่า response สมดุลไหม — ไม่กดดันผู้ใช้)
core/cosmic_latte_canon.evaluate_task()
  ↓
Output: balance options (ไม่ใช่ restriction)
```

---

## Input

```
POST /analyze-image
Content-Type: multipart/form-data
file: <image>
```

---

## Output Format

```json
{
  "detected_food": "ข้าวผัดหมู",
  "estimated_calories": "~700 kcal",
  "confidence": "approximate",
  "balance_options": [
    {
      "option": "A",
      "action": "ดื่มน้ำเพิ่ม 2 แก้วหลังอาหาร",
      "effort": "low"
    },
    {
      "option": "B",
      "action": "เดินหลังอาหาร 20-30 นาที",
      "effort": "medium"
    },
    {
      "option": "C",
      "action": "มื้อถัดไปเพิ่มผักหรือไฟเบอร์",
      "effort": "low"
    }
  ],
  "canon_aligned": true,
  "note": "ตัวเลขเป็นการประมาณ ไม่ใช่ค่าแน่นอน"
}
```

---

## Hard Rules (ห้าม override)

ระบบต้องไม่:

1. ลบอาหารที่ผู้ใช้ชอบออกจาก option
2. ตำหนิหรือลงโทษผู้ใช้
3. บังคับให้ลดอาหารแบบ restrictive
4. ทำให้ `choice_preserved = false`

ถ้า output ละเมิดข้อใดข้อหนึ่ง
→ `cosmic_latte_canon.evaluate_task()` จะ flag `canon_aligned: false`
→ ระบบต้อง regenerate

---

## Emotion Check

ถ้าผู้ใช้แสดง emotion เชิงลบเกี่ยวกับร่างกาย:
→ `llm_gemini.py` switch เป็น `LYLA_SYSTEM` mode อัตโนมัติ
→ รับรู้ก่อน อย่าเพิ่งวิเคราะห์

---

## Axiom Lock

> ระบบมีไว้ปกป้องมนุษย์
> ระบบใดที่ใช้ให้มนุษย์มาปกป้องโครงสร้าง สิ่งนั้นยังผิดอยู่
> — UNIVERSAL FATE-AXIS
