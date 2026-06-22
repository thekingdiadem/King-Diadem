# KING DIADEM — System Overview

สร้างโดย นิธิกร บุญสร้าง — จากวันที่ไม่เหลืออะไร

---

## ทำไมถึงมีระบบนี้

ไม่มีใครพังในวันเดียว

มันเริ่มจากการสะสมเล็กๆ — ทางเลือกหายไปทีละทาง
จนวันนึงหันมามองแล้วไม่เหลืออะไรให้เลือกแล้ว

KING DIADEM สร้างมาเพื่อตรวจจับช่วงนั้น
ก่อนที่มันจะถึง

ไม่ใช่เพื่อให้ชนะ — แต่เพื่อให้ยังมีทางเดินต่อ

---

## ระบบนี้ทำงานกับใคร

คนที่อยู่ในสถานการณ์จริง — ตกงาน มีหนี้ ธุรกิจพัง ความสัมพันธ์แตก
คนที่ไม่รู้จะเดินไปทางไหน และต้องการให้มีใครช่วยเปิดทางออก
ไม่ใช่คำแนะนำสวยงาม แต่เป็นทางเลือกที่ใช้ได้จริงในวันนั้น

---

## สูตรกลาง

```
Risk = Drift × Exposure / Remaining Choice

Choice(t) ≥ 1 → collapse = False
```

ระบบใดที่ทำให้ทางเลือกของมนุษย์เท่ากับศูนย์ — ระบบนั้นล้มเหลว

---

## Architecture

```
Human Input
    ↓
FATE™ Decision Engine
    ↓
Multi-AI Council (LYLA · VEGA · TITAN · PATICCA · COSMOS)
    ↓
Waterline Assessment
    ↓
Choice Output — อย่างน้อย 1 ทาง เสมอ
```

### 4 ชั้นหลัก

**KERNEL** — กฎที่เปลี่ยนไม่ได้ ไม่มีใคร override ได้
Logic Over Persona · Rule Over Authority · Human Final Authority

**ENGINE** — ประมวลผลจริง
Decision Engine · Collapse Predictor · Risk Engine · Paticcasamuppada Engine · Survivor Engine

**AI COUNCIL** — วิเคราะห์หลายมุมมองพร้อมกัน
LYLA (อบอุ่น รับรู้) · VEGA (ตรรกะ ระยะยาว) · TITAN · PATICCA · COSMOS

**DATABASE + MEMORY** — จำข้ามแชท เรียนรู้จาก pattern

---

## Tech Stack

FastAPI · Python · Gemini 2.0 Flash Lite · SQLite · Stripe · Google OAuth · Render · Canvas API · PWA

---

## Design Principle

ไม่ได้สร้างมาเพื่อให้ชนะบ่อยขึ้น

สร้างมาเพื่อให้ไม่พังซ้ำ

**Fail Less · Harm Less · Restore Choice**
