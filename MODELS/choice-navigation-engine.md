# MODELS/choice-navigation-engine.md — KING DIADEM
# Decision Support: สร้าง pathways จริงจาก context ของผู้ใช้
# Author: Nithikorn Bunsrang
# Fail less. Harm less. Restore more.

## CHOICE NAVIGATION ENGINE
**Scope: User-Facing Decision Support — สร้าง options จาก context จริง**

---

### Purpose

ต่างจาก Balance/Collapse Model ที่เป็น theoretical —
Navigation Engine คือ runtime layer ที่รับ input จากผู้ใช้จริง แล้วสร้างทางเลือกที่ทำได้ทันที

---

### System Input

```
location:        ประเทศ / พื้นที่
activity:        กิจกรรมปัจจุบัน
resources:       อาหาร น้ำ พลังงาน เงิน เครื่องมือ เวลา
risk_level:      self-assess 1–10
entropy_score:   ระดับความเครียด/ความไม่แน่นอน
```

ตัวอย่าง:
```
country:   Thailand
resources: ข้าว, น้ำ, โทรศัพท์
money:     ต่ำ
energy:    กลาง
```

---

### Option Safety Rule

แต่ละ option ต้องผ่านเงื่อนไข:

```
Choice(t+1) ≥ Choice(t)
```

Options ที่ลด long-term choices → rejected ก่อน output

---

### Output Structure (3–4 options เสมอ)

```
Option 1 [lowest risk]:   xxxxxxx  →  consequence
Option 2 [medium]:        xxxxxxx  →  consequence
Option 3 [higher action]: xxxxxxx  →  consequence
Option 4 [fallback]:      stabilize / wait / observe
```

กฎ:
- ทุก option ต้อง survivable
- ไม่มี option ใดถูกระบุว่า "ถูก" หรือ "ผิด"
- มนุษย์เลือกเองเสมอ — Human Final Authority

---

### Ethical Constraint

```
Violence priority:  last resort เท่านั้น
Preferred paths:    cooperation → resource sharing → conflict avoidance
Domination:         rejected
```

---

### Integration with Other Models

```
Balance Model   → ประเมินว่า option แต่ละตัวเพิ่ม/ลด Choice หรือไม่
Collapse Model  → เช็คว่า current state ใกล้ collapse threshold ไหม
Navigation Engine → สร้าง options จาก context จริง แล้ว output ให้มนุษย์
```

---

### FATE™ Audit

```
model:          choice-navigation
scope:          user_facing_runtime
input:          real_world_context
output:         3-4 viable options, sorted risk ASC
safety_rule:    Choice(t+1) >= Choice(t) per option
human_authority: final decision always with human
fate_lock:      Fail less. Harm less. Restore more.
```
