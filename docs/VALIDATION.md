# DATA-PROOF v0.1.0 Validation Evidence

Validation date: 2026-10-01/02 (America/New_York)

This record captures the reproducible local and containerized validation performed on the author's Windows workstation.

## Local Python validation

### Unit and API tests
- Result: 6 passed
- Warning: one Starlette/TestClient deprecation warning; non-blocking

### Deterministic benchmark
- Scenario families: 16
- Passed: 16
- Policy conformance: 1.0
- Unrestricted allow errors: 0
- UAER: 0.0

### Ablation
| Ablation | Passed | Total | Conformance |
|---|---:|---:|---:|
| no_purpose | 13 | 16 | 0.8125 |
| no_residency | 14 | 16 | 0.8750 |
| no_quality | 14 | 16 | 0.8750 |
| no_lineage | 15 | 16 | 0.9375 |
| no_composition | 15 | 16 | 0.9375 |
| no_minimization | 15 | 16 | 0.9375 |
| no_policy_version | 15 | 16 | 0.9375 |

### GSTC mutation test
- Certificates tested: 5,000
- Mutations detected: 5,000
- Detection rate: 1.0

### Local latency
- Executions: 32,000
- Mean: 54.5545625 microseconds
- p95: 80.5 microseconds
- p99: 120.4 microseconds

These timings are specific to the local execution environment and should not be treated as universal performance numbers.

## HTTP end-to-end validation

### Health
GET /health -> 200 OK
- status: ok
- policy_version: v1.0.0

### Normal governed read
POST /v1/evaluate using examples/allow_read.json
- decision: ALLOW
- reason: POLICY_SATISFIED
- GSTC generated and persisted

### AI overcollection
POST /v1/evaluate using examples/ai_overcollection.json
- decision: CONSTRAIN
- reason: MINIMIZATION_REQUIRED
- repair: REDUCE_FIELDS
- retained fields:
  - customer_id
  - invoice_total
  - payment_status
- removed fields:
  - ssn
  - dob
  - address
  - medical_notes
  - email
  - phone
  - zipcode
- GSTC generated and persisted
- stored certificate verification: valid=true

### Sensitive derived join
POST /v1/evaluate using examples/sensitive_join.json
- pre-operation disclosure risk: 0.35
- predicted post-operation disclosure risk: 0.92
- governance delta: 0.57
- decision: CONSTRAIN
- reason: COMPOSITION_RISK
- repair: MASK_OR_TOKENIZE
- target risk threshold: below 0.7
- GSTC generated and persisted

## Docker validation

Docker build completed successfully.

docker compose up:
- network created
- persistent volume created
- container created
- FastAPI startup completed
- Uvicorn listening on port 8000
- health endpoint returned 200 OK

Containerized AI-overcollection validation:
- decision: CONSTRAIN
- reason: MINIMIZATION_REQUIRED
- repair: REDUCE_FIELDS
- GSTC persisted
- certificate verification returned valid=true

## Validated scope

The following paths have been validated:
- Python package installation
- Unit/API tests
- 16-scenario deterministic benchmark
- Component ablations
- GSTC generation and mutation detection
- FastAPI/OpenAPI service
- ALLOW, CONSTRAIN, REVIEW, and DENY logic via benchmark/tests
- SQLite evidence persistence
- GSTC retrieval and verification
- Docker build and Docker Compose runtime
- Containerized API decision/persistence/verification path

## Scope not yet validated

The optional AWS metadata adapter is implemented but has not been validated against a live AWS account in this evidence set.

## Interpretation

The benchmark demonstrates implementation conformance with configured synthetic policy semantics. It is not evidence of production legal compliance, production-scale end-to-end latency, or comparative superiority over mature PBAC/IFC/DFC systems.
