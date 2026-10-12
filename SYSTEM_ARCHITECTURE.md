# KING DIADEM — System Architecture

สร้างโดย นิธิกร บุญสร้าง | FATE™ v1.0 | Deterministic Logic Kernel

---

> แผนผังแบบโต้ตอบได้ (ทุกไฟล์ + การเชื่อมต่อจริง) อยู่ที่หน้าเว็บ **`/architecture`** (`static/architecture.html`)
> ข้อมูลไฟล์และเส้นเชื่อมสร้างจาก repo ด้วย `scripts/build_system_map.py` → `static/system_map.json`

**รูปแบบ:** layered monolith — FastAPI ตัวเดียว (`app.py`, gunicorn 1 worker บน Render, SQLite บนดิสก์ถาวร)
ตรรกะของระบบประกบ AI ไว้ทั้งก่อนและหลัง (kernel sandwich) · AI เป็นทางเลือก — ไม่มี AI ก็ตอบจากสมการได้

```
Human Input — static/index.html (แอปหน้าเดียว)
    │  POST /run
    ▼
ประตูหน้า — app.py · DATABASE/db.py
(ความยาว · rate limit · โควตาฟรี 20/วัน → เครดิต → Premium)
    │
    ▼
อ่านสัญญาณ — ENGINE/human_engine.py · AI/intent_engine.py · ENGINE/risk_engine.py
             core/kernel_voice.py (assess) · core/thai_signals.py · core/lang_signals.py
    │
    ▼
ใส่บริบท — core/king_diadem_core.py · core/system_orchestrator.py · core/engine_bridge.py
           (ปฏิจจสมุปบาท · Cosmic Latte · Living Water · นิทาน · ทางออก · ตัวเลขหนี้/เวลา/ทรัพยากร
            · กำไร/margin ของร้าน — DOMAINS/business_engine.py)
    │
    ▼
ตรวจความเชื่อ — AI_KERNEL/belief_core.py (ไม่ผ่าน → SYSTEM_PAUSE)
    │
    ▼
เครื่องยนต์ตัดสินใจ — ENGINE/decision_engine.py → ENGINE/pattern_engine.py → core/emptiness_guard.py
                      → ENGINE/engine_router.py (ปฏิจจสมุปบาท → ความเสี่ยง → สภา 6 เสียง → จำลอง → กลยุทธ์ → ทางรอด)
    │
    ▼
เสียง — core/llm_gemini.py (Gemini) ── ล้ม/ไม่มี key ──► core/kernel_voice.py (คำตอบจากสมการ)
    │
    ▼
ประตูหลัง — ทางเลือก ≤ 3 (มาตรา 11) · core/cosmic_latte_canon.py · AI_KERNEL/belief_core.py (enforce)
    │
    ▼
บันทึก — AI/civilization_engine.py (ไม่มีข้อความ) · AI/freedom_signal.py · report_engine.py (/report/<id>) · DATABASE/db.py
    │
    ▼
Human Action (มนุษย์ตัดสินใจขั้นสุดท้ายเสมอ)
```

ตัววัดโหลด `SECURITY/survival_mode.py` (ASGI middleware รอบ /run /simulate /analyze-image) — วัดอย่างเดียว ไม่บล็อกใคร · ดูได้ที่ `/health` → `load`

---

## Governance Layers

```
Layer 0   Reality Base      — ความจริงที่เปลี่ยนไม่ได้
Layer 1   Humility Gate     — ปิดอัตตาก่อนตัดสินใจ
Layer 2   Clean Governance  — อธิบายได้ใน 2 นาที
Layer 3   Survival Triad    — ชัดเจน · วิธีการ · ชุมชน
Layer E0  DriftZero         — วัด drift รายวัน ไม่ใช่แค่กำไร
Layer E2  Waterline         — Choice(t) ≥ 1 → collapse = False
Layer E3  Stabilize First   — นิ่งก่อนค่อยพัฒนา
```

---

## Tech Stack

```
Backend    FastAPI · Python · Gunicorn
AI         Gemini 2.0 Flash Lite (free tier · key rotation)
Database   SQLite (DATABASE/db.py)
Auth       Google OAuth · Authlib · Session Cookie
Payment    Stripe
Frontend   Vanilla JS · Canvas API · PWA
Deploy     Render.com (free tier)
```

---

## Core Law

```python
if Choice(t) >= 1:
    collapse = False

# ระบบใดที่ทำให้ทางเลือกของมนุษย์ = 0
# ระบบนั้นล้มเหลว
```

**Fail Less · Harm Less · Restore Choice**
