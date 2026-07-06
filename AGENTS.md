# AGENTS.md

Codex guidance for `projects/tutorbot`.

## Overview

- Flask-based WhatsApp tutoring bot integrated with Chatwoot, Calendar, Stripe, and PostgreSQL.

## Commands

```bash
python main.py
pytest tests/ -v
pytest tests/ -v --cov
docker compose up -d --build
```

## Rules

- Validate Chatwoot webhook requests before processing.
- Keep conversation state in PostgreSQL, not in-memory process state.
- Validate Stripe webhook signatures.
- Use the service account flow for Calendar access.
- Catch and log flow-level exceptions so one failure does not kill the bot.
