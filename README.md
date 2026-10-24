# KING DIADEM

King Diadem is a decision-governance and crisis-detection system designed to monitor whether a situation is quietly collapsing toward zero usable choices, then surface safer, more viable options before the system fails.

It is built as a practical framework for human decision support across risk, survival, infrastructure, business, and public-governance contexts.

Live demo: https://king-diadem.onrender.com

[![Website](https://img.shields.io/badge/Website-king--diadem.onrender.com-181717?style=for-the-badge&logo=render&logoColor=white)](https://king-diadem.onrender.com)
[![Instagram](https://img.shields.io/badge/Instagram-@thekingdiadem-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/thekingdiadem)
[![Fastwork](https://img.shields.io/badge/Fastwork-Hire%20Me-3B5BFE?style=for-the-badge&logoColor=white)](https://fastwork.co/byob/CtqOnVfzC7)

---

## What this project is

KING DIADEM watches for the moment when a system begins losing real, survivable choices.

The central idea is simple:

```python
Risk = Drift × Exposure / Remaining Choice
Choice(t) >= 1 -> collapse = False
```

When a path has no real room to recover, the system does not pretend it is safe. It flags the risk early and keeps the user anchored to viable options.

This project is not a generic chatbot. It is a structured decision layer built to:

- detect drift before it becomes irreversible
- distinguish real choice from fake choice
- separate survival minimums from aspirational goals
- surface downside-first reasoning before upside-first optimism
- keep human decision authority intact

---

## Current status

This repository is a working decision-support application with:

- FastAPI backend
- Python logic engine
- SQLite persistence and session memory
- Multi-AI advisory council
- web interface with PWA support
- i18n support (Thai / English / 日本語)
- Google OAuth and Stripe integration
- report generation and shareable output
- deployment targeting Render

The repo is in a mature prototype / production-adjacent stage, with a substantial automated test suite covering safety, governance logic, language handling, app pages, and system behavior.

---

## Core system behavior

KING DIADEM combines a deterministic decision kernel with a council of reasoning voices.

The flow is generally:

```text
Human input
  -> request validation and gating
  -> signal detection (risk, collapse, survival, language, urgency)
  -> context assembly and decision scoring
  -> multi-perspective council analysis
  -> choice-preservation checks and safe output constraints
  -> human final decision
```

The framework is intentionally designed so that AI is advisory, not sovereign.

### Safety principles

- Logic over persona
- Rule over authority
- Human retains final authority
- Downside before upside
- Explainability before confidence
- A system that reduces human choice to zero is considered failed

---

## Council model

The current architecture includes a multi-voice decision layer, such as:

- LYLA — emotional awareness, user-side perspective, option recovery
- VEGA — downside-first logic, risk framing
- TITAN — minimum viable survival path
- PATICCA — causal and pattern-based evaluation
- COSMOS — long-horizon, system-level view
- CIVIL — social and structural impact view

These voices are not used to replace governance. They are used to test whether a decision remains viable, explainable, and safe.

---

## Product surface

The app includes a set of decision and information pages, including:

- `/` — main conversational experience
- `/ask` — direct decision comparison
- `/guide` — guidance and usage notes
- `/letter` — letter and narrative content
- `/architecture` — architecture map and repo structure view
- `/wallet` — account / premium / payment-related state
- `/report/<id>` — generated reports with shareable links

The project also includes a global architecture map generated from repo metadata and a PWA-friendly frontend.

---

## Repository structure

Key directories and modules include:

```text
app.py                  # FastAPI application and routes
core/                   # core reasoning, signal detection, orchestration
ENGINE/                 # decision, risk, collapse, routing logic
AI/                     # advisory council and AI-oriented behavior
AI_KERNEL/              # governance and rule enforcement layers
DATABASE/               # persistence and state management
DOMAINS/                # domain-specific engines and decision contexts
WORLD_MODEL/            # broader world-state modeling
SIMULATIONS/            # scenario modeling and stress simulation
SECURITY/               # safety and load protections
static/                 # frontend assets, PWA, pages, UI resources
tests/                  # automated test suite
scripts/                # repo utilities and evaluation scripts
```

---

## Security, privacy, and governance

The system includes expected governance controls around:

- no raw user text in server logs
- session-based state handling
- secret-key and credential protection
- rate limiting and request guardrails
- secure payment verification patterns
- human-first override principles

This project is explicitly designed to protect options and reduce harm, not to optimize for manipulation or opaque automation.

---

## Local development

Requirements:

```bash
pip install -r requirements-dev.txt
```

Set environment variables:

```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export GEMINI_API_KEY=...   # optional; the system can still function with deterministic logic fallback
```

Run the app:

```bash
uvicorn app:app --reload
```

---

## Testing

The repository includes a large automated test suite under `tests/` for:

- API and route behavior
- governance and safety constraints
- language and signal detection
- UI and page usability
- resilience and edge-case logic
- decision quality evaluation

Typical usage:

```bash
pytest
```

---

## Roadmap alignment

The current repo already contains substantial completed work in:

- decision architecture
- rule-based safety automation
- crisis and risk analysis
- multi-language support
- session memory
- world-model integration concepts
- deployment readiness

Planned evolution continues around more advanced external-data integrations, deeper resilience work, and broader real-world scenario coverage.

---

## License

This project is licensed under the GNU AGPL-3.0 license.

See:

- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

---

## Contact

- Instagram: https://www.instagram.com/thekingdiadem
- Fastwork: https://fastwork.co/byob/CtqOnVfzC7

---

Fail less. Harm less. Restore choice.
