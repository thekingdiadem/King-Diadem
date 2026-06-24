# MODELS/choice-balance-model.md — KING DIADEM
# Micro-level: วัด balance ของ action เดียวต่อ choice ที่เหลือ
# Fail less. Harm less. Restore more.

## CHOICE BALANCE MODEL
**Scope: Individual Action Level — ทุกการกระทำเดียว**

---

### Purpose

วัดว่า action หนึ่งๆ เพิ่มหรือลด Choice ของมนุษย์
ไม่ใช่การห้าม — แต่คือการทำให้มองเห็นก่อนตัดสินใจ

---

### Core Variables

| Variable | คำอธิบาย |
|----------|----------|
| `Choice(t)` | จำนวนทางเลือกที่มีอยู่จริงในเวลา t |
| `Resource(t)` | ทรัพยากรที่เข้าถึงได้ (เงิน เวลา สุขภาพ) |
| `Entropy(t)` | ความเสื่อมจากการกระทำนั้นๆ |
| `Balance(t)` | action ที่ชดเชย entropy กลับมา |

---

### Core Equation

```
Choice(t+Δ) = Choice(t) + Balance(t) − Entropy(t)
```

---

### Decision Rule

```
Balance(t) ≥ Entropy(t)  →  Choice คงที่หรือเพิ่ม   ✓
Balance(t) < Entropy(t)  →  Choice ลด              ⚠
Choice(t+Δ) → 0          →  SYSTEM_PAUSE           STOP
```

---

### Application Example

**Action:** กินอาหารแคลอรีสูง
- Entropy เพิ่ม: สุขภาพระยะยาวลด
- Balance ที่ชดเชยได้: เดิน / ดื่มน้ำ / ปรับสัดส่วน

ถ้า Balance ≥ Entropy → Choice คงอยู่ได้

---

### FATE™ Audit

```
model:     choice-balance
scope:     individual_action
equation:  Choice(t+Δ) = Choice(t) + Balance(t) - Entropy(t)
trigger:   Choice(t+Δ) <= 0 → SYSTEM_PAUSE
fate_lock: Fail less. Harm less. Restore more.
```
