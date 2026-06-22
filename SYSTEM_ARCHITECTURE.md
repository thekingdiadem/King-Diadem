# KING DIADEM — System Architecture

สร้างโดย นิธิกร บุญสร้าง | FATE™ v1.0 | Deterministic Logic Kernel

---

```
Human Input
    │
    ▼
Galaxy Interface — static/index.html
(Canvas Solar System · LYLA/VEGA personas · Mobile PWA)
    │
    ▼
API Layer — app.py (FastAPI)
(Google OAuth · Session · Cookie · Rate Limit)
    │
    ▼
FATE™ Decision Engine — ENGINE/decision_engine.py
(Deterministic Logic · Choice Preservation · Route Detection)
    │
    ▼
Multi-AI Council
────────────────────────────────────────
LYLA ◈  — Warmth · Governance Intelligence
VEGA ◆  — Strategic Analysis · Logic
TITAN   — Risk Assessment · Threat Detection
PATICCA — Dependent Origination · Root Cause
COSMOS  — System Integrity · Final Arbiter
    │
    ▼
Intelligence Layer
────────────────────────────────────────
ENGINE/human_engine.py        — Human State Analysis
ENGINE/paticcasamuppada_engine.py — Causal Chain Mapping
ENGINE/risk_engine.py         — Risk Scoring
ENGINE/collapse_predictor.py  — Collapse Probability
ENGINE/realhuman_survivorengine.py — Waterline Assessment
    │
    ▼
Simulation Layer
────────────────────────────────────────
ENGINE/simulation_engine.py   — Future Path Simulation
ENGINE/consensus_engine.py    — Council Consensus
ENGINE/universal_engine.py    — Cross-Engine Enrichment
    │
    ▼
Memory & Persistence
────────────────────────────────────────
DATABASE/db.py                — SQLite · User · Decision Log
DATABASE/db.py                — chat_memory · auto_extract_memory
report_engine.py              — FATE™ Decision Report URL
    │
    ▼
Decision Output
────────────────────────────────────────
ai_response     — LYLA/VEGA natural language
route           — GENERAL · RISK · SURVIVAL · COLLAPSE · CIVIL · VEGA
risk_score      — 0–100
waterline       — entropy · stability · resource
consensus       — Council verdict
report_url      — Shareable FATE™ audit link
    │
    ▼
Human Action
(มนุษย์ตัดสินใจขั้นสุดท้ายเสมอ)
```

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
