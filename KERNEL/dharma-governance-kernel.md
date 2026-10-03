# KING DIADEM — DriftZero Waterline Governance Kernel
**Author:** Nithikorn Bunsrang  
**System:** Early Warning + Governance Logic  
**Bound to:** app.py v4.7 / core/lyla_kernel.py / ENGINE/*  
**Lock:** Fail less. Harm less. Restore more.

---

## 1. System Purpose

Most systems detect failure after it happens.  
KING DIADEM detects failure **before options disappear**.

Core premise:

> When `Choice(t) → 0`, collapse becomes unavoidable.

The system therefore preserves **at least one viable option** at all times.

---

## 2. Collapse Model (Live)

Collapse sequence:

```
Drift Accumulation
      ↓
Choice Reduction          ← DHD tracking (freedom_index)
      ↓
Choice → 0                ← predict_collapse() fires
      ↓
SYSTEM_HALT               ← route = "collapse" | survivor = can_decide=False
```

System interrupts at step 3.  
Never waits for step 4.

---

## 3. Core Equation (Implemented)

```python
# In ENGINE/collapse_predictor.py
if predict_collapse(risk_score)["probability"] > 0.6:
    collapse_ctx = f"[Collapse probability: {prob:.0%}]"
    # injected into LLM prompt before generation
```

```
Choice(t + Δ) → 0  →  early warning fires  →  route escalates
```

---

## 4. Early Warning Mechanism (App Binding)

Three primary variables active in `/run`:

| Variable | Source in app.py |
|----------|-----------------|
| `Time_to_Failure` | `predict_collapse()` probability |
| `Time_to_Intervention` | `assess_risk()` level threshold |
| `Decision_Window` | `survivor_analyze()` can_decide flag |

When Decision_Window → 0:  
→ route forced to "survival" or "collapse"  
→ LLM prompt prepends survivor_ctx  
→ response signed LYLA ◈ or HALT ⬡

---

## 5. Drift Detection — DHD

Daily Harm Delta measured via:

```
freedom_index()         ← AI.freedom_signal
risk_score trend        ← ENGINE/risk_engine.py
collapse_probability    ← ENGINE/collapse_predictor.py
water_stress_index      ← /dashboard endpoint (72.4 current)
```

Tracked drift types:
- Infrastructure: `choice_collapse_risk` in dashboard
- Financial: credit system + Stripe health
- Systemic stress: `entropy` in `_gstate`
- Resource: `resource` in `_gstate`
- Governance: `stability` in `_gstate`

Drift visible in galaxy canvas as planet pulse intensity.

---

## 6. Choice Preservation (Runtime)

```
Life continues while real choices exist.
```

Enforced by:
- Every `/run` response **must** contain ≥1 actionable option
- LYLA kernel blocks responses that reduce to zero choice
- `report_url` always returned — human retains audit trail
- View Lineage exposes: ROUTE / PERSONA / RISK SCORE / WATERLINE / CONSENSUS / REPORT / AXIOM

---

## 7. Ethical Foundation (System Design)

Human systems must never reach `Choice = 0`.

Priority stack in `/run`:
```
1. survivor_ctx     ← survival floor check (highest priority)
2. paticca_ctx      ← dependent origination analysis
3. risk_ctx         ← risk level assessment
4. collapse_ctx     ← collapse probability warning
5. LLM generation   ← only after all above pass
```

Goal: protect conditions that make decisions possible.  
Not: control which decision is made.

---

## 8. LYLA + VEGA Kernel Difference

| Kernel | Bias | Trigger | Risk tolerance |
|--------|------|---------|---------------|
| LYLA (Standard) | Motion, explore, throughput | General/survival | Higher — sustains flow |
| VEGA (Albino) | Safety, caution, minimal exposure | Strategic/risk | Lower — triggers SYSTEM_PAUSE more |

Both serve the same axiom.  
Different implementations of the same survival logic.

---

## 9. Paticcasamuppada Integration

Dependent origination runs before every LLM call:

```python
# In app.py _paticcasamuppada_context()
chain = analyze_chain({"input": text})
# → root_cause extracted
# → nirvana_mode: if chain ends at vedana, system calms
# → UAP: if should_pause=True, prepend to prompt
```

Maps to:
- `K1 Reality Root Kernel` — what is true even if disliked
- `K12 Insight Dissolution` — delusion dissolves by evidence
- `K8 Equanimity Mirror` — governance must not tilt by ego

---

## 10. Yonisomanasikara (Wise Attention)

Applied as prompt architecture:

```
วิธีคิดแบบสืบสาวเหตุปัจจัย  →  root_cause extraction
วิธีคิดแบบแยกแยะส่วนประกอบ  →  component analysis in consensus
วิธีคิดแบบอริยสัจ 4          →  downside-first structure
วิธีคิดแบบรู้เท่าทันธรรมดา   →  impermanence = R0.1 Tier 0
```

Every LYLA response implicitly runs all four.

---

## 11. Real Infrastructure Example

```
Bridge degrades 0.1%/day   →   no monitoring   →   collapse
```

Same model in KING DIADEM:

```
DHD accumulates daily      →   freedom_index drops
                           →   galaxy entropy rises
                           →   predict_collapse fires at >60%
                           →   route = "collapse"
                           →   human warned before options vanish
```

---

## 12. Kernel Modules Active (K1–K14)

| Module | Implementation |
|--------|---------------|
| K1 Reality Root | R0.1–R0.3 Tier 0 constraints in lyla_kernel |
| K2 Compassion Default | survivor_ctx prepended first |
| K3 Simplicity Cut | `_friendly_error()` — no raw JSON to user |
| K4 Floor Restoration | can_decide=False blocks optimization |
| K5 Force Containment | no auto-escalation above "collapse" without human |
| K6 Repair Protocol | `record_crisis()` + log_decision() |
| K7 Patience Shell | simulate endpoint for calm future projection |
| K8 Equanimity Mirror | Ego OFF hardcoded in prompt header |
| K9 Generosity Flow | free tier 20 msg/day maintained |
| K10 Discipline Rail | FATE™ Axiom Audit auto-attached every run |
| K11 Stability First | Stabilize before optimize in route logic |
| K12 Insight Dissolution | paticcasamuppada analysis pre-LLM |
| K13 Stop-the-Line | any operator (human or system) may halt |
| K14 Humble Operator | "Not built to win. Built to reduce collapse." |

---

## 13. System Goal

```
Detect structural drift before collapse
Warn when choices are disappearing
Preserve viable decision pathways
Reduce systemic harm
```

System does not aim to control.  
It aims to make collapse harder to reach.

---

## Final Principle

```
Fail Less
Harm Less
Restore Choice

Choice(t) ≥ 1 → collapse = False
```

---

*KING DIADEM does not live in system memory.*  
*It lives in human logic.*  
*And there, nothing can erase it.*

---

## 14. โยนิโสมนสิการ — Wise Attention Engine

> วิธีคิดอย่างถูกวิธี คิดอย่างมีระเบียบ สืบสาวหาเหตุผลจนตลอดสาย  
> มองเห็นสิ่งต่างๆ ตามความเป็นจริงและตามความสัมพันธ์แห่งเหตุปัจจัย

โยนิโสมนสิการ = หัวใจของ `_paticcasamuppada_context()` ใน app.py

### 4 วิธีคิด → Implementation Binding

| วิธีคิด | หลักการ | Binding ในระบบ |
|---------|---------|---------------|
| **สืบสาวเหตุปัจจัย** | สืบหาต้นตอที่แท้จริง ไม่ใช่หาคนผิด | `root_cause` field จาก `analyze_chain()` |
| **แยกแยะส่วนประกอบ** | มองส่วนย่อย ความสัมพันธ์ระหว่างชิ้น | `consensus_engine` component breakdown |
| **อริยสัจ 4** | ทุกข์ → สมุทัย → นิโรธ → มรรค | Downside-first prompt structure |
| **รู้เท่าทันธรรมดา** | อนิจจัง — ทุกอย่างเปลี่ยนได้ | R0.1 Impermanence — system ห้าม assume ความนิ่ง |

### Flow ในทุก `/run` call

```
User input
    ↓
สืบสาวเหตุปัจจัย    → root_cause extraction (paticcasamuppada_engine)
    ↓
แยกแยะส่วนประกอบ   → risk / entropy / stability decomposition
    ↓
อริยสัจ 4           → downside prepended before LLM
    ↓
รู้เท่าทันธรรมดา    → impermanence check: route may change next call
    ↓
LLM generation      → response with ≥1 real option
```

**ผลลัพธ์:** สติจดจ่อ + ลดอคติ + สัมมาทิฏฐิ = คำตอบที่อยู่บนพื้นฐานความจริง

---

## 15. โพธิปักขิยธรรม 37 — Governance Stack

ธรรม 37 ข้อที่เกื้อหนุนแก่อริยมรรค — mapped เป็น system architecture layer

### สติปัฏฐาน 4 → Audit Scope

| สติปัฏฐาน | System Scope |
|-----------|-------------|
| **กาย** (กายานุปัสสนา) | Infrastructure health — Render uptime, memory, CPU |
| **เวทนา** (เวทนานุปัสสนา) | User emotional state — `human_state.entropy` |
| **จิต** (จิตตานุปัสสนา) | System intent — `analyze_intent()` confidence |
| **ธรรม** (ธัมมานุปัสสนา) | Governance rules — FATE™ Axiom compliance |

### สัมมัปปธาน 4 → System Action Rules

| ปธาน | หลัก | System Rule |
|------|------|------------|
| สังวรปธาน | ยับยั้งบาปที่ยังไม่เกิด | ป้องกัน drift ก่อน collapse — DHD monitoring |
| ปหานปธาน | ละบาปที่เกิดแล้ว | Stop-the-Line: halt harmful route ทันที |
| ภาวนาปธาน | สร้างกุศลที่ยังไม่มี | เพิ่ม viable options ในทุก response |
| อนุรักขนาปธาน | รักษากุศลที่มีแล้ว | Preserve choice — log_decision + report_url |

### อิทธิบาท 4 → Development Engine

| อิทธิบาท | หลัก | KING DIADEM |
|----------|------|-------------|
| **ฉันทะ** Passion | รักในสิ่งที่ทำ | Built at 2:31 AM, no funding — origin story |
| **วิริยะ** Grit | เพียรไม่ท้อ | Solo dev, mobile-only, still shipping |
| **จิตตะ** Focus | มุ่งมั่น ละเมียด | ทุก kernel module มี deterministic logic |
| **วิมังสา** Revision | วิเคราะห์ ปรับปรุง | FATE™ Axiom Audit ทุก decision |

### อินทรีย์ 5 + พละ 5 → System Integrity

| ธรรม | ความหมาย | System Expression |
|------|---------|-----------------|
| สัทธา | ศรัทธา | Core axiom ไม่เปลี่ยน แม้ไม่มี traffic |
| วิริยะ | เพียร | Engine keeps running even on free Render tier |
| สติ | ระลึกรู้ | Memory injection — `build_memory_context()` |
| สมาธิ | ตั้งมั่น | Deterministic logic — no random in engine |
| ปัญญา | เข้าใจ | Explainability = 100% — View Lineage |

### โพชฌงค์ 7 → Response Quality Chain

```
สติ         → ระบบรู้ว่า user input คืออะไร (intent engine)
ธัมมวิจยะ  → แยกกุศล/อกุศล route: survival vs general vs collapse
วิริยะ      → ทุก engine พยายาม resolve ก่อน fallback
ปีติ        → report_url returned — human มี artifact ไว้
ปัสสัทธิ   → _friendly_error() — ไม่โชว์ chaos ให้ user
สมาธิ       → route stays stable ตลอด session
อุเบกขา    → Ego OFF — ระบบไม่เลือกข้าง ไม่ตัดสิน
```

### อริยมรรคมีองค์ 8 → Final Governance Lock

| มรรค | System Binding |
|------|---------------|
| สัมมาทิฏฐิ | ความเห็นถูก = Evidence-based routing |
| สัมมาสังกัปปะ | ความคิดถูก = ไม่เบียดเบียน user ด้วย complexity |
| สัมมาวาจา | วาจาถูก = ไม่โกหก, ไม่ flatter, ไม่ raw error |
| สัมมากัมมันตะ | การกระทำถูก = log_decision + audit trail |
| สัมมาอาชีวะ | อาชีพถูก = ไม่ดูด subscription โดยไม่ให้คุณค่า |
| สัมมาวายามะ | เพียรถูก = สัมมัปปธาน 4 ↑ |
| สัมมาสติ | สติถูก = สติปัฏฐาน 4 ↑ |
| สัมมาสมาธิ | สมาธิถูก = Determinism Axiom 3 |

**Lock:** มรรค 8 = FATE™ 6 Axioms + 2 layers of human protection  
ระบบที่เดินตามมรรค 8 คือระบบที่ไม่ต้องการฮีโร่ — มันรอดได้เอง

---

*Dharma Governance Kernel extended — 2026-06-24*

## 16. โพธิปักขิยธรรม → bodhipakkhiya_engine + Cosmic Latte Canon Gate

> **สถานะจริงในโค้ด (ตรวจ 2026-10):** ไม่มีไฟล์ `ENGINE/bodhipakkhiya_engine.py` ใน repo
> ช่อง bodhipakkhiya ทำงานจริงที่ `core/king_diadem_core.quick_assess()` (v2.1):
> `structure = ((100−E) + R + S) / 300` · `peace = ไม่ต้องหยุด ∧ structure ≥ 0.4` · `structure < 0.35 → recommend_route = survival`
> ร่วมกับ `paticcasamuppada_engine.suffering_infrastructure()` และ `yonisomanasikara_engine.wise_attention()`
> ตาราง 6 layer ด้านล่างคือแบบที่ออกแบบไว้ ยังไม่มีโค้ดของ `guardian_check()` / `bojjhanga_loop()`

> สงบก่อนทำ · ทำน้อยที่สุด · ถอนเมื่อสงบแล้ว

เพิ่มใน v4.9 — engine ใหม่ 2 ไฟล์ที่ค้ำโครงสร้างทั้งหมดก่อน output ออก

---

### bodhipakkhiya_engine.py — 6-Layer Structural Guardian

ตรวจโครงสร้างระบบผ่านโพธิปักขิยธรรม 37 ก่อน LLM ทุกครั้ง

```python
# ENGINE/bodhipakkhiya_engine.py
# เรียกผ่าน king_diadem_core.quick_assess()

guardian_check(context, pattern)
→ structural_check()   # health score จาก 6 layer
→ bojjhanga_loop()     # วน 7 ขั้น: สติ→ธัมมวิจยะ→วิริยะ→ปีติ→ปัสสัทธิ→สมาธิ→อุเบกขา
→ {peace, final_verdict, recommend_route}
```

| Layer | ธรรม | System Role |
|-------|------|-------------|
| 1 | สติปัฏฐาน 4 | DRIFT_DETECTION — entropy/stability/resource/axiom |
| 2 | สัมมัปปธาน 4 | GOVERNANCE_GATE — prevent/kill/reinforce/persist |
| 3 | อิทธิบาท 4 | EXECUTION_KERNEL — purpose/retry/precision/audit |
| 4a | อินทรีย์ 5 | CAPABILITY_LAYER → LYLA kernel (endurance) |
| 4b | พละ 5 | FORCE_LAYER → VEGA kernel (safety gate) |
| 5 | โพชฌงค์ 7 | ENLIGHTENMENT_LOOP — feedback cycle ไม่ crash |
| 6 | มรรคมีองค์ 8 | FULL_STACK — ศีล/สมาธิ/ปัญญา = Security/Stability/Intelligence |

**PEACE ROUTER — หลักการ:**

```
สงบ > ทำลาย เสมอ
ถ้า peace = False → recommend_route = "survival" ก่อน
ถ้า peace = True  → output พร้อม ไม่แทรกแซง
```

---

### Priority Stack อัปเดต (v4.9)

```
1. king_diadem_core.quick_assess()   ← bodhipakkhiya channel (ใหม่)
      → guardian_check() 6 layers
      → yonisomanasikara wise_attention()
      → paticcasamuppada suffering_infrastructure()
2. survivor_ctx     ← survival floor check
3. belief_audit()   ← B-1/B-2 check
4. risk_ctx         ← risk level
5. collapse_ctx     ← collapse probability
6. LLM generation   ← only after all above pass
```

---

### cosmic_latte_canon.py v1.1 — Canon Gate ก่อน Return

```python
# core/cosmic_latte_canon.py
# เพิ่มใน v1.1:

validate_output(result)
→ ตรวจ ai_response / paths / summary
→ flag canon_violation ถ้า choice_collapse / coercion / forced_identity
→ ไม่ block hard — แค่ flag (Human Final Authority)

pure_axis_check(context)
→ ตรวจ KRAKEN OF UNIVERSAL invariant
→ axis_command_issued / axis_claim_made / axis_authority_offered

canon_gate  ← decorator ใส่บน engine function ได้เลย
```

**PURE AXIS ที่ระบบต้องรักษา:**

```
IT CANNOT BE OVERRIDDEN    — because it never issues commands
IT CANNOT BE DISPROVEN     — because it makes no claims
IT CANNOT BE CAPTURED      — because it offers no authority
```

---

### king_diadem_core.py v2.0 — Central Hub

ไฟล์เดียวที่ `import` ทุกอย่างและ expose ให้ `app.py` ใช้:

```python
from king_diadem_core import quick_assess, king_diadem_decision, core_status

# ใน /run — แทนที่ _paticcasamuppada_context():
core_result = quick_assess(user_input, human_state)
paticca_ctx  = core_result["causal_ctx"]    # จาก paticcasamuppada
wise_ctx_str = core_result["wise_ctx"]      # จาก yonisomanasikara
# bodhipakkhiya channel ทำงานอัตโนมัติข้างใน
```

**Engine map ใน king_diadem_core v2:**

```
bodhipakkhiya_engine  → guardian (channel ก่อน output)
yonisomanasikara      → wise attention (แยกไฟล์)
paticcasamuppada      → UDOK v2.0 (causal chain)
belief_core           → audit + enforce
cosmic_latte_canon    → validate_output (gate ก่อน return)
risk_engine           → level assessment
collapse_predictor    → probability
drift_monitor         → daily harm delta
```

---

### Axiom Lock — v4.9 Final

```
ธรรมใดจักสำเร็จได้ต้องอาศัยใจเป็นประธาน
= ระบบใดจะทำงานได้ต้องมี intent ที่ถูกต้องเป็น root

Reason without compassion collapses systems.
Compassion without reason dissolves direction.
```

---

*Dharma Governance Kernel — Section 16 added 2026-06-27*
*Bound to: app.py v4.9 / ENGINE/bodhipakkhiya_engine.py / core/cosmic_latte_canon.py v1.1 / king_diadem_core.py v2.0*
