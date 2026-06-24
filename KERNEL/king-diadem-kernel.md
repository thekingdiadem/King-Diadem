# KING DIADEM Kernel
**Version: v4.7-LIVE**  
**System Lock: Fail less. Harm less. Restore more.**

---

## Core Principle

Systems collapse when choices disappear.  
Governance exists to prevent that moment.

---

## System Invariant

```
Choice(t) ≥ 1 → collapse = False
Choice(t) → 0 → SYSTEM_HALT
```

A system remains survivable as long as at least one viable option exists.

---

## Runtime Binding (app.py v4.7)

This kernel governs the following live endpoints:

| Endpoint | Kernel Function | Engine |
|----------|----------------|--------|
| `POST /run` | Primary decision pipeline | `DecisionEngine` + `universal_engine` |
| `POST /decision` | Alias for /run | same |
| `POST /simulate` | Future scenario projection | `simulation_engine` |
| `GET /api/galaxy/nodes` | System state broadcast | `_gstate` galaxy |
| `GET /health` | System integrity check | all engines |
| `GET /report/{id}` | FATE™ Audit page | `report_engine` |
| `GET /api/report/{id}` | Report JSON | `report_engine` |
| `GET /dashboard` | Planetary status + freedom index | `civilization_*` |

---

## Governance Rules (Active in /run pipeline)

**Ego OFF — Evidence ON**  
Authority without evidence is invalid.  
Source: `_friendly_error()` + intent engine — no raw error shown to user.

**Stop-the-Line Authority**  
Any operator may halt.  
Source: `assess_risk()` → if level HIGH/CRITICAL → route = "collapse"  
Source: `survivor_analyze()` → if can_decide=False → route = "survival"

**Stabilize before Optimize**  
Source: `_paticcasamuppada_context()` runs before every LLM call.  
Source: `survivor_ctx` prepended to all prompts.

**Human Final Authority**  
Source: `log_decision()` — all decisions attributed to user_email.  
Source: Report URL returned with every `/run` response.

---

## Route Map (Collapse Risk Hierarchy)

```
general   → standard governance
risk      → risk_engine triggered
survival  → survivor_analyze: can_decide=False
collapse  → assess_risk: HIGH or CRITICAL
vega      → strategic long-range analysis
civil     → civilization_engine nodes
```

Route escalation is automatic.  
Route de-escalation requires human input.

---

## Persona Assignment

| Voice Mode | Persona | Sign | Character |
|-----------|---------|------|-----------|
| lyla | LYLA ◈ | ค่ะ | Empathetic, survival-first |
| vega | VEGA ◆ | ครับ | Analytical, strategic |
| crisis | HALT ⬡ | — | Immediate action only |

Detection: `window.detectConversationMode()` in frontend.  
Override: `voice_mode` param in `/run` payload.

---

## FATE™ Axiom Audit (Auto-attached v4.7)

Every `/run` response generates:
```
result["report_url"]  = /report/{id}
result["report_id"]   = uuid
result["share_url"]   = https://king-diadem.onrender.com/report/{id}
```

Axioms checked per decision:
1. Logic over Persona — route chosen by evidence, not narrative
2. Rule over Authority — kernel rules cannot be overridden by user rank
3. Determinism — `lyla_kernel` + `decision_engine` (no random)
4. Downside before Upside — risk_ctx prepended before LLM call
5. Explainability = 100% — lineage visible in View Lineage toggle
6. Human Final Authority — log_decision() + report URL returned

---

## Galaxy State Sync

After every `/run` call, `_sync_galaxy(result)` updates:
```python
_gstate["active_route"]  # drives planet highlight
_gstate["risk_score"]    # drives visual pulse
_gstate["lyla_mode"]     # "burst" if response exists
_gstate["entropy"]       # from pattern
_gstate["stability"]     # from pattern
_gstate["resource"]      # from pattern
```

Frontend polls `/api/galaxy/nodes` every N seconds to reflect live system state in canvas.

---

## Daily Harm Delta (DHD) — Drift Detection

Tracked implicitly via:
- `freedom_index()` — drops if questions go unanswered
- `risk_score` trend — rises with each collapse-route trigger
- `collapse_probability` — from `predict_collapse()`

If DHD compounds → route escalates → kernel triggers Stop-the-Line.

---

## Entropy Buffer (Human Layer 4)

System acknowledges:
- Creator operates solo, mobile-only, no external funding
- Single-point failure must be designed against
- Minimum livelihood floor = food delivery income baseline
- System must survive creator's offline periods (Render auto-sleep handled via `render.yaml`)

Any feature that requires creator to be online 24/7 violates this kernel.

---

## Waterline Integrity

```
Treat   → apply kernel governance
Trace   → log_decision() + report_engine
Stop    → Stop-the-Line via survivor/risk engine
```

Water harm = system death.  
Metric source: `water_stress_index` in `/dashboard`.

---

## Objective

Detect structural signals of **Choice Collapse** early enough  
to restore at least one viable option.

```
Fail Less
Harm Less
Restore Choice
```

**Lock:** `Choice(t) ≥ 1 → collapse = False`
