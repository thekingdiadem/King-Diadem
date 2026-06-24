# MODELS/choice-collapse-model.md — KING DIADEM
# System-level: โมเดล Drift สะสม → Collapse ระดับระบบ
# Author: Nithikorn Bunsrang
# Fail less. Harm less. Restore more.

## CHOICE COLLAPSE MODEL
**Scope: System Level — Drift สะสมระยะยาว**

---

### Purpose

อธิบายกลไกที่ระบบล่มสลายจาก Drift เล็กน้อยสะสม ไม่ใช่จากเหตุการณ์ครั้งเดียว
ต่างจาก Balance Model ที่ดู action เดียว — Collapse Model ดู trajectory ของทั้งระบบ

---

### Core Variables

| Variable | คำอธิบาย |
|----------|----------|
| `Choice(t)` | จำนวน viable decisions ที่ระบบมีในเวลา t |
| `Drift(t)` | การเสื่อมเชิงโครงสร้างสะสม (≥ 0) |
| `Entropy(t)` | ความผิดปกติตามธรรมชาติ + การสูญเสียทรัพยากร (≥ 0) |
| `Intervention(t)` | action ที่ดึง choice กลับมา (≥ 0) |
| `Resources(t)` | พลังงาน วัสดุ โครงสร้าง capacity ของมนุษย์ |

---

### System Evolution Equation

```
Choice(t+Δ) = Choice(t) - Drift(t) - Entropy(t) + Intervention(t)
```

**ต่างจาก Balance Model:** มี `Drift(t)` แยกชัด = ความเสื่อมเชิงโครงสร้างที่สะสม
ไม่ใช่แค่ entropy จาก action เดียว

---

### Drift Accumulation (DHD)

```
Drift(t) = Σ Daily Harm Delta (DHD)
```

DHD วัดการเสื่อมเล็กน้อยรายวัน:
- โครงสร้างพื้นฐานเสื่อม
- ภาระหนี้สินเพิ่ม
- ความเครียดสะสม
- ทรัพยากรลด
- Governance ล้มเหลว

---

### Collapse Threshold

```
if Choice(t+Δ) → 0:  System State = COLLAPSE_RISK
if Choice(t) = 0:    collapse irreversible
```

---

### Early Warning Condition

```
if Choice(t+Δ) < Safe_Threshold:
    → Trigger Early Warning
    → Generate Intervention options
```

`Safe_Threshold` = จำนวน options ขั้นต่ำที่ระบบต้องมีเพื่อ recover ได้

---

### Recovery Pathway

```
if Intervention(t) > Drift(t):
    Choice(t) stabilizes or increases
```

---

### FATE™ Audit

```
model:          choice-collapse
scope:          system_level
drift_source:   DHD daily accumulation
equation:       Choice(t+Δ) = Choice(t) - Drift(t) - Entropy(t) + Intervention(t)
collapse_at:    Choice(t) = 0  →  irreversible
early_warn_at:  Choice(t+Δ) < Safe_Threshold
fate_lock:      Fail less. Harm less. Restore more.
```
