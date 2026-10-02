# DATA-PROOF

**DATA-PROOF** is a runnable reference implementation of the research framework:

> Multi-Dimensional Governance-State Assurance for Enterprise Data Transformation and AI Consumption.

It evaluates consequential data operations as governance-state transitions rather than inheriting source-access authorization blindly.

## What is implemented

- ALLOW / CONSTRAIN / REVIEW / DENY decision engine
- Purpose continuity
- Residency checks
- Quality and freshness checks
- Lineage/provenance checks
- Derived/composition-risk checks
- Task-scoped field minimization
- Policy-version freshness
- Repair/constraint suggestions
- Governance State Transition Certificate (GSTC)
- SHA-256 certificate integrity verification
- SQLite evidence store
- FastAPI service
- CLI
- Deterministic 16-scenario benchmark
- Component ablations
- Unit/API/integrity tests
- Docker and Docker Compose
- GitHub Actions CI
- Optional AWS metadata adapter for S3/Glue tags (no credentials stored)

## Quick start

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
dataproof-benchmark
uvicorn dataproof.api:app --host 0.0.0.0 --port 8000
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
pytest
dataproof-benchmark
uvicorn dataproof.api:app --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000/docs`.

## Evaluate a request

```bash
curl -s http://127.0.0.1:8000/v1/evaluate \
  -H "Content-Type: application/json" \
  -d @examples/ai_overcollection.json
```

## Verify a GSTC

```bash
curl -s http://127.0.0.1:8000/v1/certificates/<request_id>/verify
```

## Docker

```bash
docker compose up --build
```

## Benchmark

```bash
dataproof-benchmark --out artifacts/benchmark
```

The benchmark writes `scenario_results.csv`, `summary.json`, `ablation.json`, and `integrity.json`.

The benchmark is deterministic and demonstrates implementation coverage under configured synthetic policy semantics. It is **not** a claim of production legal-compliance accuracy.

## AWS integration

`dataproof.adapters.aws` can read governance metadata from S3 object tags and Glue table parameters when `boto3` is installed and normal AWS credentials are available.

No credentials, account IDs, or secrets are committed to this repository.

## License

Apache-2.0.


## Validated v0.1.0 evidence

The reference implementation has been reproduced on Windows and under Docker Compose.

Validated results:
- 6/6 local tests passed
- 16/16 canonical scenario families passed
- UAER = 0.0 in the configured benchmark
- 5,000/5,000 GSTC mutations detected
- 32,000 local timing executions
- local mean = 54.55 µs, p95 = 80.50 µs, p99 = 120.40 µs
- FastAPI health/evaluation/persistence/verification path passed
- Docker build and containerized AI-overcollection path passed

See [docs/VALIDATION.md](docs/VALIDATION.md) for the full validation record.

> Performance values are environment-specific and should not be generalized to production deployments.
