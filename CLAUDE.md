# CLAUDE.md — tutorbot

**Room:** WhatsApp Tutoring Bot
**Domain:** tutoring
**Language:** Python (Flask)

WhatsApp bot for Stephen's tutoring business. Handles student intake, lesson planning, and payment flows via Chatwoot (WhatsApp CRM), Google Calendar, and Stripe.

---

## Commands

```bash
# From project root
python main.py                     # Start Flask bot server

# Tests
pytest tests/ -v                   # All tests
pytest tests/ -v --cov            # With coverage

# Docker
docker compose up -d --build       # Run via Docker
```

---

## Architecture

```
main.py                # Flask app entry point + webhook handler
helpers.py             # Shared utilities
modules/
├── segment_detection/ # Classify incoming conversation (new/existing student)
├── intake/            # New student intake flow
├── planning/          # Lesson scheduling flow
└── payment/           # Stripe payment link generation
config/                # Configuration and environment loading
scripts/               # Utility scripts
tests/                 # Pytest test suite
coverage_html/         # pytest --cov HTML report output (gitignored)
docs/                  # Project documentation (architecture, API, setup, workflows)
tutorbot_env/          # Python virtualenv (gitignored — use for local dev)
```

**Integrations:**
| Service | Purpose | Auth |
|---------|---------|------|
| Chatwoot | WhatsApp CRM + webhook source | API token |
| Google Calendar | Lesson scheduling | Service account |
| Stripe | Payment links + webhooks | Secret key |
| PostgreSQL | Student data (via direct psycopg2 or shared schema) | DB URL |

---

## Agent routing

**Primary agents:** 03-implementer, 12-workflow-architect | **Skills:** `repo-research`, `workflow-decomposition`, `implementation-planning`

---

## Key rules

- **Webhook security:** Chatwoot webhook requests must be validated before processing — check `helpers.py`.
- **Conversation state:** state is stored in PostgreSQL — never in memory (Flask is stateless under Docker).
- **Stripe webhooks:** validate `stripe-signature` header before processing payment events.
- **Calendar:** use the service account in `config/` — never OAuth flow (bot runs headless).
- **Error handling:** all flow handlers must catch and log exceptions — a crash in one flow must not kill other conversations.
- **No shared Prisma:** tutorbot uses direct DB access (Python) — changes to schema must be reflected manually here.
