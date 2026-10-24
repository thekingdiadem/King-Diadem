# KING DIADEM

King Diadem is a decision-governance system designed to detect when a situation is quietly collapsing toward zero usable choices and intervene before the path becomes irreversible.

It is not a generic chatbot. It is a practical decision layer built for real-world risk, crisis, survival, business, and governance situations where humans need a safer route forward.

Live demo: https://king-diadem.onrender.com

[![Website](https://img.shields.io/badge/Website-king--diadem.onrender.com-181717?style=for-the-badge&logo=render&logoColor=white)](https://king-diadem.onrender.com)
[![Instagram](https://img.shields.io/badge/Instagram-@thekingdiadem-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/thekingdiadem)
[![Fastwork](https://img.shields.io/badge/Fastwork-Hire%20Me-3B5BFE?style=for-the-badge&logoColor=white)](https://fastwork.co/byob/CtqOnVfzC7)

---

## What this project is

KING DIADEM is built around one principle:

```python
Risk = Drift × Exposure / Remaining Choice
Choice(t) >= 1 -> collapse = False
```

The framework tries to answer a simple question:

> Is this system losing real options, and is the loss happening faster than people notice?

It is designed for situations where choices are shrinking silently:

- financial stress and debt
- employment and survival uncertainty
- relationship and safety risk
- business disruption
- public or organizational decision collapse
- crisis response under pressure

The goal is not to make a perfect prediction. The goal is to keep actual, survivable options visible before the system reaches a hard failure point.

---

## What is already built

This repository is not a blank prototype. It contains a working decision-support system with real engineering behind it.

### Core product capabilities

- FastAPI web app and route layer
- multi-layer decision pipeline
- risk, collapse, survival, and route detection
- crisis-aware responses for self-harm, violence, basic-needs shortages, scams, and disaster conditions
- deterministic fallback logic when AI is unavailable or blocked
- session memory and user-specific state tracking
- multi-language handling for Thai, English, and Japanese
- Google OAuth login and session management
- Stripe billing, premium handling, and wallet-style credit flows
- report generation and shareable decision reports
- PWA support and web app behavior
- architecture map and system overview pages

### Decision system behavior

The app pipeline is structured around a safety-first flow:

```text
User input
  -> input validation and rate limiting
  -> signal detection (risk, urgency, language, route)
  -> human-state and context analysis
  -> kernel + engine reasoning
  -> council-style advisory review
  -> canon and safety gate checks
  -> final response with human authority preserved
```

This means the system appends governance around AI rather than letting AI decide without guardrails.

---

## The actual architecture in this repo

The codebase is organized around real system layers rather than a toy app structure.

```text
app.py                  # FastAPI app, routes, auth, payments, safety middleware
core/                   # core decision logic, language signals, route logic, kernel response generation
ENGINE/                 # decision engine, risk engine, collapse predictor, survivor logic, bridge logic
AI/                     # AI intent and advisory behavior
AI_KERNEL/              # governance / enforcement / belief checks
DATABASE/               # SQLite persistence, user accounts, memory, transactions
DOMAINS/                # domain-specific reasoning and context engines
WORLD_MODEL/            # broader world-state simulations and modeling
SIMULATIONS/            # scenario simulation modules
SECURITY/               # load protection, system resilience layers
static/                 # frontend, pages, service worker, app assets
tests/                  # automated regression and behavior tests
scripts/                # utility / evaluation scripts
```

### Decision and governance layers

The system includes several overlapping layers:

- Kernel rules and safety gates
- decision engine and route orchestration
- human-state risk analysis
- survival and collapse checks
- council voices for decision review
- belief and canon enforcement before response delivery
- output sanitization and option limiting

This is how the project differs from a basic chatbot: the flow is designed to keep humans safer and keep choices realistic.

---

## Main product surfaces

The application includes pages and APIs with concrete functions:

| Route | Purpose |
|---|---|
| `/` | main conversation and decision experience |
| `/ask` | direct comparison / option analysis |
| `/guide` | user guidance and instructions |
| `/letter` | narrative / founder letter |
| `/architecture` | architecture and repo map |
| `/wallet` | credit, premium, account payment state |
| `/report/<id>` | shareable generated reports |
| `/health` | system health status |
| `/login/google` | Google auth flow |
| `/webhook/stripe` | Stripe payment event processing |

It also includes API routes for:

- `/run` and `/decision`
- `/simulate`
- `/api/chat-state`
- `/api/history`
- `/api/memory`
- `/api/waterline`
- `/api/feedback`
- `/api/report/share`

---

## Key technical stack

```text
Backend:     FastAPI + Python
AI:          Google Gemini + fallback deterministic logic
Database:    SQLite
Auth:        Google OAuth + signed session cookies
Payments:    Stripe checkout + webhook validation
Frontend:    Vanilla JS + HTML/CSS + Canvas/PWA
Deploy:      Render
```

### Notable implementation details

The codebase explicitly includes:

- secret-key enforcement for sessions and auth
- request-body limits and security headers
- quota / credit / premium logic
- fallback responses without AI for urgent use cases
- user-safe handling for potentially dangerous situations
- server-side validation of third-party payment events
- report lifecycle and temporary share-token handling

---

## Current project status

This repository is in a mature working state for a research-to-product decision-governance project.

It already contains substantial implementation in:

- risk detection and collapse awareness
- multi-model decision framing
- safety gating and crisis response
- user authentication + payment
- persistence and memory
- app pages and deployed web experience
- large automated tests covering pages, logic, safety, and language behavior

The project is not “just a concept repo” anymore. It is a functioning decision-support application with operational layers and deployment-oriented engineering.

---

## Safety and governance principles

The system is shaped around these principles:

- Logic over persona
- Rule over authority
- Human retains final authority
- Downside before upside
- Explainability before confidence
- A system that reduces a human to zero viable options is considered a failure

This is not a productivity app pretending to be neutral. It is deliberately designed to keep choice alive.

---

## Local development

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

Set required environment variables:

```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export GEMINI_API_KEY=...
export GOOGLE_CLIENT_ID=...
export GOOGLE_CLIENT_SECRET=...
export STRIPE_SECRET_KEY=...
export STRIPE_WEBHOOK_SECRET=...
export STRIPE_PRICE_ID=...
export STRIPE_PREMIUM_PRICE_ID=...
```

Run locally:

```bash
uvicorn app:app --reload
```

---

## Testing

This repo has a large automated test suite under `tests/` covering behavior such as:

- page rendering and route behavior
- safety and governance constraints
- language detection and multilingual behavior
- risk and urgent-response logic
- API contract checks
- edge-case logic and fallback behavior

Run tests with:

```bash
pytest
```

---

## Roadmap alignment

The repo already includes completed work in:

- decision framework and governance kernel
- multi-voice advisory system
- survival and crisis logic
- memory and personalization features
- secure auth and billing
- web deployment and app buildout
- project-wide testing and governance layers

The remaining work is centered on deeper external-data integration, resilience scaling, and broader live-world scenario coverage.

---

## License

This project is licensed under the GNU AGPL-3.0 license.

See:

- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

---

## Support

- Instagram: https://www.instagram.com/thekingdiadem
- Fastwork: https://fastwork.co/byob/CtqOnVfzC7

---

Fail less. Harm less. Restore choice.
