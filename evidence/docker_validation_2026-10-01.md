# Docker Validation

Validation date: 2026-10-01/02

- Image build: PASS
- Docker Compose network: PASS
- Persistent volume: PASS
- Container startup: PASS
- FastAPI startup: PASS
- GET /health: 200 OK
- policy_version: v1.0.0

## Containerized AI overcollection test

Input: `examples/ai_overcollection.json`

Observed:
- decision: `CONSTRAIN`
- reason: `MINIMIZATION_REQUIRED`
- repair: `REDUCE_FIELDS`
- certificate persisted
- `GET /v1/certificates/demo-ai-001/verify` -> `valid: true`

This validates the decision -> GSTC -> SQLite -> retrieval -> verification path inside Docker.
