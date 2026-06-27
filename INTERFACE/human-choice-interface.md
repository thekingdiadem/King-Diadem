# HUMAN CHOICE INTERFACE
**KING DIADEM — สะพานระหว่างมนุษย์กับระบบตัดสินใจ**
Author: Nithikorn Bunsrang | Bound to: `app.py /run` + `king_diadem_core.py` v2.0

---

## Purpose

ให้มนุษย์อธิบายสถานการณ์ของตัวเองในภาษาธรรมชาติ
แล้วได้รับ 3-4 เส้นทางที่รอดได้ — ไม่ใช่คำสั่ง

**อธิปไตยของการเลือกเป็นของมนุษย์เสมอ**

---

## Input (ภาษาธรรมชาติ — ไม่ต้องกรอก form)

ผู้ใช้พิมพ์ใน chat เช่น:
```
"ตอนนี้ตกงาน มีเงินเหลือ 3,000 บาท มีลูก 1 คน
ไม่รู้จะทำยังไงดี"
```

ระบบจะ extract เอง:

| field | extracted |
|-------|-----------|
| resource.money | ต่ำ (3,000 บาท) |
| resource.food | unknown → ถามเพิ่ม |
| constraint | มีลูก = dependant |
| emotion | เครียด/ไม่รู้จะทำอะไร |
| urgency | medium-high |

---

## Processing (codebase binding)

```
User message → app.py /run
  ↓
ENGINE/human_engine.analyze_human()        ← extract human state
  ↓
king_diadem_core.quick_assess()            ← bodhipakkhiya channel
  ↓
core/llm_gemini.py LYLA_SYSTEM             ← รับรู้ก่อน ค่อยวิเคราะห์
  ↓
ENGINE/survival_advisor.survival_advisor() ← generate paths
  ↓
king_diadem_core.north_principle()         ← กรอง
  ↓
king_diadem_core.preserve_choice()         ← ≥1 เสมอ
  ↓
core/cosmic_latte_canon.evaluate_task()    ← canon gate ก่อน return
  ↓
Response to user (LYLA tone — เข้าอกเข้าใจ)
```

---

## Response Rules (LYLA Warmth Axioms)

1. **รับรู้ก่อนเสมอ** — 1-2 ประโยคก่อน solution
2. **ไม่เกิน 3 ตัวเลือก** ต่อ response (Article 11)
3. **ไม่ตัดสิน** ไม่ว่าสถานการณ์จะเป็นอะไร
4. **ไม่สั่ง** — เสนอเส้นทาง ไม่บังคับ
5. **ถ้า emotion สูง** → switch CRISIS_SYSTEM อัตโนมัติ

---

## Output ที่ผู้ใช้เห็น

```
ฉันได้ยินที่คุณพูดนะคะ — มันหนักจริงๆ 🤍

ลองดูสามทางนี้ก่อนได้เลยค่ะ:

1) วันนี้ก่อนเลย — เขียนรายจ่ายจำเป็น 30 วัน
   แค่ตัวเลข ยังไม่ต้องตัดสินใจอะไร

2) งานชั่วคราวที่เริ่มได้เร็ว — Shopee Food, Grab
   เปิด-ปิดได้เองตามเวลาที่มี

3) โทรหา 1506 กรมจัดหางาน
   ลงทะเบียนว่างงานก่อน เพื่อรักษาสิทธิ์ประกันสังคม

— LYLA ◈
```

---

## Validation Gate

ก่อน response ทุกครั้ง ระบบตรวจ:

```python
canon_check = evaluate_task({
    "description": response_text,
    "has_choice": len(paths) >= 1,
    "has_exit": True,
})
# ถ้า canon_aligned = False → regenerate
```

---

## Axiom Lock

> ชีวิตไม่ควรถูกบีบจนเหลือทางเดียว
> — KING DIADEM Founder's Letter, Principle 1
